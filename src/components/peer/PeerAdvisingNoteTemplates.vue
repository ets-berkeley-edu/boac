<template>
  <div class="border-b-sm">
    <div class="align-center d-flex justify-space-between ma-3">
      <div class="w-50">
        <h2 class="font-size-16">Note Templates</h2>
      </div>
      <div>
        <v-btn
          id="create-new-peer-advising-note-template"
          class="float-end"
          color="primary"
          slim
          text="Create new Note Template"
          :disabled="currentUser.isAdmin"
          variant="text"
          :prepend-icon="mdiPlus"
          @click="openNewTemplateModal"
        />
        <PeerAdvisingNoteTemplateModal
          v-model="noteTemplateModalOpen"
          :peer-advising-dept-id="peerAdvisingDepartment.id"
          :selected-note-template="selectedNoteTemplate"
          :action="action"
          :note-templates="noteTemplates"
          @note-template-updated="getNoteTemplates"
        />
      </div>
    </div>
    <v-data-table
      density="compact"
      fixed-header
      :headers="headers"
      :header-props="{class: 'data-table-header-cell'}"
      hide-default-footer
      hover
      :items="noteTemplates"
      :items-per-page="-1"
      mobile-breakpoint="md"
      :row-props="row => ({id: `row-note-template-${row.item.uid}`})"
    >
      <!-- Override header cells for each column -->
      <template #no-data>
        <div class="pa-4">
          Click on <span class="font-italic">Create new Note Template</span> to add your first note template.
        </div>
      </template>
      <template #header.name>
        <th class="w-50">Template Name</th>
      </template>
      <template #header.createdAt>
        <th class="w-20">Created</th>
      </template>
      <template #header.actions>
        <th class="w-30">Actions</th>
      </template>
      <template #item="{ item, index }">
        <tr :class="index % 2 === 0 ? 'white-row' : 'grey-row'">
          <td class="font-weight-bold cursor-pointer" @click="openNoteTemplateClicked(item)"> {{ item.title }}</td>
          <td class="cursor-pointer" @click="openNoteTemplateClicked(item)"> {{ DateTime.fromISO(item.createdAt).toFormat('MMM d, yyyy') }} </td>
          <td>
            <v-btn
              :id="`edit-note-template-${item.id}`"
              :aria-label="`Edit ${item.name}`"
              color="primary"
              density="compact"
              :disabled="currentUser.isAdmin"
              text="Edit"
              variant="text"
              @click="editTemplateClicked(item)"
            />
            |
            <v-btn
              :id="`copy-note-template-${item.id}`"
              :aria-label="`Copy ${item.name}`"
              color="primary"
              density="compact"
              :disabled="currentUser.isAdmin"
              text="Copy"
              variant="text"
              @click="copyTemplateClicked(item)"
            />
            |
            <v-btn
              :id="`delete-note-template-${item.id}`"
              :aria-label="`Delete ${item.name}`"
              color="primary"
              density="compact"
              :disabled="currentUser.isAdmin"
              text="Delete"
              variant="text"
              @click="deleteTemplateClicked(item)"
            />
          </td>
        </tr>
      </template>
    </v-data-table>
    <AreYouSureModal
      id="confirm-delete-note-template-modal"
      v-model="showDeleteModal"
      button-label-confirm="Delete"
      :function-cancel="cancelDeleteNoteTemplate"
      :function-confirm="deleteTemplateApi"
      modal-header="Delete Note Template"
    >
      Are you sure you want to delete "<strong>{{ selectedNoteTemplate.title }}</strong>"?
    </AreYouSureModal>
  </div>
</template>

<script setup>
import {mdiPlus} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {DateTime} from 'luxon'
import {alertScreenReader} from '@/lib/utils'
import {getNoteTemplatesForPeerAdvising} from '@/api/note-templates'
import PeerAdvisingNoteTemplateModal from '@/components/peer/PeerAdvisingNoteTemplateModal.vue'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import {deletePeerAdvisingNoteTemplate} from '@/api/peer-advising.js'
import {useContextStore} from '@/stores/context.js'

const props = defineProps({
  peerAdvisingDepartment: {
    required: true,
    type: Object
  }
})

const headers = [
  {align: 'start', key: 'name', title: 'Template Name', width: '50%'},
  {align: 'end', key: 'createdAt', title: 'Created', width: '20%'},
  {align: 'end', key: 'actions', title: 'Actions', sortable: false, width: '30%'},
]
const noteTemplates = ref([])
const showDeleteModal = ref(false)
const selectedNoteTemplate = ref(null)
const noteTemplateModalOpen = ref(false)
const action = ref('create')
const currentUser = ref(useContextStore().currentUser)

onMounted(() => {
  getNoteTemplates()
})

const getNoteTemplates = () => {
  getNoteTemplatesForPeerAdvising(props.peerAdvisingDepartment.id).then(response => {
    noteTemplates.value = response
  })
}

const openNewTemplateModal = () => {
  selectedNoteTemplate.value = null
  action.value = 'create'
  noteTemplateModalOpen.value = true
}

const copyTemplateClicked = noteTemplate => {
  selectedNoteTemplate.value = noteTemplate
  action.value = 'copy'
  noteTemplateModalOpen.value = true
}


const cancelDeleteNoteTemplate = () => {
  showDeleteModal.value = false
}

const deleteTemplateClicked = (noteTemplate) => {
  showDeleteModal.value = true
  selectedNoteTemplate.value = noteTemplate
}
const deleteTemplateApi = () => {
  deletePeerAdvisingNoteTemplate(selectedNoteTemplate.value.id).then(() => {
    getNoteTemplatesForPeerAdvising(props.peerAdvisingDepartment.id).then(response => {
      noteTemplates.value = response
      showDeleteModal.value = false
      alertScreenReader(`Note Template ${response.title} has been deleted.`)
    })
  })
}

const editTemplateClicked = noteTemplate => {
  selectedNoteTemplate.value = noteTemplate
  action.value = 'edit'
  noteTemplateModalOpen.value = true
  alertScreenReader(`Opened ${noteTemplate.title} note template to edit.`)
}

const openNoteTemplateClicked = (noteTemplate) => {
  if (currentUser.value.isAdmin) {
    selectedNoteTemplate.value = noteTemplate
    action.value = 'view'
    noteTemplateModalOpen.value = true
    alertScreenReader(`Opened ${noteTemplate.title} note template.`)
  } else {
    editTemplateClicked(noteTemplate)
  }

}
</script>

<style>

.data-table-header-cell {
  height: 24px !important;
}
.white-row {
  background-color: white;
}
.grey-row {
  background-color: #f6f6f6;
}

/* Force a fixed layout so widths are respected */
.v-data-table .v-data-table__wrapper table {
  table-layout: fixed;
}

/* Target header cells within your custom header class */
.data-table-header-cell th:nth-child(1) {
  width: 50% !important;
}
.data-table-header-cell th:nth-child(2) {
  width: 20% !important;
}
.data-table-header-cell th:nth-child(3) {
  width: 30% !important;
}
</style>
