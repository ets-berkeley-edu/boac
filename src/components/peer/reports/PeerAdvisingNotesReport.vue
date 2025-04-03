<template>
  <table v-if="notesReport" class="w-100">
    <caption class="sr-only">Peer advisor notes summary</caption>
    <tbody>
      <tr v-if="notesReport.peerAdvisingDepartment">
        <th scope="row">Total {{ notesReport.peerAdvisingDepartment.name }} peer advising notes</th>
        <td id="peer-advising-notes-total" class="font-weight-bold text-right">{{ notesReport.totalPeerAdvisingNoteCount }}</td>
      </tr>
      <tr v-if="!notesReport.peerAdvisingDepartment">
        <th scope="row">Total peer advisor notes</th>
        <td id="peer-advising-notes-total" class="font-weight-bold text-right">{{ notesReport.totalPeerAdvisingNoteCount }}</td>
      </tr>
      <tr>
        <th scope="row">Distinct peer advisor authors</th>
        <td id="peer-advising-note-authors-total" class="font-weight-bold text-right">{{ notesReport.distinctPeerAdvisorAuthors }}</td>
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
th {
  font-weight: normal;
  padding-left: 16px;
  text-align: left;
}
</style>
