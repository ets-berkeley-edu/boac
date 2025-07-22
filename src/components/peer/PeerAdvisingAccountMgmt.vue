<template>
  <div>
    <div class="align-end d-flex flex-wrap default-margins justify-space-between font-weight-bold">
      <div class="add-student-container pr-4">
        <PeerAdvisingAddStudent
          :exclude-these-students="peerAdvisors"
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
            class: 'font-size-16 py-2 vertical-top',
            id: `td-peer-advisor-${data.item.uid}-column-${data.column.key}`,
            style: mdAndUp ? 'max-width: 200px;' : ''
          }
        }"
        density="compact"
        fixed-header
        :headers="headers"
        :header-props="{
          class: 'data-table-header-cell'
        }"
        hide-default-footer
        :hide-default-header="!mdAndUp && dataTableRows.length <= 1"
        hide-no-data
        hover
        :items="dataTableRows"
        :items-per-page="-1"
        mobile-breakpoint="md"
        must-sort
        :row-props="row => ({id: `tr-member-${row.item.uid}`})"
        :sort-by="[sortBy]"
        @update:sort-by="onUpdateSortBy"
      >
        <template #headers="{columns, isSorted, toggleSort, getSortIcon}">
          <tr>
            <th
              v-for="column in columns"
              :key="(column.key as string)"
              :aria-label="column.sortable ? (column.ariaLabel || column.title) : undefined"
              :aria-sort="column.sortable ? `${sortBy.order}ending` : undefined"
              class="px-2"
              :class="{'text-left': column.align === 'start', 'text-right': column.align === 'end'}"
              :style="column.headerProps"
            >
              <template v-if="column.sortable">
                <v-btn
                  :id="`students-sort-by-${column.key}-btn`"
                  :append-icon="getSortIcon(column)"
                  :aria-label="`Sort by ${column.ariaLabel || column.title} ${isSorted(column) && sortBy.order === 'asc' ? 'descending' : 'ascending'}`"
                  class="align-start font-size-12 font-weight-bold height-unset min-width-unset pa-1 text-uppercase v-table-sort-btn-override"
                  :class="{'icon-visible': isSorted(column)}"
                  color="body"
                  density="compact"
                  variant="plain"
                  @click="() => toggleSort(column)"
                >
                  <span class="text-left text-wrap">{{ column.title }}</span>
                </v-btn>
              </template>
              <template v-else>
                <span :class="get(column, 'headerProps.class', '')">{{ column.title }}</span>
              </template>
            </th>
          </tr>
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
    <div v-if="!peerAdvisors.length" class="font-size-16 pl-6 mt-2 text-medium-emphasis">
      Peer Advisors have yet to be created for <span class="font-weight-550">{{ peerAdvisingDepartment.name }}</span>.
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {DateTime} from 'luxon'
import {computed, ref} from 'vue'
import {filter as _filter, find, get} from 'lodash'
import {useDisplay} from 'vuetify'
import type {BoaUser, PeerAdvisingDepartment} from '@/lib/types'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import NotesCreatedByPeerAdvisor from '@/components/peer/note/NotesCreatedByPeerAdvisor.vue'
import PeerAdvisingAddStudent from '@/components/peer/PeerAdvisingAddStudent.vue'
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
  {align: 'start' as 'start' | 'end' | 'center', key: 'name', sortable: dataTableRows.value.length > 1, title: 'Peer Advisor'},
  {align: 'end' as 'start' | 'end' | 'center', key: 'notesCreatedCount', sortable: dataTableRows.value.length > 1, sortRaw: sortByNoteCount, title: 'Notes Created'},
  {align: 'end' as 'start' | 'end' | 'center', key: 'createdAt', sortable: dataTableRows.value.length > 1, title: 'Date Added'},
  {align: 'end' as 'start' | 'end' | 'center', ariaLabel: 'actions', key: 'actions', sortable: false}
])
const isBusy = ref(false)
const isDeleteModalOpen = ref(false)
const isDeleting = ref(false)
const selectedPeerAdvisor = ref<BoaUser | undefined>()
const showDeletedPeerAdvisors = ref<boolean>()
const sortBy = ref<{key: string, order: 'asc' | 'desc'}>({key: 'createdAt', order: 'desc'})
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
    deletePeerAdvisor(props.peerAdvisingDepartment.id, selectedPeerAdvisor.value.id).then(() => {
      props.refresh().then(() => {
        isBusy.value = isDeleting.value = isDeleteModalOpen.value = false
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

const onClickRestorePeerAdvisor = (userId: number) => {
  isBusy.value = true
  restorePeerAdvisor(props.peerAdvisingDepartment.id, userId).then(() => {
    props.refresh().then(() => {
      isBusy.value = false
    })
  })
}

const onUpdateSortBy = (primarySortBy: {key: string, order: 'asc' | 'desc'}[]) => {
  const key = primarySortBy[0].key
  const header = find(headers.value, {key: key})
  sortBy.value = primarySortBy[0]
  if (header) {
    alertScreenReader(`Sorted by ${header.ariaLabel || header.title}, ${sortBy.value.order}ending`)
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
  min-width: 550px;
  width: 75%;
}
</style>
