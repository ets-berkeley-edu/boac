<template>
  <div class="notes-report pb-3">
    <div class="align-center border-b-sm d-flex pb-2">
      <h2 class="font-size-20 mr-2">Notes</h2>
      <v-progress-circular
        v-if="isLoading"
        indeterminate
        size="16"
        width="2"
      />
      <div v-if="!isLoading" class="text-no-wrap">
        (<v-btn
          id="show-hide-notes-report"
          :aria-expanded="isShowingReport"
          class="font-size-16 letter-spacing-normal px-0 show-hide-notes-report-btn"
          color="primary"
          density="compact"
          slim
          :text="`${isShowingReport ? 'Hide' : 'Show'} complete notes report`"
          variant="text"
          @click="toggleShowReport"
        />)
      </div>
    </div>
    <div aria-live="polite" class="sr-only" role="status">
      <span v-if="isLoading">Notes report is loading.</span>
    </div>
    <div v-if="!isLoading && report">
      <div class="align-center d-flex flex-wrap justify-space-between mt-3">
        <h3 class="font-size-16 pr-2" :class="{'font-weight-bold': isShowingReport}">
          {{ numFormat(report.boa.total) }} notes have been created in BOA
        </h3>
        <div class="font-size-16 text-no-wrap">
          (<a id="download-boa-notes-metadata" :href="`${config.apiBaseUrl}/api/reports/boa_notes/metadata`">download<span class="sr-only"> notes report</span></a>)
        </div>
      </div>
      <v-expand-transition>
        <v-card v-if="isShowingReport" flat>
          <v-card-text>
            <div class="font-size-16">
              <div class="d-flex justify-space-between pt-1">
                <label class="font-weight-medium" for="notes-count-boa-authors">Distinct authors</label>
                <div id="notes-count-boa-authors" class="font-weight-bold">
                  {{ numFormat(report.boa.authors) }}
                </div>
              </div>
              <div class="d-flex justify-space-between pt-1">
                <label class="font-weight-medium" for="private-notes-count">Private notes</label>
                <div id="private-notes-count" class="font-weight-bold">
                  {{ numFormat(report.boa.privateNoteCount) }}
                </div>
              </div>
              <div class="d-flex justify-space-between pt-1">
                <label class="font-weight-medium" for="notes-count-boa-with-attachments">Notes with one or more attachments</label>
                <div id="notes-count-boa-with-attachments" class="font-weight-bold">
                  {{ numFormat((report.boa.withAttachments / report.boa.total) * 100, '0.0') }}%
                </div>
              </div>
              <div class="d-flex justify-space-between pt-1">
                <label class="font-weight-medium" for="notes-count-boa-with-topics">Notes with one or more topics</label>
                <div id="notes-count-boa-with-topics" class="font-weight-bold">
                  {{ numFormat((report.boa.withTopics / report.boa.total) * 100, '0.0') }}%
                </div>
              </div>
              <div class="pt-1">
                <h5 class="font-size-16">Batch Notes</h5>
                <div class="pl-3">
                  <div
                    v-for="row in [
                      {id: 'notes-batch-count', label: 'Total batch count', value: report.boa.batchNotes.totalBatchCount},
                      {id: 'notes-count-via-batch', label: 'Total count of notes created via batch', value: report.boa.batchNotes.totalNoteCount}
                    ]"
                    :key="row.id"
                    class="d-flex justify-space-between pt-1"
                  >
                    <label class="font-weight-medium" :for="row.id">{{ row.label }}</label>
                    <div :id="row.id" class="font-weight-bold">
                      {{ numFormat(row.value) }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="pt-1">
                <h5 class="font-size-16">Imported Notes</h5>
                <div class="pl-3">
                  <div
                    v-for="row in [
                      {id: 'notes-count-sis', label: 'CalCentral/SIS', value: report.sis},
                      {id: 'notes-count-asc', label: 'Athletic Study Center', value: report.asc},
                      {id: 'notes-count-ei', label: 'CE3', value: report.ei}
                    ]"
                    :key="row.id"
                    class="d-flex justify-space-between pt-1"
                  >
                    <div>
                      <label :for="row.id">{{ row.label }}</label>
                    </div>
                    <div :id="row.id" class="font-weight-bold">
                      {{ numFormat(row.value) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="pt-1">
              <h5 class="font-size-16">Peer-advisor notes</h5>
              <PeerAdvisingNotesReport class="font-size-16" :notes-report="report.boa.peerAdvising" />
            </div>
            <v-btn
              id="show-hide-boa-note-counts"
              :prepend-icon="isShowingBoaNoteCounts ? mdiChevronDown : mdiChevronRight"
              class="mt-3 px-0"
              flat
              slim
              @click="isShowingBoaNoteCounts = !isShowingBoaNoteCounts"
            >
              <div class="d-flex flex-wrap justify-start">
                <div>BOA note count by month </div>
                <div>(reverse chronological)</div>
              </div>
            </v-btn>
            <v-expand-transition>
              <div v-if="isShowingBoaNoteCounts" class="pt-3">
                <v-card
                  v-for="(annual, index) in boaNoteCountsByMonth"
                  :key="annual.year"
                  :class="{'mt-5': index > 0}"
                >
                  <v-card-title class="bg-primary">
                    {{ annual.year }}
                  </v-card-title>
                  <v-card-text>
                    <v-list class="border-sm rounded-lg mt-5">
                      <v-list-item
                        v-for="(row, monthIndex) in reverse(sortBy(annual.months, 'month'))"
                        :key="row.month"
                        :class="{'border-b-sm': monthIndex !== annual.months.length - 1}"
                      >
                        <div class="align-center d-flex font-size-16 justify-space-between">
                          <div class="font-weight-medium">
                            {{ DateTime.fromJSDate(new Date(annual.year, row.month - 1, 1)).toFormat('MMMM') }}
                          </div>
                          <v-chip
                            class="px-2 sidebar-pill"
                            color="primary"
                            variant="flat"
                          >
                            {{ row.count }}
                          </v-chip>
                        </div>
                      </v-list-item>
                    </v-list>
                  </v-card-text>
                </v-card>
              </div>
            </v-expand-transition>
          </v-card-text>
        </v-card>
      </v-expand-transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import {mdiChevronDown, mdiChevronRight} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {reverse, sortBy} from 'lodash'
import PeerAdvisingNotesReport from '@/components/peer/reports/PeerAdvisingNotesReport.vue'
import {numFormat} from '@/lib/utils'
import {getBoaNoteCountByMonth, getNotesReport} from '@/api/admin-reports.js'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  department: {
    required: true,
    type: Object
  }
})

const boaNoteCountsByMonth = ref()
const contextStore = useContextStore()
const config = contextStore.config
const isLoading = ref(true)
const report = ref()
const isShowingBoaNoteCounts = ref(false)
const isShowingReport = ref(false)

onMounted(() => {
  const requests = [
    new Promise<void>(resolve => getNotesReport(props.department.deptCode).then(data => report.value = data).finally(resolve)),
    new Promise<void>(resolve => getBoaNoteCountByMonth().then(data => boaNoteCountsByMonth.value = reverse(sortBy(data, 'year'))).finally(resolve)),
  ]
  Promise.all(requests).then(() => isLoading.value = false)
})

const toggleShowReport = () => {
  isShowingReport.value = !isShowingReport.value
  isShowingBoaNoteCounts.value = false
}
</script>

<style scoped>
.notes-report {
  max-width: 40rem;
}
.show-hide-notes-report-btn {
  margin-bottom: 2px;
}
</style>
