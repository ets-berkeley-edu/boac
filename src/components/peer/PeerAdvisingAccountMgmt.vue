<template>
  <div class="align-end d-flex default-margins justify-space-between font-weight-bold">
    <div class="add-student-container">
      <PeerAdvisingAddStudent
        :exclude-these-students="peerAdvisors"
        :peer-advising-department-id="peerAdvisingDepartmentId"
        :refresh="refresh"
      />
    </div>
    <div>
      <v-switch
        id="toggle-inactive-students-button"
        v-model="showDeletedPeerAdvisors"
        :class="{'text-primary': showDeletedPeerAdvisors}"
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
  <div class="border-b-sm ml-4 mt-6">
    <v-data-table
      :cell-props="data => {
        return {
          class: 'font-size-16 py-2 vertical-top',
          id: `td-peer-advisor-${data.item.uid}-column-${data.column.key}`,
          style: mdAndUp ? 'max-width: 200px;' : ''
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
        <div class="float-right">
          <NotesCreatedByPeerAdvisor
            v-if="get(item, 'noteCount')"
            :header-text="`${pluralize('note', toInt(get(item, 'noteCount') || 0))} created by ${item.name}`"
            :user="item"
          />
          <span v-if="!get(item, 'noteCount')" :class="{'font-weight-medium text-red': item.deletedAt}">0</span>
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
          @click="() => onClickDelete(item)"
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
    <AreYouSureModal
      v-model="isDeleteModalOpen"
      :button-label-confirm="isDeleting ? 'Deleting' : 'Delete'"
      :function-cancel="cancel"
      :function-confirm="onConfirmDelete"
      :modal-header="`Remove ${get(selectedPeerAdvisor, 'name')}'s Peer Advisor role?`"
      modal-header-class="font-size-18 font-weight-medium"
    />
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {DateTime} from 'luxon'
import {computed, ref} from 'vue'
import {filter as _filter, get} from 'lodash'
import {useDisplay} from 'vuetify'
import type {BoaUser} from '@/lib/types'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import NotesCreatedByPeerAdvisor from '@/components/peer/note/NotesCreatedByPeerAdvisor.vue'
import PeerAdvisingAddStudent from '@/components/peer/PeerAdvisingAddStudent.vue'
import {alertScreenReader, pluralize, putFocusNextTick, toInt} from '@/lib/utils'
import {deletePeerAdvisor, restorePeerAdvisor} from '@/api/peer-advising-users.js'

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
    type: Array as PropType<BoaUser[]>
  },
  refresh: {
    required: true,
    type: Function
  }
})
const dataTableRows = computed<BoaUser[]>(() => _filter(props.peerAdvisors, u => showDeletedPeerAdvisors.value || !u.deletedAt))
const isBusy = ref(false)
const isDeleteModalOpen = ref(false)
const isDeleting = ref(false)
const peerAdvisorsActiveCount = computed<number>(() => _filter(props.peerAdvisors, m => !m.deletedAt).length)
const selectedPeerAdvisor = ref<BoaUser | undefined>()
const showDeletedPeerAdvisors = ref(!peerAdvisorsActiveCount.value)
const {mdAndUp} = useDisplay()

const cancel = () => {
  isDeleteModalOpen.value = false
  const uid = get(selectedPeerAdvisor.value, 'uid')
  selectedPeerAdvisor.value = undefined
  alertScreenReader('Canceled')
  putFocusNextTick(`delete-peer-advisor-${uid}`)
}

const onConfirmDelete = () => {
  isBusy.value = isDeleting.value = true
  if (selectedPeerAdvisor.value) {
    deletePeerAdvisor(props.peerAdvisingDepartmentId, selectedPeerAdvisor.value.id).then(() => {
      props.refresh().then(() => {
        isBusy.value = isDeleting.value = isDeleteModalOpen.value = false
      })
    })
  } else {
    throw Error('Where is the Peer Advisor we want to delete?')
  }
}

const onClickRestorePeerAdvisor = (userId: number) => {
  isBusy.value = true
  restorePeerAdvisor(props.peerAdvisingDepartmentId, userId).then(() => {
    props.refresh().then(() => {
      isBusy.value = false
    })
  })
}

const onClickDelete = (peerAdvisor: BoaUser) => {
  selectedPeerAdvisor.value = peerAdvisor
  isDeleteModalOpen.value = true
}
</script>

<style scoped>
.add-student-container {
  width: 550px;
}
</style>
