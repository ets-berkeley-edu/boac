<template>
  <div class="ml-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <CohortPageHeader :show-history="showHistory" :toggle-show-history="toggleShowHistory" />
      <div v-if="domain === 'admitted_students' && students" class="pb-2">
        <AdmitDataWarning :updated-at="_get(students, '[0].updatedAt')" />
      </div>
      <b-collapse
        id="show-hide-filters"
        v-model="showFilters"
        class="mr-3 mb-3"
      >
        <FilterRow
          v-for="(filter, index) in filters"
          :key="filterRowUniqueKey(filter, index)"
          class="filter-row"
          :position="index"
        />
        <FilterRow v-if="isOwnedByCurrentUser" />
        <ApplyAndSaveButtons v-if="isOwnedByCurrentUser" />
      </b-collapse>
      <SectionSpinner :loading="editMode === 'apply'" />
      <div v-if="!showHistory && showStudentsSection">
        <div class="align-items-center d-flex justify-content-between mr-3 pt-1">
          <div>
            <CuratedGroupSelector
              :context-description="domain === 'default' ? `Cohort ${cohortName || ''}` : `Admitted Students Cohort ${cohortName || ''}`"
              :domain="domain"
              :on-create-curated-group="resetFiltersToLastApply"
              :students="students"
            />
          </div>
          <div class="d-flex flex-wrap justify-content-end">
            <div>
              <TermSelector v-if="domain === 'default'" />
            </div>
            <div class="pl-4">
              <SortBy v-if="showSortBy" :domain="domain" />
            </div>
          </div>
        </div>
        <div v-if="totalStudentCount > pagination.itemsPerPage" class="pt-1">
          <hr class="filters-section-separator mr-3" />
          <div class="mt-3">
            <Pagination
              :click-handler="goToPage"
              :init-page-number="pageNumber"
              :limit="10"
              :per-page="pagination.itemsPerPage"
              :total-rows="totalStudentCount"
            />
          </div>
        </div>
        <div v-if="domain === 'default'" id="cohort-students" class="list-group mr-2">
          <StudentRow
            v-for="(student, index) in students"
            :id="`student-${student.uid}`"
            :key="student.sid"
            :row-index="index"
            :student="student"
            :sorted-by="currentUser.preferences.sortBy"
            :term-id="currentUser.preferences.termId"
            :class="{'list-group-item-info': anchor === `#${student.uid}`}"
            list-type="cohort"
            class="border-right-0 list-group-item border-left-0 pl-0"
          />
        </div>
        <div v-if="domain === 'admitted_students'">
          <div class="pb-1">
            <hr class="filters-section-separator" />
          </div>
          <AdmitStudentsTable :include-curated-checkbox="true" :students="students" />
        </div>
        <div v-if="totalStudentCount > pagination.itemsPerPage" class="p-3">
          <Pagination
            :click-handler="goToPage"
            :init-page-number="pageNumber"
            :limit="10"
            :per-page="pagination.itemsPerPage"
            :total-rows="totalStudentCount"
          />
        </div>
      </div>
      <div v-if="showHistory">
        <CohortHistory />
      </div>
    </div>
  </div>
</template>

<script>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdmitStudentsTable from '@/components/admit/AdmitStudentsTable'
import ApplyAndSaveButtons from '@/components/cohort/ApplyAndSaveButtons'
import CohortEditSession from '@/mixins/CohortEditSession'
import CohortHistory from '@/components/cohort/CohortHistory'
import CohortPageHeader from '@/components/cohort/CohortPageHeader'
import Context from '@/mixins/Context'
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector'
import FilterRow from '@/components/cohort/FilterRow'
import Pagination from '@/components/util/Pagination'
import SectionSpinner from '@/components/util/SectionSpinner'
import SortBy from '@/components/student/SortBy'
import Spinner from '@/components/util/Spinner'
import store from '@/store'
import StudentRow from '@/components/student/StudentRow'
import TermSelector from '@/components/student/TermSelector'
import Util from '@/mixins/Util'
import {applyFilters, loadCohort, resetFiltersToLastApply, updateFilterOptions} from '@/store/modules/cohort-edit-session/utils'
import {scrollToTop} from '@/lib/utils'
import {translateSortByOption} from '@/berkeley'

export default {
  name: 'Cohort',
  components: {
    AdmitDataWarning,
    AdmitStudentsTable,
    ApplyAndSaveButtons,
    CohortHistory,
    CohortPageHeader,
    CuratedGroupSelector,
    FilterRow,
    Pagination,
    SectionSpinner,
    SortBy,
    Spinner,
    StudentRow,
    TermSelector
  },
  mixins: [CohortEditSession, Context, Util],
  data: () => ({
    pageNumber: undefined,
    showFilters: undefined,
    showHistory: false
  }),
  computed: {
    anchor: () => location.hash,
    showStudentsSection() {
      return this._size(this.students) && this.editMode !== 'apply'
    }
  },
  watch: {
    domain(newVal, oldVal) {
      this.removeEventHandler(`${oldVal === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, this.onChangeSortBy)
      this.setEventHandler(`${newVal === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, this.onChangeSortBy)
    },
    isCompactView() {
      this.showFilters = !this.isCompactView
    }
  },
  mounted() {
    const forwardPath = this.$routerHistory.hasForward() && this._get(this.$routerHistory.next(), 'path')
    const continueExistingSession =
      (this._startsWith(forwardPath, '/student') || this._startsWith(forwardPath, '/admit/student')) && this._size(this.filters)
    if (continueExistingSession) {
      this.showFilters = !this.isCompactView
      this.pageNumber = this.pagination.currentPage
      this.setPageTitle(this.cohortName)
      this.loadingComplete(this.getLoadedAlert())
    } else {
      const cohortId = this.toInt(this._get(this.$route, 'params.id'))
      const domain = this.$route.query.domain || 'default'
      const orderBy = this._get(this.currentUser.preferences, this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy')
      const termId = this._get(this.currentUser.preferences, 'termId')
      this.init(cohortId, domain, orderBy, termId).then(() => {
        this.showFilters = !this.isCompactView
        this.pageNumber = this.pagination.currentPage
        const pageTitle = this.cohortId ? this.cohortName : 'Create Cohort'
        this.setPageTitle(pageTitle)
        this.loadingComplete(this.getLoadedAlert())
        this.putFocusNextTick(this.cohortId ? 'cohort-name' : 'create-cohort-h1')
      })
    }
  },
  created() {
    const sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
    this.setEventHandler(`${sortByKey}-user-preference-change`, this.onChangeSortBy)
    this.setEventHandler('cohort-apply-filters', this.resetPagination)
    this.setEventHandler('termId-user-preference-change', this.onChangeTerm)
  },
  destroyed() {
    const sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
    this.removeEventHandler(`${sortByKey}-user-preference-change`, this.onChangeSortBy)
    this.removeEventHandler('cohort-apply-filters', this.resetPagination)
    this.removeEventHandler('termId-user-preference-change', this.onChangeTerm)
  },
  methods: {
    filterRowUniqueKey: (filter, index) => `${filter.key}-${filter.value}-${index}`,
    getLoadedAlert() {
      if (!this.cohortId) {
        return 'Create cohort page has loaded'
      } else {
        return `Cohort ${this.cohortName || ''}, sorted by ${translateSortByOption(this.currentUser.preferences.sortBy)}, ${this.pageNumber > 1 ? `(page ${this.pageNumber})` : ''} has loaded`
      }
    },
    init(cohortId, domain, orderBy, termId) {
      return new Promise(resolve => {
        this.resetSession()
        this.setCompactView(!!cohortId)
        this.setModifiedSinceLastSearch(undefined)
        store.commit('context/updateCurrentUserPreference', {
          key: domain === 'admitted_students' ? 'admitSortBy' : 'sortBy',
          value: orderBy
        })
        store.commit('context/updateCurrentUserPreference', {key: 'termId', value: termId})

        if (cohortId) {
          loadCohort(cohortId, orderBy, termId).then(resolve)
        } else {
          if (domain) {
            this.setDomain(domain)
          } else {
            throw new TypeError('\'domain\' is required when creating a new cohort.')
          }
          updateFilterOptions(this.domain, this.cohortOwner, []).then(() => {
            this.resetSession()
            this.stashOriginalFilters()
            resolve()
          })
        }
      })
    },
    goToPage(page) {
      this.setPagination(page)
      this.onPageNumberChange().then(() => {
        scrollToTop()
        this.loadingComplete(this.getLoadedAlert())
      })
    },
    onChangeSortBy() {
      if (!this.loading) {
        this.goToPage(1)
      }
    },
    onChangeTerm() {
      if (!this.loading) {
        this.goToPage(this.pageNumber)
      }
    },
    onPageNumberChange() {
      return applyFilters(
        this._get(this.currentUser.preferences, this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'),
        this._get(this.currentUser.preferences, 'termId')
      )
    },
    resetFiltersToLastApply,
    resetPagination() {
      this.setPagination(1)
    },
    setPagination(page) {
      this.pageNumber = page
      this.setCurrentPage(this.pageNumber)
    },
    toggleShowHistory(value) {
      this.showHistory = value
      if (value && !this.isCompactView) {
        this.toggleCompactView()
      }
      if (!value) {
        this.onPageNumberChange().then(scrollToTop)
      }
    }
  }
}
</script>

<style scoped>
.filter-row {
  align-items: center;
  background-color: #f3f3f3;
  border-left: 6px solid #3b7ea5 !important;
  min-height: 46px;
}
</style>
