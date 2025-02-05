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
          text="Add Unit Requirement"
          variant="text"
          :append-icon="mdiPlus"
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
      <template #item.createdAt="{item}">
        <div class="float-right" :class="{'font-weight-medium text-red': item.deletedAt}">
          {{ item.createdAt }}
        </div>
      </template>
      <template #item.actions="{item}">
        <v-tooltip text="Delete">
          <template #activator="{props}">
            <v-btn
              v-bind="props"
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
              v-bind="props"
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
              v-bind="props"
              :id="`delete-note-template-${item.uid}`"
              :aria-label="`Delete ${item.name}`"
              color="primary"
              density="compact"
              text="Delete"
              variant="text"
              @click="deleteTemplate(item)"
            />
          </template>
        </v-tooltip>
      </template>
    </v-data-table>
  </div>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {onMounted, ref} from 'vue'
import {mdiPlus} from '@mdi/js'

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
})

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
