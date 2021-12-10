<template>
  <div class="ml-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <div class="d-flex flex-wrap justify-content-between">
        <h1 id="cohort-name" class="page-section-header">
          CE3 Admissions
          <span
            v-if="totalAdmitCount !== undefined"
            class="faint-text"
          >{{ pluralize('admitted student', totalAdmitCount) }}</span>
        </h1>
        <a
          v-if="totalAdmitCount > pagination.itemsPerPage"
          id="skip-to-pagination-widget"
          class="sr-only"
          href="#pagination-widget"
          @click="alertScreenReader('Go to another page of search results')"
          @keyup.enter="alertScreenReader('Go to another page of search results')"
        >
          Skip to bottom, other pages of search results
        </a>
        <div class="d-flex align-self-baseline mr-4">
          <NavLink
            id="admitted-students-cohort-show-filters"
            class="btn btn-link no-wrap pl-0 pr-1 pt-0"
            aria-label="Create a CE3 Admissions cohort"
            path="/cohort/new"
            :default-counter="counter"
            :query-args="{domain: 'admitted_students'}"
          >
            Create Cohort
          </NavLink>
          <div class="faint-text">|</div>
          <b-btn
            id="export-student-list-button"
            :disabled="!exportEnabled || !totalAdmitCount"
            class="no-wrap pl-1 pr-0 pt-0"
            variant="link"
            @click.prevent="exportCohort"
          >
            Export List
          </b-btn>
        </div>
      </div>
      <div v-if="admits" class="pb-2">
        <AdmitDataWarning :updated-at="$_.get(admits, '[0].updatedAt')" />
      </div>
      <SectionSpinner :loading="sorting" />
      <div v-if="!sorting">
        <div class="float-right pb-2">
          <SortBy domain="admitted_students" />
        </div>
        <table id="cohort-admitted-students" class="border-top-0 table table-sm table-borderless cohort-admitted-students mx-2">
          <thead class="sortable-table-header">
            <tr>
              <th class="align-top pt-3">Name</th>
              <th class="align-top pt-3 text-nowrap">CS ID</th>
              <th class="align-top pt-3">SIR</th>
              <th class="align-top pt-3">CEP</th>
              <th class="align-top pt-3 text-nowrap">Re-entry</th>
              <th class="align-top pt-3 text-nowrap">1st Gen</th>
              <th class="align-top pt-3">UREM</th>
              <th class="align-top pt-3">Waiver</th>
              <th class="align-top pt-3">INT'L</th>
              <th class="align-top pt-3">Freshman or Transfer</th>
            </tr>
          </thead>
          <tbody>
            <AdmitStudentRow
              v-for="(admit, index) in admits"
              :id="`admit-${admit.csEmplId}`"
              :key="admit.csEmplId"
              :row-index="index"
              :sorted-by="$currentUser.preferences.admitSortBy"
              :admit-student="admit"
            />
          </tbody>
        </table>
        <div v-if="totalAdmitCount > pagination.itemsPerPage" class="p-3">
          <Pagination
            :click-handler="goToPage"
            :init-page-number="pagination.currentPage"
            :limit="10"
            :per-page="pagination.itemsPerPage"
            :total-rows="totalAdmitCount"
          />
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
import Loading from '@/mixins/Loading'
import NavLink from '@/components/util/NavLink'
import Pagination from '@/components/util/Pagination'
import Scrollable from '@/mixins/Scrollable'
import SectionSpinner from '@/components/util/SectionSpinner'
import SortBy from '@/components/student/SortBy'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {getAllAdmits} from '@/api/admit'
import {downloadCsv} from '@/api/cohort'

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
    this.counter = this.toInt(this.$route.query._, 0)
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
      this.alertScreenReader(`Exporting cohort ${name}`)
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
          query: {...this.$route.query, p: this.pagination.currentPage}
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
      getAllAdmits(this.$currentUser.preferences.admitSortBy, limit, offset).then(response => {
        if (response) {
          this.admits = this.$_.get(response, 'students')
          this.totalAdmitCount = this.$_.get(response, 'totalStudentCount')
          this.loaded(`${this.totalAdmitCount} CE3 admits loaded`)
          this.$putFocusNextTick('cohort-name')
        } else {
          this.$router.push({path: '/404'})
        }
        this.sorting = false
      })
    }
  }
}
</script>
