<template>
  <div class="ml-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <div class="d-flex flex-wrap justify-content-between">
        <h1
          id="cohort-name"
          class="page-section-header"
          tabindex="0">
          CE3 Admissions
          <span
            v-if="totalAdmitCount !== undefined"
            class="faint-text">{{ pluralize('admitted student', totalAdmitCount) }}</span>
        </h1>
        <div class="d-flex align-self-baseline mr-4">
          <NavLink
            id="admitted-students-cohort-show-filters"
            class="btn btn-link no-wrap pl-2 pr-2 pt-0"
            aria-label="Create a CE3 Admissions cohort"
            path="/cohort/new"
            :default-counter="counter"
            :query-args="{domain: 'admitted_students'}">
            Create Cohort
          </NavLink>
          <div class="faint-text">|</div>
          <span id="export-student-list-description" class="sr-only">Download CSV file containing all admitted students in this cohort</span>
          <b-btn
            id="export-student-list-button"
            :disabled="!exportEnabled || !totalAdmitCount"
            class="no-wrap pl-2 pr-2 pt-0"
            variant="link"
            aria-describedby="export-student-list-description"
            @click.prevent="exportCohort">
            Export List
          </b-btn>
        </div>
      </div>
      <AdmitDataWarning v-if="admits" :updated-at="$_.get(admits, '[0].updatedAt')" />
      <hr class="filters-section-separator mr-2 mt-3" />
      <SectionSpinner :loading="sorting" />
      <div>
        <a
          v-if="totalAdmitCount > pagination.itemsPerPage"
          id="skip-to-pagination-widget"
          class="sr-only"
          href="#pagination-widget"
          @click="alertScreenReader('Go to another page of search results')"
          @keyup.enter="alertScreenReader('Go to another page of search results')">Skip to bottom, other pages of search results</a>
        <div v-if="!sorting" class="cohort-column-results">
          <div class="justify-content-end d-flex align-items-center p-2">
            <SortBy domain="admitted_students" />
          </div>
          <div>
            <div class="cohort-column-results">
              <table id="cohort-admitted-students" class="table table-sm table-borderless cohort-admitted-students mx-2">
                <thead class="sortable-table-header">
                  <tr>
                    <th class="pt-3">Name</th>
                    <th class="pt-3">CS ID</th>
                    <th class="pt-3">SIR</th>
                    <th class="pt-3">CEP</th>
                    <th class="pt-3">Re-entry</th>
                    <th class="pt-3">1st Gen</th>
                    <th class="pt-3">UREM</th>
                    <th class="pt-3">Waiver</th>
                    <th class="pt-3">INT'L</th>
                    <th class="pt-3">Freshman/Transfer</th>
                  </tr>
                </thead>
                <tbody>
                  <AdmitStudentRow
                    v-for="(admit, index) in admits"
                    :id="`admit-${admit.csEmplId}`"
                    :key="admit.csEmplId"
                    :row-index="index"
                    :sorted-by="preferences.admitSortBy"
                    :admit-student="admit" />
                </tbody>
              </table>
            </div>
            <div v-if="totalAdmitCount > pagination.itemsPerPage" class="p-3">
              <Pagination
                :click-handler="goToPage"
                :init-page-number="pagination.currentPage"
                :limit="10"
                :per-page="pagination.itemsPerPage"
                :total-rows="totalAdmitCount" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdmitStudentRow from '@/components/admit/AdmitStudentRow'
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import Loading from '@/mixins/Loading'
import NavLink from '@/components/util/NavLink'
import Pagination from '@/components/util/Pagination'
import Scrollable from '@/mixins/Scrollable'
import SectionSpinner from '@/components/util/SectionSpinner'
import SortBy from '@/components/student/SortBy'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import { getAllAdmits } from '@/api/admit'
import { downloadCsv } from '@/api/cohort'

export default {
  name: 'AdmitStudents',
  components: {
    AdmitDataWarning,
    AdmitStudentRow,
    NavLink,
    Pagination,
    SectionSpinner,
    SortBy,
    Spinner
  },
  mixins: [
    Berkeley,
    Context,
    Loading,
    Scrollable,
    CurrentUserExtras,
    Util
  ],
  data: () => ({
    admits: undefined,
    counter: null,
    exportEnabled: true,
    pagination: {
      currentPage: 1,
      itemsPerPage: 50
    },
    sorting: false,
    totalAdmitCount: undefined
  }),
  mounted() {
    this.counter = this.$route.query._
    this.initPagination()
    this.loadAdmits()
  },
  created() {
    this.$eventHub.off('admitSortBy-user-preference-change')
    this.$eventHub.on('admitSortBy-user-preference-change', sortBy => {
      this.sorting = true
      this.loadAdmits()
      if (!this.loading) {
        this.goToPage(1)
        const action = `Sort admitted students by ${sortBy}`
        this.alertScreenReader(action)
      }
    })
  },
  methods: {
    exportCohort() {
      const name = 'CE3 Admissions'
      const fields = this.$_.map(this.getAdmitCsvExportColumns(), 'value')
      this.showExportListModal = false
      this.exportEnabled = false
      this.alertScreenReader(`Exporting ${name} cohort`)
      downloadCsv('admitted_students', name, [], fields).then(() => {
        this.exportEnabled = true
      })
    },
    goToPage(page) {
      if (page !== this.pagination.currentPage) {
        if (this.pagination.currentPage) {
          this.alertScreenReader(`Loading page ${page} of this cohort's students`)
        }
        this.pagination.currentPage = page
        this.$router.push({
          query: { ...this.$route.query, p: this.pagination.currentPage }
        })
      }
    },
    initPagination() {
      if (this.$route.query.p && !isNaN(this.$route.query.p)) {
        this.pagination.currentPage = parseInt(this.$route.query.p, 10)
      }
    },
    loadAdmits() {
      const limit = this.pagination.itemsPerPage
      const offset =
        this.pagination.currentPage === 0
          ? 0
          : (this.pagination.currentPage - 1) * limit
      getAllAdmits(this.preferences.admitSortBy, limit, offset).then(response => {
        if (response) {
          this.admits = this.$_.get(response, 'students')
          this.totalAdmitCount = this.$_.get(response, 'totalStudentCount')
          this.loaded(`${this.totalAdmitCount} CE3 admits loaded`)
          this.putFocusNextTick('cohort-name')
        } else {
          this.$router.push({ path: '/404' })
        }
        this.sorting = false
      })
    }
  }
}
</script>
