<template>
  <div class="align-end d-flex justify-space-between font-weight-bold">
    <div class="ml-4 w-40">
      <PeerAdvisingAddStudent />
    </div>
    <div v-if="peerAdvisorsActiveCount && peerAdvisorsDeletedCount" class="mr-3">
      <v-switch
        id="toggle-inactive-students-button"
        v-model="showDeletedPeerAdvisors"
        class="font-size-14 font-weight-bold text-medium-emphasis"
        color="primary"
        density="compact"
        hide-details
        :label="`${showDeletedPeerAdvisors ? 'Hide' : 'Show'} deleted`"
        role="switch"
      />
      <span aria-live="polite" class="sr-only">Showing {{ showDeletedPeerAdvisors ? 'all students' : 'active students' }}</span>
    </div>
  </div>
  <div class="border-b-sm mt-6">
    <v-data-table
      :cell-props="data => {
        return {
          class: 'font-size-16 py-2 vertical-top',
          id: `td-peer-advisor-${data.item.uid}-column-${data.column.key}`,
          style: $vuetify.display.mdAndUp ? 'max-width: 200px;' : ''
        }
      }"
      density="compact"
      fixed-header
      :headers="headers"
      :header-props="{
        class: 'data-table-header-cell'
      }"
      hide-default-footer
      hide-no-data
      hover
      :items="_filter(peerAdvisingDepartment.peerAdvisingDepartmentMembers, m => showDeletedPeerAdvisors || !m.deletedAt)"
      :items-per-page="-1"
      mobile-breakpoint="md"
      :row-props="row => ({id: `tr-member-${row.item.uid}`})"
    >
      <template #item.name="{item}">
        <div :class="{'font-weight-bold opacity-60 text-red': item.deletedAt}">
          {{ item.name }}
        </div>
      </template>
      <template #item.notesCreatedCount="{item}">
        <div class="float-right" :class="{'font-weight-medium text-red': item.deletedAt}">
          {{ item.notesCreatedCount }}
        </div>
      </template>
      <template #item.createdAt="{item}">
        <div class="float-right" :class="{'font-weight-bold opacity-60 text-red': item.deletedAt}">
          {{ DateTime.fromISO(item.createdAt).toFormat('DD') }}
        </div>
      </template>
      <template #item.actions="{item}">
        <v-btn
          v-if="!item.deletedAt"
          :id="`delete-peer-advisor-${item.uid}`"
          :aria-label="`Remove ${item.name}'s 'Peer Advisor' role`"
          class="bg-transparent text-error"
          :disabled="isBusy"
          :icon="mdiTrashCan"
          size="md"
          :title="`Remove ${item.name}'s Peer Advisor role.`"
          variant="flat"
          @click="onClickDeletePeerAdvisor(item.id)"
        />
        <v-btn
          v-if="item.deletedAt"
          :id="`restore-peer-advisor-${item.uid}`"
          :aria-label="`Restore ${item.name}'s 'Peer Advisor' role`"
          class="bg-transparent text-success"
          :disabled="isBusy"
          :icon="mdiUndo"
          size="md"
          :title="`Remove ${item.name}'s Peer Advisor role.`"
          variant="flat"
          @click="onClickRestorePeerAdvisor(item.id)"
        />
      </template>
    </v-data-table>
  </div>
</template>

<script setup>
import {DateTime} from 'luxon'
import {filter as _filter} from 'lodash'
import {mdiTrashCan, mdiUndo} from '@mdi/js'
import {computed, ref} from 'vue'
import PeerAdvisingAddStudent from '@/components/peer/PeerAdvisingAddStudent.vue'
import {deletePeerAdvisor, restorePeerAdvisor} from '@/api/peer-advising.js'

const props = defineProps({
  peerAdvisingDepartment: {
    required: true,
    type: Object
  },
  refresh: {
    required: true,
    type: Function
  }
})

const peerAdvisorsActiveCount = computed(() => {
  const members = props.peerAdvisingDepartment.peerAdvisingDepartmentMembers
  return _filter(members, m => !m.deletedAt).length
})
const peerAdvisorsDeletedCount = computed(() => {
  const members = props.peerAdvisingDepartment.peerAdvisingDepartmentMembers
  return _filter(members, 'deletedAt').length
})
const headers = [
  {align: 'start', key: 'name', title: 'Peer Advisor'},
  {align: 'end', key: 'notesCreatedCount', title: 'Notes Created'},
  {align: 'end', key: 'createdAt', title: 'Date Added'},
  {align: 'end', key: 'actions', sortable: false},
]
const isBusy = ref(false)
const showDeletedPeerAdvisors = ref(!peerAdvisorsActiveCount.value)

const onClickDeletePeerAdvisor = userId => {
  isBusy.value = true
  deletePeerAdvisor(props.peerAdvisingDepartment.id, userId).then(() => {
    props.refresh().then(() => {
      isBusy.value = false
    })
  })
}

const onClickRestorePeerAdvisor = userId => {
  isBusy.value = true
  restorePeerAdvisor(props.peerAdvisingDepartment.id, userId).then(() => {
    props.refresh().then(() => {
      isBusy.value = false
    })
  })
}
</script>
