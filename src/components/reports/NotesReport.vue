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
          class="p-0"
          variant="link"
          @click="isShowingReport = !isShowingReport"
        >
          {{ isShowingReport ? 'Hide' : 'Show' }} complete notes report
        </b-btn>)
      </div>
    </div>
    <div
      v-if="isLoading"
      aria-live="polite"
      role="alert"
    >
      <span class="sr-only">Notes report is loading.</span>
    </div>
    <div v-if="!isLoading">
      <div class="d-flex pt-3">
        <div>
          <h3 class="font-size-16 pr-2" :class="{'font-weight-bold': isShowingReport}">
            {{ numFormat(report.boa.total) }} notes have been created in BOA
          </h3>
        </div>
        <div class="font-size-14 pb-2 text-black-50">
          (<a id="download-boa_notes-metadata" :href="`${$config.apiBaseUrl}/api/reports/boa_notes/metadata`">download</a>)
        </div>
      </div>
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
                <label for="private-notes-count">Private notes</label>
              </div>
              <div id="private-notes-count" class="font-weight-bolder">
                {{ numFormat(report.boa.privateNoteCount) }}
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
            <div class="align-items-center d-flex">
              <div class="pr-2">
                <b-btn
                  id="show-hide-boa-note-counts"
                  class="caret-toggle"
                  variant="link"
                  @click="isShowingBoaNoteCounts = !isShowingBoaNoteCounts"
                >
                  <font-awesome v-if="!isShowingBoaNoteCounts" icon="caret-right" />
                  <span v-if="!isShowingBoaNoteCounts" class="sr-only">Show</span>
                  <font-awesome v-if="isShowingBoaNoteCounts" icon="caret-down" />
                  <span v-if="isShowingBoaNoteCounts" class="sr-only">Hide</span>
                </b-btn>
              </div>
              <div>
                BOA note count by month <span class="text-secondary">(reverse chronological)</span>
              </div>
            </div>
            <b-collapse v-model="isShowingBoaNoteCounts" class="mt-0 pt-3">
              <b-card
                v-for="annual in boaNoteCountsByMonth"
                :key="annual.year"
                class="mb-2"
                border-variant="primary"
                :header="`${annual.year}`"
                header-bg-variant="primary"
                header-class="btn-primary-color-override font-size-16"
                header-text-variant="white"
              >
                <b-list-group>
                  <b-list-group-item
                    v-for="row in $_.reverse($_.sortBy(annual.months, 'month'))"
                    :key="row.month"
                    class="d-flex justify-content-between align-items-center"
                  >
                    {{ new Date(annual.year, row.month - 1, 1) | moment('MMMM') }}
                    <b-badge class="btn-primary-color-override" variant="primary" pill>{{ row.count }}</b-badge>
                  </b-list-group-item>
                </b-list-group>
              </b-card>
            </b-collapse>
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
import Util from '@/mixins/Util'
import {getBoaNoteCountByMonth, getNotesReport} from '@/api/reports'

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
    boaNoteCountsByMonth: undefined,
    isLoading: true,
    report: undefined,
    isShowingBoaNoteCounts: false,
    isShowingReport: false
  }),
  created() {
    getNotesReport(this.department.code).then(report => {
      this.report = report
      getBoaNoteCountByMonth().then(data => {
        this.boaNoteCountsByMonth = this.$_.reverse(this.$_.sortBy(data, 'year'))
        this.isLoading = false
      })
    })
  }
}
</script>

<style scoped>
.caret-toggle {
  color: #337ab7;
  height: 15px;
  line-height: 1;
  margin-bottom: 6px;
  padding: 0;
  width: 16px;
}
</style>
