<template>
  <div class="mb-3 mr-5 pt-4 w-50">
    <div class="align-items-end border-bottom d-flex pb-2">
      <div class="pr-2">
        <h3 class="mb-1 page-section-header-sub">Notes</h3>
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
    <div v-if="!isLoading && !isShowingReport" class="font-weight-500">
      {{ report.boa.total | numFormat }} notes have been created in BOA.
    </div>
    <div v-if="!isLoading && isShowingReport">
      <div>
        <h4 class="font-size-16 font-weight-bold">Created in BOA</h4>
        <div class="pl-3">
          <div class="d-flex justify-content-between">
            <div>
              <label for="notes-count-boa">Total</label>
            </div>
            <div id="notes-count-boa" class="font-weight-bolder">
              {{ report.boa.total | numFormat }}
            </div>
          </div>
          <div class="d-flex justify-content-between">
            <div>
              <label for="notes-count-boa-authors">Distinct authors</label>
            </div>
            <div id="notes-count-boa-authors" class="font-weight-bolder">
              {{ report.boa.authors | numFormat }}
            </div>
          </div>
          <div class="d-flex justify-content-between">
            <div>
              <label for="notes-count-boa-with-attachments">Notes with one or more attachments</label>
            </div>
            <div id="notes-count-boa-with-attachments" class="font-weight-bolder">
              {{ (report.boa.withAttachments / report.boa.total) * 100 | numFormat('0.0') }}%
            </div>
          </div>
          <div class="d-flex justify-content-between">
            <div>
              <label for="notes-count-boa-with-topics">Notes with one or more topics</label>
            </div>
            <div id="notes-count-boa-with-topics" class="font-weight-bolder">
              {{ (report.boa.withTopics / report.boa.total) * 100 | numFormat('0.0') }}%
            </div>
          </div>
        </div>
      </div>
      <div class="pt-2">
        <h4 class="font-size-16 font-weight-bold">Imported from CalCentral/SIS</h4>
        <div class="pl-3">
          <div class="d-flex justify-content-between">
            <div>
              <label for="notes-count-sis">Total</label>
            </div>
            <div id="notes-count-sis" class="font-weight-bolder">
              {{ report.sis | numFormat }}
            </div>
          </div>
        </div>
      </div>
      <div class="pt-2">
        <h4 class="font-size-16 font-weight-bold">Imported from Athletic Study Center</h4>
        <div class="pl-3">
          <div class="d-flex justify-content-between">
            <div>
              <label for="notes-count-asc">Total</label>
            </div>
            <div id="notes-count-asc" class="font-weight-bolder">
              {{ report.asc | numFormat }}
            </div>
          </div>
        </div>
      </div>
      <div class="pt-2">
        <h4 class="font-size-16 font-weight-bold">Imported from Centers for Educational Equity and Excellence</h4>
        <div class="pl-3">
          <div class="d-flex justify-content-between">
            <div>
              <label for="notes-count-ei">Total</label>
            </div>
            <div id="notes-count-ei" class="font-weight-bolder">
              {{ report.ei | numFormat }}
            </div>
          </div>
        </div>
      </div>
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
  watch: {
    department() {
      this.render();
    }
  },
  created() {
    this.render();
  },
  methods: {
    render() {
      this.isLoading = true;
      getNotesReport(this.department.code).then(report => {
        this.report = report;
        this.isLoading = false;
      });
    }
  }
}
</script>
