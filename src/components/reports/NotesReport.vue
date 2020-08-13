<template>
  <div class="mb-3 mr-5 pt-4 w-50">
    <div class="align-items-end border-bottom d-flex pb-2">
      <div class="pr-2">
        <h2 class="mb-1 page-section-header-sub">Notes</h2>
      </div>
      <div v-if="isLoading">
        <font-awesome icon="sync" spin />
      </div>
      <div v-if="!isLoading" class="font-size-14 text-black-50">
        (<b-btn
          id="show-hide-notes-report"
          :aria-label="isShowingReport ? 'Hide full report' : 'Show full report'"
          class="p-0"
          variant="link"
          @click="isShowingReport = !isShowingReport">
          {{ isShowingReport ? 'Hide' : 'Show' }} complete notes report
        </b-btn>)
      </div>
    </div>
    <div
      v-if="isLoading"
      aria-live="polite"
      role="alert">
      <span class="sr-only">Notes report is loading.</span>
    </div>
    <div v-if="!isLoading">
      <h3 class="font-size-16 m-0 pt-3" :class="{'font-weight-bold': isShowingReport}">A total of {{ numFormat(report.boa.total) }} notes have been created in BOA.</h3>
      <b-collapse v-model="isShowingReport" class="mt-0 pt-3">
        <div>
          <div class="pl-3">
            <div class="d-flex justify-content-between">
              <div>
                <label for="notes-count-boa-authors">Distinct authors</label>
              </div>
              <div id="notes-count-boa-authors" class="font-weight-bolder">
                {{ numFormat(report.boa.authors) }}
              </div>
            </div>
            <div class="d-flex justify-content-between">
              <div>
                <label for="notes-count-boa-with-attachments">Notes with one or more attachments</label>
              </div>
              <div id="notes-count-boa-with-attachments" class="font-weight-bolder">
                {{ numFormat((report.boa.withAttachments / report.boa.total) * 100, '0.0') }}%
              </div>
            </div>
            <div class="d-flex justify-content-between">
              <div>
                <label for="notes-count-boa-with-topics">Notes with one or more topics</label>
              </div>
              <div id="notes-count-boa-with-topics" class="font-weight-bolder">
                {{ numFormat((report.boa.withTopics / report.boa.total) * 100, '0.0') }}%
              </div>
            </div>
          </div>
        </div>
        <div class="pt-2">
          <h5 class="font-size-16 font-weight-bold">Imported from CalCentral/SIS</h5>
          <div class="pl-3">
            <div class="d-flex justify-content-between">
              <div>
                <label for="notes-count-sis">Total</label>
              </div>
              <div id="notes-count-sis" class="font-weight-bolder">
                {{ numFormat(report.sis) }}
              </div>
            </div>
          </div>
        </div>
        <div class="pt-2">
          <h5 class="font-size-16 font-weight-bold">Imported from Athletic Study Center</h5>
          <div class="pl-3">
            <div class="d-flex justify-content-between">
              <div>
                <label for="notes-count-asc">Total</label>
              </div>
              <div id="notes-count-asc" class="font-weight-bolder">
                {{ numFormat(report.asc) }}
              </div>
            </div>
          </div>
        </div>
        <div class="pt-2">
          <h5 class="font-size-16 font-weight-bold">Imported from Centers for Educational Equity and Excellence</h5>
          <div class="pl-3">
            <div class="d-flex justify-content-between">
              <div>
                <label for="notes-count-ei">Total</label>
              </div>
              <div id="notes-count-ei" class="font-weight-bolder">
                {{ numFormat(report.ei) }}
              </div>
            </div>
          </div>
        </div>
      </b-collapse>
    </div>
  </div>
</template>

<script>
import Util from '@/mixins/Util';
import { getNotesReport } from "@/api/reports";

export default {
  name: 'NotesReport',
  mixins: [Util],
  props: {
    department: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    isLoading: true,
    report: undefined,
    isShowingReport: false
  }),
  created() {
    getNotesReport(this.department.code).then(report => {
      this.report = report;
      this.isLoading = false;
    });
  }
}
</script>
