<template>
  <div class="border-b-sm">
    <div class="align-center d-flex justify-space-between ma-3">
      <div class="w-50">
        <h2 class="font-size-16">Note Templates</h2>
      </div>
      <div>
        <v-btn
          id="unit-requirement-create-link"
          class="float-end"
          color="primary"
          slim
          text="Create new Note Template"
          variant="text"
          :prepend-icon="mdiPlus"
          @click.prevent="onClickAdd"
        />
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
      <template #item="{ item, index }">
        <tr :class="index % 2 === 0 ? 'white-row' : 'grey-row'">
          <td> {{ item.name }}</td>
          <td> {{ item.createdAt }} </td>
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
import {mdiPlus} from '@mdi/js'
import {alertScreenReader} from '@/lib/utils'
import {getNoteTemplatesForPeerAdvising} from '@/api/note-templates'

const props = defineProps({
  peerAdvisingDepartment: {
    required: true,
    type: Object
  }
})

const headers = [
  {align: 'start', key: 'name', title: 'Template Name', width: '60%'},
  {align: 'end', key: 'createdAt', title: 'Created'},
  {align: 'end', key: 'actions', title: 'Actions', sortable: false},
]
const noteTemplates = ref([])

onMounted(() => {
  noteTemplates.value = [
    {
      name: 'Change of Major',
      createdAt: 'Apr 2, 2024'
    },
    {
      name: 'Declaring a Major',
      createdAt: 'Apr 2, 2024'
    },
    {
      name: 'Units Exception',
      createdAt: 'Mar 24, 2024'
    },
    {
      name: 'Graduation Planning',
      createdAt: 'Mar 3, 2024'
    },
  ]
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

const onClickAdd = () => {
  alertScreenReader('onClickAdd')
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
</style>
