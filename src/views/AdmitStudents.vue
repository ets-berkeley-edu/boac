<template>
  <div v-if="!loading" class="default-margins">
    <div class="d-flex flex-wrap justify-space-between">
      <h1 id="cohort-name" class="page-section-header">
        CE3 Admissions
        <span
          v-if="totalAdmitCount !== undefined"
          class="text-grey"
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
      <div class="d-flex align-center align-self-center mr-6">
        <v-btn
          id="admitted-students-cohort-show-filters"
          class="font-size-15 px-1 text-no-wrap"
          aria-label="Create a CE3 Admissions cohort"
          color="anchor"
          variant="text"
          @click="createNewAdmittedStudentsCohort"
        >
          Create Cohort
        </v-btn>
        <div class="text-grey" role="separator">|</div>
        <v-btn
          id="export-student-list-button"
          :disabled="!exportEnabled || !totalAdmitCount"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          text="Export List"
          variant="text"
          @click="openFerpaReminderDialog"
        />
        <FerpaReminderModal
          :cancel="cancelExportModal"
          :confirm="exportCohort"
          :is-downloading="isDownloadingCSV"
          :show-modal="showExportListDialog"
        />
      </div>
    </div>
    <div v-if="admits" class="pb-2">
      <AdmitDataWarning :updated-at="_get(admits, '[0].updatedAt')" />
    </div>
    <SectionSpinner :loading="sorting" />
    <div v-if="!sorting">
      <div class="align-center d-flex justify-content-end mr-6">
        <div class="mr-auto">
          <CuratedGroupSelector
            context-description="Admit Students"
            domain="admitted_students"
            :students="admits"
          />
        </div>
        <div class="mr-4">
          <SortBy domain="admitted_students" />
        </div>
      </div>
      <div v-if="totalAdmitCount > pagination.itemsPerPage" class="mt-3">
        <Pagination
          :click-handler="goToPage"
          :init-page-number="pagination.currentPage"
          :limit="10"
          :per-page="pagination.itemsPerPage"
          :total-rows="totalAdmitCount"
        />
      </div>
      <div class="mt-3">
        <AdmitStudentsTable
          :include-curated-checkbox="true"
          :students="admits"
        />
        <hr />
      </div>
      <div v-if="totalAdmitCount > pagination.itemsPerPage" class="mt-3">
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
</template>

<script>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdmitStudentsTable from '@/components/admit/AdmitStudentsTable'
import Context from '@/mixins/Context'
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector'
import FerpaReminderModal from '@/components/util/FerpaReminderModal'
import Pagination from '@/components/util/Pagination'
import SectionSpinner from '@/components/util/SectionSpinner'
import SortBy from '@/components/student/SortBy'
import Util from '@/mixins/Util'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {downloadCsv} from '@/api/cohort'
import {getAdmitCsvExportColumns} from '@/berkeley'
import {getAllAdmits} from '@/api/admit'

export default {
  name: 'AdmitStudents',
  components: {
    AdmitDataWarning,
    AdmitStudentsTable,
    CuratedGroupSelector,
    FerpaReminderModal,
    Pagination,
    SectionSpinner,
    SortBy
  },
  mixins: [Context, Util],
  data: () => ({
    admits: undefined,
    counter: null,
    exportEnabled: true,
    isDownloadingCSV: false,
    pagination: {
      currentPage: 1,
      itemsPerPage: 50
    },
    showExportListDialog: false,
    sorting: false,
    totalAdmitCount: undefined
  }),
  created() {
    this.loadingStart()
    this.setEventHandler('admitSortBy-user-preference-change', this.onAdmitSortByUserPreferenceChange)
  },
  mounted() {
    this.counter = this.toInt(this.$route.query._, 0)
    this.initPagination()
    this.loadAdmits()
  },
  beforeUnmount() {
    this.removeEventHandler('admitSortBy-user-preference-change', this.onAdmitSortByUserPreferenceChange)
  },
  methods: {
    cancelExportModal() {
      this.showExportListDialog = false
      alertScreenReader('Export canceled')
    },
    createNewAdmittedStudentsCohort() {
      this.$router.push({
        path: '/cohort/new',
        query: {domain: 'admitted_students'}
      })
    },
    exportCohort() {
      const name = 'CE3 Admissions'
      this.isDownloadingCSV = true
      this.exportEnabled = false
      alertScreenReader(`Exporting cohort ${name}`)
      downloadCsv(
        'admitted_students',
        name,
        [],
        this._map(getAdmitCsvExportColumns(), 'value')
      ).then(() => {
        this.showExportListDialog = false
        this.exportEnabled = true
        this.isDownloadingCSV = false
      })
    },
    goToPage(page) {
      if (page !== this.pagination.currentPage) {
        if (this.pagination.currentPage) {
          alertScreenReader(`Loading page ${page} of this cohort's students`)
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
      getAllAdmits(this.currentUser.preferences.admitSortBy, limit, offset).then(response => {
        if (response) {
          this.admits = this._get(response, 'students')
          this.totalAdmitCount = this._get(response, 'totalStudentCount')
          this.loadingComplete(`${this.totalAdmitCount} CE3 admits loaded`)
          this.putFocusNextTick('cohort-name')
        } else {
          this.$router.push({path: '/404'})
        }
        this.sorting = false
      })
    },
    onAdmitSortByUserPreferenceChange(sortBy) {
      this.sorting = true
      this.loadAdmits()
      if (!this.loading) {
        this.goToPage(1)
        alertScreenReader(`Sort admitted students by ${sortBy}`)
      }
    },
    openFerpaReminderDialog() {
      this.showExportListDialog = true
      putFocusNextTick('modal-header')
    }
  }
}
</script>
