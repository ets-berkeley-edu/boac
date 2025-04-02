<template>
  <v-container fluid>
    <v-row>
      <v-col class="pr-7" cols="12" md="6">
        <div class="align-center d-flex flex-wrap justify-space-between">
          <h2 class="font-size-18 mr-3">Reporting &amp; Statistics</h2>
          <div class="text-no-wrap">
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
        <PeerAdvisingNotesReport :notes-report="notesReport" :peer-advising-department="peerAdvisingDepartment" />
        <div class="pt-6 pr-2">
          <PeerAdvisingTemplatesUsed :notes-report="notesReport" />
        </div>
      </v-col>
      <v-col class="pl-7" cols="12" md="6">
        <div v-if="notesReport">
          <PeerAdvisingCurrentMonthReport :notes-report="notesReport" />
          <PeerAdvisingHistoricalReport
            class="mt-3"
            :current-month-label="notesReport.currentMonth.label"
            :peer-advising-department="peerAdvisingDepartment"
          />
        </div>
        <div v-if="!notesReport" class="mt-16 text-center">
          <v-progress-circular
            :indeterminate="true"
            :size="36"
            :width="7"
            color="primary"
          />
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import {onMounted, ref} from 'vue'
import type {PropType} from 'vue'
import PeerAdvisingNotesReport from '@/components/peer/reports/PeerAdvisingNotesReport.vue'
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
