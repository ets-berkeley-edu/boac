<template>
  <div>
    <div class="align-center d-flex justify-space-between">
      <div class="font-weight-bold">
        Current Peer Note Count for {{ notesReport.currentMonth.label }}
      </div>
      <div class="text-right">
        <PillCount
          id="current-month-peer-note-count"
          class="px-2 sidebar-pill text-white"
          color="primary"
        >
          <span class="font-size-16">{{ notesReport.currentMonth.noteCount }}</span>
        </PillCount>
      </div>
    </div>
    <div class="mt-4 w-100">
      <table v-if="notesReport.currentMonth.peerAdvisors.length" class="border-sm w-100">
        <thead>
          <tr>
            <th
              :aria-sort="getPeerAdvisorAriaSort('name', sortOptions)"
              class="bg-grey-lighten-2 border-sm w-90"
              scope="col"
            >
              <v-btn
                id="sort-current-month-peer-advisors-by-name"
                :append-icon="sortOptions.sortBy === 'name' ? (sortOptions.sortDesc ? mdiMenuDown : mdiMenuUp) : undefined"
                aria-label="Sort by Peer Advisor"
                block
                class="sort-col-btn font-weight-bold text-no-wrap v-table-sort-btn-override"
                :class="{'icon-visible': sortOptions.sortBy === 'name'}"
                color="body"
                density="compact"
                size="small"
                text="Peer Advisor"
                variant="plain"
                @click="onSortName"
              />
            </th>
            <th
              :aria-sort="getPeerAdvisorAriaSort('noteCount', sortOptions)"
              class="bg-grey-lighten-2 border-sm text-right"
              scope="col"
            >
              <v-btn
                id="sort-current-month-peer-advisors-by-note-count"
                :append-icon="sortOptions.sortBy === 'noteCount' ? (sortOptions.sortDesc ? mdiMenuDown : mdiMenuUp) : undefined"
                aria-label="Sort by Notes"
                block
                class="sort-col-btn font-weight-bold justify-end ml-auto text-no-wrap v-table-sort-btn-override"
                :class="{'icon-visible': sortOptions.sortBy === 'noteCount'}"
                color="body"
                density="compact"
                size="small"
                text="Notes"
                variant="plain"
                @click="onSortNoteCount"
              />
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="peerAdvisor in sortedPeerAdvisors"
            :id="`tr-current-month-peer-advisor-${peerAdvisor.uid}`"
            :key="peerAdvisor.uid"
          >
            <td
              :id="`td-current-month-peer-advisor-${peerAdvisor.uid}-name`"
              :class="{
                'demo-mode-blur': currentUser.inDemoMode,
                'font-weight-medium text-red': peerAdvisor.deletedAt && !currentUser.inDemoMode
              }"
              class="border-sm w-90"
            >
              {{ peerAdvisor.name }}
              <span v-if="peerAdvisor.deletedAt" class="text-medium-emphasis">
                (deleted on <Date :id="`peer-advisor-${peerAdvisor.uid}-deleted-at`" :date="peerAdvisor.deletedAt" />)
              </span>
            </td>
            <td
              :id="`td-current-month-peer-advisor-${peerAdvisor.uid}-note-count`"
              class="border-sm text-no-wrap text-right"
            >
              <NotesCreatedByPeerAdvisor
                v-if="get(peerAdvisor, 'noteCount')"
                :header-text="`${pluralize('note', toInt(get(peerAdvisor, 'noteCount') || 0), {1: 'One'})} created by ${currentUser.inDemoMode ? '...' : peerAdvisor.name}`"
                :peer-advising-department="notesReport.peerAdvisingDepartment"
                :timeframe="notesReport.currentMonth"
                :user="peerAdvisor"
              />
              <span v-if="!get(peerAdvisor, 'noteCount')" :class="{'font-weight-medium text-red': peerAdvisor.deletedAt}">
                0<span class="sr-only"> notes created in {{ notesReport.currentMonth.label }}</span>
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      <div
        v-if="!notesReport.currentMonth.peerAdvisors.length"
        class="font-weight-550 pa-3 text-medium-emphasis"
      >
        <span class="font-weight-bold">{{ notesReport.peerAdvisingDepartment.name }}</span>
        has had no active Peer Advisors in the current month.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {computed, ref} from 'vue'
import {get} from 'lodash'
import {mdiMenuDown, mdiMenuUp} from '@mdi/js'
import type {PeerAdvisingManagerReport} from '@/lib/types-peer-advising'
import Date from '@/components/util/Date.vue'
import NotesCreatedByPeerAdvisor from '@/components/peer/note/NotesCreatedByPeerAdvisor.vue'
import PillCount from '@/components/util/PillCount.vue'
import {
  defaultPeerAdvisorSortOptions,
  getPeerAdvisorAriaSort,
  sortPeerAdvisors,
  togglePeerAdvisorSort
} from '@/lib/peer-advisor-sort'
import type {PeerAdvisorSortOptions} from '@/lib/peer-advisor-sort'
import {pluralize, toInt} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  notesReport: {
    required: true,
    type: Object as PropType<PeerAdvisingManagerReport>
  }
})

const currentUser = useContextStore().currentUser
const sortOptions = ref<PeerAdvisorSortOptions>(defaultPeerAdvisorSortOptions())

const sortedPeerAdvisors = computed(() => {
  return sortPeerAdvisors(props.notesReport.currentMonth.peerAdvisors, sortOptions.value)
})

const onSortName = () => {
  sortOptions.value = togglePeerAdvisorSort('name', sortOptions.value)
}

const onSortNoteCount = () => {
  sortOptions.value = togglePeerAdvisorSort('noteCount', sortOptions.value)
}
</script>

<style scoped>
table {
  border: 1px solid;
  border-collapse: collapse;
}
th {
  border: 1px solid;
  font-size: 14px;
  padding: 6px 12px;
}
td {
  border: 1px solid;
  padding: 6px 12px;
}
.sort-col-btn {
  height: 28px !important;
  letter-spacing: normal !important;
  margin: 0 4px 0 -.1em;
  min-width: 0px !important;
  padding: 0 2px 0 4px;
}
</style>

<style>
.v-table-sort-btn-override .v-btn__append {
  margin-inline: 2px 1px !important;
}
.v-table-sort-btn-override .v-btn__append .v-icon {
  opacity: 0;
}
.v-table-sort-btn-override .v-btn__content {
  text-align: left;
}
.v-table-sort-btn-override:active .v-btn__append .v-icon,
.v-table-sort-btn-override:hover .v-btn__append .v-icon,
.v-table-sort-btn-override:focus .v-btn__append .v-icon {
  opacity: var(--v-medium-emphasis-opacity);
}
.v-table-sort-btn-override.icon-visible .v-btn__append .v-icon {
  opacity: 1;
}
</style>
