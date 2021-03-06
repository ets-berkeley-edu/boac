<template>
  <div class="ml-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <CohortPageHeader :show-history="showHistory" :toggle-show-history="toggleShowHistory" />
      <AdmitDataWarning v-if="domain === 'admitted_students' && students" :updated-at="$_.get(students, '[0].updatedAt')" />
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
        <hr class="filters-section-separator mr-2 mt-0" />
        <div class="cohort-column-results">
          <div
            :class="{
              'justify-content-end': domain === 'admitted_students',
              'justify-content-between': domain === 'default'
            }"
            class="align-items-center d-flex mr-3 pb-1 pt-2"
          >
            <SelectAll
              v-if="domain === 'default'"
              :context-description="`Cohort ${cohortName || ''}`"
              :ga-event-tracker="$ga.cohortEvent"
              :on-create-curated-group="resetFiltersToLastApply"
              :students="students"
            />
            <div class="pt-1">
              <TermSelector />
            </div>
            <div class="pt-1">
              <SortBy v-if="showSortBy" :domain="domain" />
            </div>
          </div>
          <div v-if="totalStudentCount > pagination.itemsPerPage">
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
          <div>
            <div class="cohort-column-results">
              <div v-if="domain === 'default'" id="cohort-students" class="list-group mr-2">
                <StudentRow
                  v-for="(student, index) in students"
                  :id="`student-${student.uid}`"
                  :key="student.sid"
                  :row-index="index"
                  :student="student"
                  :sorted-by="preferences.sortBy"
                  :term-id="preferences.termId"
                  :class="{'list-group-item-info': anchor === `#${student.uid}`}"
                  list-type="cohort"
                  class="border-right-0 list-group-item border-left-0 pl-0"
                />
              </div>
              <table v-if="domain === 'admitted_students'" id="cohort-admitted-students" class="table table-sm table-borderless cohort-admitted-students mx-2">
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
                    v-for="(student, index) in students"
                    :id="`admit-${student.csEmplId}`"
                    :key="student.csEmplId"
                    :row-index="index"
                    :sorted-by="preferences.admitSortBy"
                    :admit-student="student"
                  />
                </tbody>
              </table>
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
import AdmitStudentRow from '@/components/admit/AdmitStudentRow'
import ApplyAndSaveButtons from '@/components/cohort/ApplyAndSaveButtons'
import CohortEditSession from '@/mixins/CohortEditSession'
import CohortHistory from '@/components/cohort/CohortHistory'
import CohortPageHeader from '@/components/cohort/CohortPageHeader'
import Context from '@/mixins/Context'
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import FilterRow from '@/components/cohort/FilterRow'
import Loading from '@/mixins/Loading'
import Pagination from '@/components/util/Pagination'
import Scrollable from '@/mixins/Scrollable'
import SectionSpinner from '@/components/util/SectionSpinner'
import SelectAll from '@/components/curated/dropdown/SelectAll'
import SortBy from '@/components/student/SortBy'
import Spinner from '@/components/util/Spinner'
import StudentRow from '@/components/student/StudentRow'
import TermSelector from '@/components/student/TermSelector'
import Util from '@/mixins/Util'

export default {
  name: 'Cohort',
  components: {
    AdmitDataWarning,
    AdmitStudentRow,
    ApplyAndSaveButtons,
    CohortHistory,
    CohortPageHeader,
    FilterRow,
    Pagination,
    SectionSpinner,
    SelectAll,
    SortBy,
    Spinner,
    StudentRow,
    TermSelector
  },
  mixins: [
    CohortEditSession,
    Context,
    Loading,
    Scrollable,
    CurrentUserExtras,
    Util
  ],
  data: () => ({
    pageNumber: undefined,
    showFilters: undefined,
    showHistory: false
  }),
  computed: {
    anchor: () => location.hash,
    showStudentsSection() {
      return this.$_.size(this.students) && this.editMode !== 'apply'
    }
  },
  watch: {
    isCompactView() {
      this.showFilters = !this.isCompactView
    }
  },
  mounted() {
    const forwardPath = this.$routerHistory.hasForward() && this.$_.get(this.$routerHistory.next(), 'path')
    const continueExistingSession =
      (this.$_.startsWith(forwardPath, '/student') || this.$_.startsWith(forwardPath, '/admit/student')) && this.$_.size(this.filters)
    if (continueExistingSession) {
      this.showFilters = !this.isCompactView
      this.pageNumber = this.pagination.currentPage
      this.setPageTitle(this.cohortName)
      this.loaded(this.getLoadedAlert())
    } else {
      const domain = this.$route.query.domain || 'default'
      const id = this.toInt(this.$_.get(this.$route, 'params.id'))
      const termId = this.$_.get(this.preferences, 'termId')
      this.init({
        id,
        orderBy: this.$_.get(this.preferences, domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'),
        termId: termId,
        domain
      }).then(() => {
        this.showFilters = !this.isCompactView
        this.pageNumber = this.pagination.currentPage
        const pageTitle = this.cohortId ? this.cohortName : 'Create Cohort'
        this.setPageTitle(pageTitle)
        this.loaded(this.getLoadedAlert())
        this.putFocusNextTick(this.cohortId ? 'cohort-name' : 'create-cohort-h1')
        this.$ga.cohortEvent(this.cohortId || '', this.cohortName || '', 'view')
      })
    }
  },
  created() {
    const domain = this.$route.query.domain || 'default'
    this.$eventHub.on('cohort-apply-filters', () => {
      this.setPagination(1)
    })
    this.$eventHub.on(`${domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, sortBy => {
      if (!this.loading) {
        this.goToPage(1)
        this.$ga.cohortEvent(this.cohortId || '', this.cohortName || '', `Sort ${domain === 'admitted_students' ? 'admitted ' : ''}students by ${sortBy}`)
      }
    })
    this.$eventHub.on('termId-user-preference-change', termId => {
      if (!this.loading) {
        this.goToPage(this.pageNumber)
        this.$ga.cohortEvent(this.cohortId || '', this.cohortName || '', `Term id changed to ${termId}`)
      }
    })
  },
  methods: {
    filterRowUniqueKey: (filter, index) => `${filter.key}-${filter.value}-${index}`,
    getLoadedAlert() {
      if (!this.cohortId) {
        return 'Create cohort page has loaded'
      } else {
        return `Cohort ${this.cohortName || ''}, sorted by ${this.translateSortByOption(this.preferences.sortBy)}, ${this.pageNumber > 1 ? `(page ${this.pageNumber})` : ''} has loaded`
      }
    },
    goToPage(page) {
      if (page > 1) {
        this.$ga.cohortEvent(this.cohortId || '', this.cohortName || '', `Go to page ${page}`)
      }
      this.setPagination(page)
      this.onPageNumberChange().then(this.scrollToTop)
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
        this.onPageNumberChange().then(this.scrollToTop)
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
