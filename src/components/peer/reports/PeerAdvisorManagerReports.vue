<template>
  <div class="mx-3 my-6">
    <div class="align-center d-flex justify-space-between pr-15 w-50">
      <h2 class="font-size-18 mr-3">Reporting &amp; Statistics</h2>
      <div>
        (<v-btn
          id="download-csv"
          aria-label="Download the users currently shown in Passenger Manifest"
          class="font-size-16 letter-spacing-normal pb-1 px-0 download-csv"
          :color="isDownloadingCsv ? 'black' : 'primary'"
          density="compact"
          :disabled="isDownloadingCsv"
          slim
          :text="isDownloadingCsv ? 'downloading...' : 'download notes'"
          variant="text"
          @click="() => downloadCSV()"
        >
          <template v-if="isDownloadingCsv" #prepend>
            <v-progress-circular
              class="ml-1"
              color="primary"
              indeterminate
              size="16"
              width="3"
            />
          </template>
        </v-btn>)
      </div>
    </div>
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
              <td class="font-weight-bold text-right">{{ notesReport.totalPeerAdvisingNoteCount }}</td>
            </tr>
            <tr>
              <td>Distinct peer advisor authors</td>
              <td class="font-weight-bold text-right">{{ notesReport.distinctPeerAdvisorAuthors }}</td>
            </tr>
          </tbody>
        </table>
        <div class="mt-6 pr-2">
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
import type {PeerAdvisingDepartment} from '@/lib/types'
import type {PeerAdvisingManagerReport} from '@/lib/types-peer-advising'
import PeerAdvisingCurrentMonthReport from '@/components/peer/reports/PeerAdvisingCurrentMonthReport.vue'
import PeerAdvisingHistoricalReport from '@/components/peer/reports/PeerAdvisingHistoricalReport.vue'
import PeerAdvisingTemplatesUsed from '@/components/peer/reports/PeerAdvisingTemplatesUsed.vue'
import {downloadPeerAdvisingNotes, getPeerAdvisingNotesReport} from '@/api/peer-advising-reports'

const props = defineProps({
  peerAdvisingDepartment: {
    required: true,
    type: Object as PropType<PeerAdvisingDepartment>
  }
})

const isDownloadingCsv = ref(false)
const notesReport = ref<PeerAdvisingManagerReport | undefined>(undefined)

onMounted(() => {
  getPeerAdvisingNotesReport(props.peerAdvisingDepartment.id).then(data => {
    notesReport.value = data
  })
})

const downloadCSV = () => {
  isDownloadingCsv.value = true
  downloadPeerAdvisingNotes(props.peerAdvisingDepartment).then(() => {
    isDownloadingCsv.value = false
  })
}
</script>

<style scoped>
td {
  padding: 4px 0 4px 0;
}
td:first-child {
  padding-left: 16px;
}
</style>
