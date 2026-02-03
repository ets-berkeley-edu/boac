<template>
  <div>
    <div class="align-end d-flex flex-wrap default-margins justify-space-between font-weight-bold">
      <div class="add-student-container w-100 w-md-75 pr-4">
        <PeerAdvisingAddStudent
          :active-and-deleted-peer-advisors="peerAdvisors"
          :peer-advising-department-id="peerAdvisingDepartment.id"
          :refresh="refresh"
        />
      </div>
      <v-switch
        v-if="peerAdvisors.length"
        id="toggle-inactive-students-button"
        v-model="showDeletedPeerAdvisors"
        :class="{'text-primary': showDeletedPeerAdvisors}"
        class="font-size-14 font-weight-bold text-medium-emphasis ml-1 mb-1"
        color="primary"
        density="compact"
        :disabled="isBusy || isRefreshing"
        hide-details
        :label="`${showDeletedPeerAdvisors ? 'Hide' : 'Show'} deleted`"
        role="switch"
      />
      <span aria-live="polite" class="sr-only">Showing {{ showDeletedPeerAdvisors ? 'all students' : 'active students' }}</span>
    </div>
    <div v-if="peerAdvisors.length" class="border-b-sm ml-4 mt-6">
      <v-data-table
        :cell-props="data => {
          return {
            class: 'font-size-16 pl-1 py-2 vertical-top',
            'data-label': data.column.title,
            id: `td-peer-advisor-${data.item.uid}-column-${data.column.key}`
          }
        }"
        :class="{'stacked-table': $vuetify.display.width <= mobileBreakpoint}"
        density="compact"
        fixed-header
        :headers="headers"
        :header-props="{
          class: 'data-table-header-cell'
        }"
        hide-default-footer
        hide-no-data
        hover
        :items="dataTableRows"
        :items-per-page="-1"
        must-sort
        :row-props="row => ({id: `tr-member-${row.item.uid}`})"
        :sort-by="[sortBy]"
        @update:sort-by="onUpdateSortBy"
      >
        <template #headers="{columns, isSorted, toggleSort, getSortIcon, sortBy: sortedBy}">
          <SortableTableHeader
            v-if="columns.length && (size(dataTableRows) || $vuetify.display.width > mobileBreakpoint)"
            :columns="columns"
            :disable-sort="size(dataTableRows) <= 1"
            id-prefix="students"
            :is-compact="$vuetify.display.width <= mobileBreakpoint"
            :is-sorted="isSorted"
            :set-order="onUpdateSortBy"
            :sorted-by="sortedBy[0]"
            :sort-icon="getSortIcon"
            :toggle-sort="toggleSort"
          />
        </template>
        <template #item.name="{item}">
          <div :class="{'font-weight-bold opacity-60 text-red': item.deletedAt && !currentUser.inDemoMode, 'demo-mode-blur': currentUser.inDemoMode}">
            {{ item.name || `UID: ${item.uid}` }}
          </div>
        </template>
        <template #item.notesCreatedCount="{item}">
          <div class="float-right">
            <NotesCreatedByPeerAdvisor
              v-if="get(item, 'noteCount')"
              :header-text="`${pluralize('note', toInt(get(item, 'noteCount') || 0), {1: 'One'})} created by ${currentUser.inDemoMode ? '...' : item.name}`"
              :peer-advising-department="peerAdvisingDepartment"
              :user="item"
            />
            <span
              v-if="!get(item, 'noteCount')"
              class="pa-1 border-sm border-opacity-0"
              :class="{'font-weight-medium text-red': item.deletedAt}"
            >
              0
            </span>
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
            class="peer-advisor-btn d-flex py-1 px-2 mb-1"
            :disabled="isBusy || isRefreshing"
            size="md"
            text="Delete"
            variant="flat"
            @click="() => onClickDelete(item)"
          />
          <v-btn
            v-if="item.deletedAt"
            :id="`restore-peer-advisor-${item.uid}`"
            :aria-label="`Restore ${item.name}'s 'Peer Advisor' role`"
            :class="{'bg-transparent text-primary': !isBusy}"
            class="peer-advisor-btn d-flex pa-1 mb-1"
            :disabled="isBusy || isRefreshing"
            size="md"
            text="Restore"
            variant="flat"
            @click="() => onClickRestorePeerAdvisor(item)"
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
    <div v-if="!peerAdvisors.length" class="font-size-16 pl-6 mt-2 text-medium-emphasis">
      Peer Advisors have yet to be created for <span class="font-weight-550">{{ peerAdvisingDepartment.name }}</span>.
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {DateTime} from 'luxon'
import {computed, ref} from 'vue'
import {filter as _filter, find, get, size} from 'lodash'
import type {BoaUser, PeerAdvisingDepartment} from '@/lib/types'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import NotesCreatedByPeerAdvisor from '@/components/peer/note/NotesCreatedByPeerAdvisor.vue'
import PeerAdvisingAddStudent from '@/components/peer/PeerAdvisingAddStudent.vue'
import SortableTableHeader from '@/components/util/SortableTableHeader.vue'
import {alertScreenReader, pluralize, putFocusNextTick, toInt} from '@/lib/utils'
import {deletePeerAdvisor, restorePeerAdvisor} from '@/api/peer-advising-users.js'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  isRefreshing: {
    required: true,
    type: Boolean
  },
  peerAdvisingDepartment: {
    required: true,
    type: Object as PropType<PeerAdvisingDepartment>
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

const currentUser = useContextStore().currentUser
const dataTableRows = computed<BoaUser[]>(() => _filter(props.peerAdvisors, u => showDeletedPeerAdvisors.value || !u.deletedAt))
const headers = computed(() => [
  {align: 'start' as 'start' | 'end' | 'center', key: 'name', sortable: true, title: 'Peer Advisor'},
  {align: 'end' as 'start' | 'end' | 'center', key: 'notesCreatedCount', sortable: true, sortRaw: sortByNoteCount, title: 'Notes Created'},
  {align: 'end' as 'start' | 'end' | 'center', key: 'createdAt', sortable: true, title: 'Date Added'},
  {align: 'center' as 'start' | 'end' | 'center', key: 'actions', sortable: false}
])
const isBusy = ref(false)
const isDeleteModalOpen = ref(false)
const isDeleting = ref(false)
const mobileBreakpoint = 600
const selectedPeerAdvisor = ref<BoaUser | undefined>()
const showDeletedPeerAdvisors = ref<boolean>()
const sortBy = ref<{key: string, order: 'asc' | 'desc'}>({key: 'createdAt', order: 'desc'})

const cancel = () => {
  isDeleteModalOpen.value = false
  const uid = get(selectedPeerAdvisor.value, 'uid')
  selectedPeerAdvisor.value = undefined
  alertScreenReader('Canceled')
  putFocusNextTick(`delete-peer-advisor-${uid}`)
}

const onConfirmDelete = () => {
  if (selectedPeerAdvisor.value) {
    const peerAdvisor = selectedPeerAdvisor.value
    const indexOf = props.peerAdvisors.findIndex(u => u.id === peerAdvisor.id)
    isBusy.value = isDeleting.value = true
    alertScreenReader(`Removing ${peerAdvisor.name}'s 'Peer Advisor' role`)
    deletePeerAdvisor(props.peerAdvisingDepartment.id, peerAdvisor.id).then(() => {
      props.refresh().then(() => {
        isBusy.value = isDeleting.value = isDeleteModalOpen.value = false
        alertScreenReader(`${peerAdvisor.name}'s 'Peer Advisor' role has been removed.`)
        if (showDeletedPeerAdvisors.value) {
          putFocusNextTick(`restore-peer-advisor-${peerAdvisor.uid}`)
        } else {
          const peerAdvisorsCount = size(dataTableRows.value)
          if (!peerAdvisorsCount) {
            putFocusNextTick('toggle-inactive-students-button')
          } else {
            const nextPeerAdvisor = indexOf < peerAdvisorsCount ? props.peerAdvisors[indexOf] : props.peerAdvisors[indexOf - 1]
            putFocusNextTick(`${nextPeerAdvisor.deletedAt ? 'restore' : 'delete'}-peer-advisor-${peerAdvisor.uid}`)
          }
        }
      })
    })
  } else {
    throw Error('Where is the Peer Advisor we want to delete?')
  }
}

const onClickDelete = (peerAdvisor: BoaUser) => {
  selectedPeerAdvisor.value = peerAdvisor
  isDeleteModalOpen.value = true
}

const onClickRestorePeerAdvisor = (peerAdvisor: BoaUser) => {
  isBusy.value = true
  alertScreenReader(`Restoring ${peerAdvisor.name}'s 'Peer Advisor' role`)
  restorePeerAdvisor(props.peerAdvisingDepartment.id, peerAdvisor.id).then(() => {
    props.refresh().then(() => {
      isBusy.value = false
      alertScreenReader(`${peerAdvisor.name}'s 'Peer Advisor' role is restored.`)
      putFocusNextTick(`delete-peer-advisor-${peerAdvisor.uid}`)
    })
  })
}

const onUpdateSortBy = (primarySortBy: {key: string, order: 'asc' | 'desc'}[]) => {
  const key = primarySortBy[0].key
  const header = find(headers.value, {key: key})
  sortBy.value = primarySortBy[0]
  if (header) {
    alertScreenReader(`Sorted by ${header.title}, ${sortBy.value.order}ending`)
  }
}

const sortByNoteCount = (c1: {noteCount: number}, c2: {noteCount: number}) => {
  if (c1.noteCount < c2.noteCount) {
    return -1
  } else if (c1.noteCount > c2.noteCount) {
    return 1
  }
  return 0
}
</script>

<style scoped>
.add-student-container {
  max-width: 50rem;
}
</style>

<style>
.peer-advisor-btn {
  margin-top: -2px;
}
</style>
