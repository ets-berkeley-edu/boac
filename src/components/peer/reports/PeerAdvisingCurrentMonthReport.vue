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
      <PeerAdvisorMonthlyNoteCountTable
        id-prefix="current-month-active"
        :peer-advisors="partitionedPeerAdvisors.active"
        :peer-advising-department="notesReport.peerAdvisingDepartment"
        section-label="Active Peer Advisors"
        :sort-options="activeSortOptions"
        :timeframe="notesReport.currentMonth"
        @sort-name="onSortActiveName"
        @sort-note-count="onSortActiveNoteCount"
      />
      <div
        v-if="!partitionedPeerAdvisors.active.length"
        class="font-weight-550 pa-3 text-medium-emphasis"
      >
        <span class="font-weight-bold">{{ notesReport.peerAdvisingDepartment.name }}</span>
        has had no active Peer Advisors in the current month.
      </div>
      <PeerAdvisorMonthlyNoteCountTable
        id-prefix="current-month-deleted"
        add-top-margin
        :is-deleted-section="true"
        :peer-advisors="partitionedPeerAdvisors.deleted"
        :peer-advising-department="notesReport.peerAdvisingDepartment"
        section-label="Deleted Peer Advisors"
        :sort-options="deletedSortOptions"
        :timeframe="notesReport.currentMonth"
        @sort-name="onSortDeletedName"
        @sort-note-count="onSortDeletedNoteCount"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {computed, ref} from 'vue'
import type {PeerAdvisingManagerReport} from '@/lib/types-peer-advising'
import PeerAdvisorMonthlyNoteCountTable from '@/components/peer/reports/PeerAdvisorMonthlyNoteCountTable.vue'
import PillCount from '@/components/util/PillCount.vue'
import {
  defaultPeerAdvisorNameSortOptions,
  partitionPeerAdvisors,
  togglePeerAdvisorSort
} from '@/lib/peer-advisor-sort'
import type {PeerAdvisorSortOptions} from '@/lib/peer-advisor-sort'

const props = defineProps({
  notesReport: {
    required: true,
    type: Object as PropType<PeerAdvisingManagerReport>
  }
})

const activeSortOptions = ref<PeerAdvisorSortOptions>(defaultPeerAdvisorNameSortOptions())
const deletedSortOptions = ref<PeerAdvisorSortOptions>(defaultPeerAdvisorNameSortOptions())

const partitionedPeerAdvisors = computed(() => {
  return partitionPeerAdvisors(props.notesReport.currentMonth.peerAdvisors)
})

const onSortActiveName = () => {
  activeSortOptions.value = togglePeerAdvisorSort('name', activeSortOptions.value)
}

const onSortActiveNoteCount = () => {
  activeSortOptions.value = togglePeerAdvisorSort('noteCount', activeSortOptions.value)
}

const onSortDeletedName = () => {
  deletedSortOptions.value = togglePeerAdvisorSort('name', deletedSortOptions.value)
}

const onSortDeletedNoteCount = () => {
  deletedSortOptions.value = togglePeerAdvisorSort('noteCount', deletedSortOptions.value)
}
</script>
