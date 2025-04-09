<template>
  <div>
    <div class="align-center d-flex justify-space-between">
      <div class="font-weight-bold">
        Current Peer Note Count for {{ notesReport.currentMonth.label }}
      </div>
      <div class="text-right">
        <PillCount
          id="current-month-peer-note-count"
          class="pa-2 sidebar-pill text-white"
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
            <th class="bg-grey-lighten-2 border-sm w-90">Peer Advisor</th>
            <th class="bg-grey-lighten-2 border-sm text-right">Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="peerAdvisor in notesReport.currentMonth.peerAdvisors"
            :id="`tr-current-month-peer-advisor-${peerAdvisor.uid}`"
            :key="peerAdvisor.id"
          >
            <td
              :id="`td-current-month-peer-advisor-${peerAdvisor.uid}-name`"
              :class="{
                'demo-mode-blur': currentUser.inDemoMode,
                'font-weight-medium text-red': peerAdvisor.deletedAt
              }"
              class="border-sm w-90"
            >
              {{ peerAdvisor.name }}
              <span v-if="peerAdvisor.deletedAt" class="text-medium-emphasis">
                (deleted on <span :id="`peer-advisor-${peerAdvisor.uid}-deleted-at`">{{ DateTime.fromISO(peerAdvisor.deletedAt).toLocaleString(DateTime.DATE_MED) }}</span>)
              </span>
            </td>
            <td
              :id="`td-current-month-peer-advisor-${peerAdvisor.uid}-note-count`"
              class="border-sm text-no-wrap text-right"
            >
              <NotesCreatedByPeerAdvisor
                v-if="get(peerAdvisor, 'noteCount')"
                :header-text="`${pluralize('note', toInt(get(peerAdvisor, 'noteCount') || 0), {1: 'One'})} created by ${peerAdvisor.name}`"
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
import {DateTime} from 'luxon'
import {get} from 'lodash'
import type {PeerAdvisingManagerReport} from '@/lib/types-peer-advising'
import NotesCreatedByPeerAdvisor from '@/components/peer/note/NotesCreatedByPeerAdvisor.vue'
import PillCount from '@/components/util/PillCount.vue'
import {pluralize, toInt} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

defineProps({
  notesReport: {
    required: true,
    type: Object as PropType<PeerAdvisingManagerReport>
  }
})

const currentUser = useContextStore().currentUser
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
</style>
