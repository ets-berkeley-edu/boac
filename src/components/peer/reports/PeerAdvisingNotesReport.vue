<template>
  <table v-if="notesReport" class="w-100">
    <thead class="sr-only">
      <tr>
        <th>Measurement</th>
        <th>Value</th>
      </tr>
    </thead>
    <tbody>
      <tr v-if="notesReport.peerAdvisingDepartment">
        <td>Total {{ notesReport.peerAdvisingDepartment.name }} peer advising notes</td>
        <td class="font-weight-bold text-right">{{ notesReport.totalPeerAdvisingNoteCount }}</td>
      </tr>
      <tr v-if="!notesReport.peerAdvisingDepartment">
        <td>Total peer advisor notes</td>
        <td class="font-weight-bold text-right">{{ notesReport.totalPeerAdvisingNoteCount }}</td>
      </tr>
      <tr>
        <td>Distinct peer advisor authors</td>
        <td class="font-weight-bold text-right">{{ notesReport.distinctPeerAdvisorAuthors }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import type {PeerAdvisingManagerReport} from '@/lib/types-peer-advising'

defineProps({
  notesReport: {
    required: true,
    type: Object as PropType<PeerAdvisingManagerReport | undefined>
  }
})
</script>

<style scoped>
td {
  padding: 4px 0 4px 0;
}
td:first-child {
  padding-left: 16px;
}
</style>
