<template>
  <div class="pl-3 pr-2 pt-3">
    <Spinner />
    <div v-if="!useContextStore().loading">
      <CohortPageHeader :show-history="showHistory" :toggle-show-history="toggleShowHistory" />
      <div v-if="useCohortStore().domain === 'admitted_students' && useCohortStore().students" class="pb-2">
        <AdmitDataWarning :updated-at="get(useCohortStore().students, '[0].updatedAt')" />
      </div>
      <v-expand-transition>
        <v-card
          v-show="showFilters"
          id="show-hide-filters"
          class="overflow-visible"
          flat
          tile
        >
          <FilterRow
            v-for="(filter, index) in useCohortStore().filters"
            :key="filterRowUniqueKey(filter, index)"
            class="filter-row"
            :position="index"
          />
          <FilterRow v-if="useCohortStore().isOwnedByCurrentUser" />
          <ApplyAndSaveButtons v-if="useCohortStore().isOwnedByCurrentUser" />
        </v-card>
      </v-expand-transition>
      <SectionSpinner :loading="useCohortStore().editMode === 'apply'" />
      <div v-if="!showHistory && showStudentsSection">
        <div class="d-flex flex-column flex-column-reverse flex-sm-row justify-space-between w-100 pt-4">
          <CuratedGroupSelector
            :context-description="useCohortStore().domain === 'default' ? `Cohort ${useCohortStore().cohortName || ''}` : `Admitted Students Cohort ${useCohortStore().cohortName || ''}`"
            :domain="useCohortStore().domain"
            :on-create-curated-group="resetFiltersToLastApply"
            :students="useCohortStore().students"
          />
          <div class="d-flex flex-wrap justify-end">
            <TermSelector v-if="useCohortStore().domain === 'default'" />
            <SortBy v-if="useCohortStore().showSortBy" :domain="useCohortStore().domain" />
          </div>
        </div>
        <hr class="mt-2 mb-0" />
        <div v-if="useCohortStore().totalStudentCount > useCohortStore().pagination.itemsPerPage" class="pt-1">
          <Pagination
            class="my-3"
            :click-handler="goToPage"
            :init-page-number="pageNumber"
            :limit="10"
            :per-page="useCohortStore().pagination.itemsPerPage"
            :total-rows="useCohortStore().totalStudentCount"
          />
          <hr class="mt-4 mb-0" />
        </div>
        <v-container v-if="useCohortStore().domain === 'default'" id="cohort-students" class="px-3">
          <StudentRow
            v-for="(student, index) in useCohortStore().students"
            :id="`student-${student.uid}`"
            :key="student.sid"
            class="border-right-0 list-group-item border-left-0 pl-0"
            :class="{'list-group-item-info': anchor === `#${student.uid}`}"
            list-type="cohort"
            :row-index="index"
            :sorted-by="useContextStore().currentUser.preferences.sortBy"
            :student="student"
            :term-id="useContextStore().currentUser.preferences.termId"
          />
        </v-container>
        <div v-if="useCohortStore().domain === 'admitted_students'">
          <hr />
          <AdmitStudentsTable :include-curated-checkbox="true" :students="useCohortStore().students" />
          <hr />
        </div>
        <Pagination
          v-if="useCohortStore().totalStudentCount > useCohortStore().pagination.itemsPerPage"
          :click-handler="goToPage"
          :index="1"
          :init-page-number="pageNumber"
          :limit="10"
          :per-page="useCohortStore().pagination.itemsPerPage"
          :total-rows="useCohortStore().totalStudentCount"
        />
      </div>
      <div v-if="showHistory">
        <CohortHistory />
      </div>
    </div>
  </div>
</template>

<script setup>
import {get, size, startsWith} from 'lodash'
</script>

<script>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdmitStudentsTable from '@/components/admit/AdmitStudentsTable'
import ApplyAndSaveButtons from '@/components/cohort/ApplyAndSaveButtons'
import CohortHistory from '@/components/cohort/CohortHistory'
import CohortPageHeader from '@/components/cohort/CohortPageHeader'
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector'
import FilterRow from '@/components/cohort/FilterRow'
import Pagination from '@/components/util/Pagination'
import SectionSpinner from '@/components/util/SectionSpinner'
import SortBy from '@/components/student/SortBy'
import Spinner from '@/components/util/Spinner'
import StudentRow from '@/components/student/StudentRow'
import TermSelector from '@/components/student/TermSelector'
import {applyFilters, loadCohort, resetFiltersToLastApply, updateFilterOptions} from '@/stores/cohort-edit-session/utils'
import {putFocusNextTick, scrollToTop, setPageTitle, toInt} from '@/lib/utils'
import {translateSortByOption} from '@/berkeley'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

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
  data: () => ({
    pageNumber: undefined,
    showHistory: false
  }),
  computed: {
    anchor: () => location.hash,
    showFilters() {
      return !useCohortStore().isCompactView
    },
    showStudentsSection() {
      return size(useCohortStore().students) && useCohortStore().editMode !== 'apply'
    },
    sortByKey() {
      return useCohortStore().domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
    }
  },
  watch: {
    domain(newVal) {
      useContextStore().removeEventHandler('admitSortBy-user-preference-change', this.onChangeSortBy)
      useContextStore().removeEventHandler('sortBy-user-preference-change', this.onChangeSortBy)
      useContextStore().setEventHandler(`${newVal === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, this.onChangeSortBy)
    }
  },
  mounted() {
    const forwardPath = window.history.state.forward
    const continueExistingSession = (startsWith(forwardPath, '/student') || startsWith(forwardPath, '/admit/student')) && size(useCohortStore().filters)
    if (continueExistingSession) {
      this.pageNumber = useCohortStore().pagination.currentPage
      setPageTitle(useCohortStore().cohortName)
      useContextStore().loadingComplete(this.getLoadedAlert())
    } else {
      const cohortId = toInt(get(useRoute(), 'params.id'))
      const domain = useRoute().query.domain || 'default'
      const orderBy = get(useContextStore().currentUser.preferences, this.sortByKey)
      const termId = get(useContextStore().currentUser.preferences, 'termId')
      this.init(cohortId, domain, orderBy, termId).then(() => {
        this.pageNumber = useCohortStore().pagination.currentPage
        const pageTitle = this.cohortId ? useCohortStore().cohortName : 'Create Cohort'
        setPageTitle(pageTitle)
        useContextStore().loadingComplete(this.getLoadedAlert())
        putFocusNextTick(this.cohortId ? 'cohort-name' : 'create-cohort-h1')
      })
    }
  },
  created() {
    useContextStore().setEventHandler(`${this.sortByKey}-user-preference-change`, this.onChangeSortBy)
    useContextStore().setEventHandler('cohort-apply-filters', this.resetPagination)
    useContextStore().setEventHandler('termId-user-preference-change', this.onChangeTerm)
  },
  unmounted() {
    useContextStore().removeEventHandler('admitSortBy-user-preference-change', this.onChangeSortBy)
    useContextStore().removeEventHandler('sortBy-user-preference-change', this.onChangeSortBy)
    useContextStore().removeEventHandler('cohort-apply-filters', this.resetPagination)
    useContextStore().removeEventHandler('termId-user-preference-change', this.onChangeTerm)
  },
  methods: {
    filterRowUniqueKey: (filter, index) => `${filter.key}-${index}`,
    getLoadedAlert() {
      if (!this.cohortId) {
        return 'Create cohort page has loaded'
      } else {
        const sortByOption = translateSortByOption(get(useContextStore().currentUser.preferences, this.sortByKey))
        return `Cohort ${useCohortStore().cohortName || ''}, sorted by ${sortByOption}, ${this.pageNumber > 1 ? `(page ${this.pageNumber})` : ''} has loaded`
      }
    },
    init(cohortId, domain, orderBy, termId) {
      return new Promise(resolve => {
        useCohortStore().resetSession()
        useCohortStore().setCompactView(!!cohortId)
        useCohortStore().setModifiedSinceLastSearch(undefined)
        useContextStore().updateCurrentUserPreference(domain === 'admitted_students' ? 'admitSortBy' : 'sortBy', orderBy)
        useContextStore().updateCurrentUserPreference('termId', termId)

        if (cohortId) {
          loadCohort(cohortId, orderBy, termId).then(resolve)
        } else {
          if (domain) {
            useCohortStore().setDomain(domain)
          } else {
            throw new TypeError('\'domain\' is required when creating a new cohort.')
          }
          updateFilterOptions(useCohortStore().domain, useCohortStore().cohortOwner(), []).then(() => {
            useCohortStore().resetSession()
            useCohortStore().stashOriginalFilters()
            resolve()
          })
        }
      })
    },
    goToPage(page) {
      useContextStore().loadingStart()
      this.setPagination(page)
      this.onPageNumberChange().then(() => {
        scrollToTop()
        useContextStore().loadingComplete(this.getLoadedAlert())
      })
    },
    onChangeSortBy() {
      if (!useContextStore().loading) {
        this.goToPage(1)
      }
    },
    onChangeTerm() {
      if (!useContextStore().loading) {
        this.goToPage(this.pageNumber)
      }
    },
    onPageNumberChange() {
      return applyFilters(
        get(useContextStore().currentUser.preferences, this.sortByKey),
        get(useContextStore().currentUser.preferences, 'termId')
      )
    },
    resetFiltersToLastApply,
    resetPagination() {
      this.setPagination(1)
    },
    setPagination(page) {
      this.pageNumber = page
      useCohortStore().setCurrentPage(this.pageNumber)
    },
    toggleShowHistory(value) {
      this.showHistory = value
      if (value && !useCohortStore().isCompactView) {
        useCohortStore().toggleCompactView()
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
  border-left: 6px solid rgb(var(--v-theme-primary)) !important;
  min-height: 46px;
}
</style>
