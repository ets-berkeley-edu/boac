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
          <span class="font-size-16">{{ notesReport.currentMonth.peerAdvisingNoteCount }}</span>
        </PillCount>
      </div>
    </div>
    <div class="mt-4 w-100">
      <table class="border-sm w-100">
        <thead>
          <tr>
            <th class="bg-grey-lighten-2 border-sm w-90">Peer Advisor</th>
            <th class="bg-grey-lighten-2 border-sm text-right">Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="peerAdvisor in notesReport.currentMonth.peerAdvisors" :key="peerAdvisor.id">
            <td class="border-sm w-90">{{ peerAdvisor.name }}</td>
            <td class="border-sm text-no-wrap text-right">
              <NotesCreatedByPeerAdvisor
                v-if="get(peerAdvisor, 'noteCount')"
                :header-text="`${pluralize('note', toInt(get(peerAdvisor, 'noteCount') || 0))} created by ${peerAdvisor.name}`"
                :user="peerAdvisor"
              />
              <span v-if="!get(peerAdvisor, 'noteCount')" :class="{'font-weight-medium text-red': peerAdvisor.deletedAt}">0</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {get} from 'lodash'
import type {PeerAdvisingManagerReport} from '@/lib/types'
import NotesCreatedByPeerAdvisor from '@/components/peer/note/NotesCreatedByPeerAdvisor.vue'
import PillCount from '@/components/util/PillCount.vue'
import {pluralize, toInt} from '@/lib/utils'

defineProps({
  notesReport: {
    required: true,
    type: Object as PropType<PeerAdvisingManagerReport>
  }
})
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
