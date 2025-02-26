<template>
  <div class="align-end d-flex justify-space-between font-weight-bold">
    <div class="ml-4 w-40">
      <PeerAdvisingAddStudent
        :exclude-these-students="peerAdvisors"
        :peer-advising-department-id="peerAdvisingDepartmentId"
        :refresh="refresh"
      />
    </div>
    <div v-if="peerAdvisorsActiveCount && peerAdvisorsDeletedCount" class="mr-3">
      <v-switch
        id="toggle-inactive-students-button"
        v-model="showDeletedPeerAdvisors"
        class="font-size-14 font-weight-bold text-medium-emphasis"
        color="primary"
        density="compact"
        :disabled="isBusy || isRefreshing"
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
      :headers="[
        {align: 'start', key: 'name', sortable: dataTableRows.length > 1, title: 'Peer Advisor'},
        {align: 'end', key: 'notesCreatedCount', sortable: dataTableRows.length > 1, title: 'Notes Created'},
        {align: 'end', key: 'createdAt', sortable: dataTableRows.length > 1, title: 'Date Added'},
        {align: 'end', key: 'actions', sortable: false}
      ]"
      :header-props="{
        class: 'data-table-header-cell'
      }"
      hide-default-footer
      hide-no-data
      hover
      :items="dataTableRows"
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
          :class="{'bg-transparent text-primary': !isBusy}"
          class="mb-1"
          :disabled="isBusy || isRefreshing"
          size="md"
          text="Delete"
          :title="`Remove ${item.name}'s Peer Advisor role.`"
          variant="flat"
          @click="() => onClickDeletePeerAdvisor(item.id)"
        />
        <v-btn
          v-if="item.deletedAt"
          :id="`restore-peer-advisor-${item.uid}`"
          :aria-label="`Restore ${item.name}'s 'Peer Advisor' role`"
          :class="{'bg-transparent text-primary': !isBusy}"
          class="mb-1"
          :disabled="isBusy || isRefreshing"
          size="md"
          text="Restore"
          :title="`Restore ${item.name}'s Peer Advisor role.`"
          variant="flat"
          @click="() => onClickRestorePeerAdvisor(item.id)"
        />
      </template>
    </v-data-table>
  </div>
</template>

<script setup>
import {computed, ref} from 'vue'
import {DateTime} from 'luxon'
import {filter as _filter} from 'lodash'
import PeerAdvisingAddStudent from '@/components/peer/PeerAdvisingAddStudent.vue'
import {deletePeerAdvisor, restorePeerAdvisor} from '@/api/peer-advising.js'

const props = defineProps({
  isRefreshing: {
    required: true,
    type: Boolean
  },
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  },
  peerAdvisors: {
    required: true,
    type: Array
  },
  refresh: {
    required: true,
    type: Function
  }
})

const dataTableRows = computed(() => _filter(props.peerAdvisors, u => showDeletedPeerAdvisors.value || !u.deletedAt))
const peerAdvisorsActiveCount = computed(() => _filter(props.peerAdvisors, m => !m.deletedAt).length)
const peerAdvisorsDeletedCount = computed(() => _filter(props.peerAdvisors, m => m.deletedAt).length)
const isBusy = ref(false)
const showDeletedPeerAdvisors = ref(!peerAdvisorsActiveCount.value)

const onClickDeletePeerAdvisor = userId => {
  isBusy.value = true
  deletePeerAdvisor(props.peerAdvisingDepartmentId, userId).then(() => {
    props.refresh().then(() => {
      isBusy.value = false
    })
  })
}

const onClickRestorePeerAdvisor = userId => {
  isBusy.value = true
  restorePeerAdvisor(props.peerAdvisingDepartmentId, userId).then(() => {
    props.refresh().then(() => {
      isBusy.value = false
    })
  })
}
</script>
