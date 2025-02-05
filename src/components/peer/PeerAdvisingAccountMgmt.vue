<template>
  <div class="align-center d-flex justify-space-between font-weight-bold">
    <div class="w-40">
      <PeerAdvisingAddStudent />
    </div>
    <div class="mr-3">
      <v-switch
        id="toggle-inactive-students-button"
        v-model="showInactiveStudents"
        aria-label="Show Only My Notes"
        color="primary"
        density="compact"
        hide-details
        :label="`${showInactiveStudents ? 'Hide' : 'Show'} inactive students`"
        role="switch"
      />
      <span aria-live="polite" class="sr-only">Showing {{ showInactiveStudents ? 'all students' : 'active students' }}</span>
    </div>
  </div>
  <div class="border-b-sm mt-6">
    <v-data-table
      density="compact"
      fixed-header
      :headers="headers"
      :header-props="{class: 'data-table-header-cell'}"
      hide-default-footer
      hide-no-data
      hover
      :items="peerAdvisingDepartment.members"
      :items-per-page="-1"
      mobile-breakpoint="md"
      :row-props="row => ({id: `tr-member-${row.item.uid}`})"
    >
      <template #item.notesCreatedCount="{item}">
        <div class="float-right" :class="{'font-weight-medium text-red': item.deletedAt}">
          {{ item.notesCreatedCount }}
        </div>
      </template>
      <template #item.actions="{item}">
        <v-tooltip text="Delete">
          <template #activator="{props}">
            <v-btn
              v-if="!item.deletedAt"
              v-bind="props"
              :id="`delete-topic-${item.uid}`"
              :aria-label="`Delete ${item.name}`"
              color="primary"
              density="compact"
              text="Remove"
              variant="text"
              @click="deletePeerAdvisor(item)"
            />
          </template>
        </v-tooltip>
        <v-tooltip text="Undelete">
          <template #activator="{props}">
            <v-btn
              v-if="item.deletedAt"
              v-bind="props"
              :id="`undelete-topic-${item.uid}`"
              :aria-label="`Un-delete ${item.name}`"
              color="warning"
              density="compact"
              text="Restore"
              variant="plain"
              @click="undelete(item)"
            />
          </template>
        </v-tooltip>
      </template>
    </v-data-table>
  </div>
</template>

<script setup>
import PeerAdvisingAddStudent from '@/components/peer/PeerAdvisingAddStudent.vue'
import {alertScreenReader} from '@/lib/utils'
import {ref} from 'vue'

defineProps({
  peerAdvisingDepartment: {
    required: true,
    type: Object
  }
})

const headers = [
  {align: 'start', key: 'name', title: 'Topic', width: '60%'},
  {align: 'end', key: 'notesCreatedCount', title: 'Notes Created'},
  {align: 'end', key: 'createdAt', title: 'Date Added'},
  {align: 'end', key: 'actions', title: 'Actions', sortable: false},
]
const showInactiveStudents = ref(false)

const deletePeerAdvisor = member => {
  alertScreenReader(member)
}

const undelete = member => {
  alertScreenReader(member)
}
</script>
