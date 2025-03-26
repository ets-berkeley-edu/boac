<template>
  <div class="mx-3 my-6">
    <h2 class="font-size-18">Reporting &amp; Statistics</h2>
    <div v-if="notesReport" class="d-flex justify-space-between mt-3">
      <div class="ml-3 pr-16 w-50">
        <table class="w-100">
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
        <div class="mt-6">
          <PeerAdvisingTemplatesUsed :notes-report="notesReport" />
        </div>
      </div>
      <div class="pr-8 w-50">
        <PeerAdvisingCurrentMonthReport :notes-report="notesReport" />
        <div class="mt-3">
          <PeerAdvisingHistoricalReport
            :current-month-label="notesReport.currentMonth.label"
            :peer-advising-department="peerAdvisingDepartment"
          />
        </div>
      </div>
    </div>
    <div v-if="!notesReport" class="mt-16 text-center w-100">
      <v-progress-circular
        :indeterminate="true"
        :size="36"
        :width="7"
        color="primary"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {onMounted, ref} from 'vue'
import type {PeerAdvisingDepartment, PeerAdvisingManagerReport} from '@/lib/types'
import PeerAdvisingCurrentMonthReport from '@/components/peer/reports/PeerAdvisingCurrentMonthReport.vue'
import PeerAdvisingTemplatesUsed from '@/components/peer/reports/PeerAdvisingTemplatesUsed.vue'
import PeerAdvisingHistoricalReport from '@/components/peer/reports/PeerAdvisingHistoricalReport.vue'
import {getPeerAdvisingNotesReport} from '@/api/peer-advising-reports'

const props = defineProps({
  peerAdvisingDepartment: {
    required: true,
    type: Object as PropType<PeerAdvisingDepartment>
  }
})

const notesReport = ref<PeerAdvisingManagerReport | undefined>(undefined)

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
