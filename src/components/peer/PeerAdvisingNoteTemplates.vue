<template>
  <div class="border-b-sm">
    <div class="align-center d-flex justify-space-between ma-3">
      <div class="w-50">
        <h2 class="font-size-16">Note Templates</h2>
      </div>
      <div>
        <PeerAdvisingNewNoteTemplateModal :peer-advising-dept-id="peerAdvisingDepartment.id" />
      </div>
    </div>
    <v-data-table
      density="compact"
      fixed-header
      :headers="headers"
      :header-props="{class: 'data-table-header-cell'}"
      hide-default-footer
      hide-no-data
      hover
      :items="noteTemplates"
      :items-per-page="-1"
      mobile-breakpoint="md"
      :row-props="row => ({id: `row-note-template-${row.item.uid}`})"
    >
      <!-- Override header cells for each column -->
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
          <td class="font-weight-bold"> {{ item.title }}</td>
          <td> {{ DateTime.fromISO(item.createdAt).toFormat('MMM, d, yyyy') }} </td>
          <td>
            <v-btn
              :id="`edit-note-template-${item.uid}`"
              :aria-label="`Edit ${item.name}`"
              color="primary"
              density="compact"
              text="Edit"
              variant="text"
              @click="editTemplate(item)"
            />
            |
            <v-btn
              :id="`copy-note-template-${item.uid}`"
              :aria-label="`Copy ${item.name}`"
              color="primary"
              density="compact"
              text="Copy"
              variant="text"
              @click="copyTemplate(item)"
            />
            |
            <v-btn
              :id="`delete-note-template-${item.uid}`"
              :aria-label="`Delete ${item.name}`"
              color="primary"
              density="compact"
              text="Delete"
              variant="text"
              @click="deleteTemplate(item)"
            />
          </td>
        </tr>
      </template>
    </v-data-table>
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue'
import {DateTime} from 'luxon'
import {alertScreenReader} from '@/lib/utils'
import {getNoteTemplatesForPeerAdvising} from '@/api/note-templates'
import PeerAdvisingNewNoteTemplateModal from '@/components/peer/PeerAdvisingNewNoteTemplateModal.vue'

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

onMounted(() => {
  getNoteTemplates()
})

const getNoteTemplates = () => {
  getNoteTemplatesForPeerAdvising(props.peerAdvisingDepartment.id).then(response => {
    noteTemplates.value = response
  })
}

const copyTemplate = noteTemplate => {
  alertScreenReader(noteTemplate)
}

const deleteTemplate = noteTemplate => {
  alertScreenReader(noteTemplate)
}

const editTemplate = noteTemplate => {
  alertScreenReader(noteTemplate)
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
