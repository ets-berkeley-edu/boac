<template>
  <div class="ma-3">
    <h2 class="font-size-18">Reporting &amp; Statistics</h2>
    <div v-if="notesReport" class="d-flex justify-space-between mt-3">
      <div class="pr-16 w-50">
        <table class="ml-3 w-100">
          <thead class="sr-only">
            <tr>
              <th>Measurement</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Total {{ peerAdvisingDepartment.name }} peer advising notes</td>
              <td class="text-right">{{ notesReport.totalPeerAdvisingNoteCount }}</td>
            </tr>
            <tr>
              <td>Distinct peer advisor authors</td>
              <td class="text-right">{{ notesReport.distinctPeerAdvisorAuthors }}</td>
            </tr>
          </tbody>
        </table>
        <h3 class="font-size-16 mt-3">Templates Used</h3>
        <table class="ml-3 w-100">
          <thead class="sr-only">
            <tr>
              <th>Note Template Title</th>
              <th>Note Template Usage Count</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(noteTemplate, index) in notesReport.noteTemplates" :key="noteTemplate.name">
              <td :class="{'pt-2': index === 0}">{{ noteTemplate.templateTitle }}</td>
              <td class="text-right">{{ noteTemplate.noteTemplateUsageCount }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pr-8 w-50">
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {onMounted, ref} from 'vue'
import type {PeerAdvisingDepartment} from '@/lib/types'
import {getPeerAdvisingNotesReport} from '@/api/peer-advising-reports'
import PillCount from '@/components/util/PillCount.vue'

const props = defineProps({
  peerAdvisingDepartment: {
    required: true,
    type: Object as PropType<PeerAdvisingDepartment>
  }
})

const notesReport = ref(undefined)

onMounted(() => {
  getPeerAdvisingNotesReport(props.peerAdvisingDepartment.id).then(data => {
    notesReport.value = data
  })
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
