<template>
  <div class="ma-5">
    <Spinner />
    <div v-if="!context.loading">
      <CohortPageHeader :show-history="showHistory" :toggle-show-history="toggleShowHistory" />
      <div v-if="cohort.domain === 'admitted_students' && cohort.students" class="pb-2">
        <AdmitDataWarning :updated-at="get(cohort.students, '[0].updatedAt')" />
      </div>
      <v-expand-transition>
        <v-card
          v-show="showFilters"
          id="show-hide-filters"
          class="overflow-visible pt-2"
          flat
          tile
        >
          <FilterRow
            v-for="(filter, index) in cohort.filters"
            :key="`${filter.key}-${index}`"
            :position="index"
          />
          <FilterRow v-if="cohort.isOwnedByCurrentUser" />
          <ApplyAndSaveButtons v-if="cohort.isOwnedByCurrentUser" />
        </v-card>
      </v-expand-transition>
      <SectionSpinner :loading="cohort.editMode === 'apply'" />
      <div v-if="!showHistory && showStudentsSection">
        <div class="d-flex flex-column flex-column-reverse flex-sm-row justify-space-between w-100 pt-4">
          <CuratedGroupSelector
            :context-description="cohort.domain === 'default' ? `Cohort ${cohort.cohortName || ''}` : `Admitted Students Cohort ${cohort.cohortName || ''}`"
            :domain="cohort.domain"
            :on-create-curated-group="resetFiltersToLastApply"
            :students="cohort.students"
          />
          <div class="d-flex flex-wrap justify-end">
            <TermSelector v-if="cohort.domain === 'default'" />
            <SortBy v-if="cohort.showSortBy" :domain="cohort.domain" />
          </div>
        </div>
        <hr class="mt-2 mb-0" />
        <div v-if="cohort.totalStudentCount > cohort.pagination.itemsPerPage" class="pt-1">
          <Pagination
            class="my-3"
            :click-handler="goToPage"
            :init-page-number="pageNumber"
            :limit="10"
            :per-page="cohort.pagination.itemsPerPage"
            :total-rows="cohort.totalStudentCount"
          />
          <hr class="mt-4 mb-0" />
        </div>
        <v-container v-if="cohort.domain === 'default'" id="cohort-students" class="px-3">
          <StudentRow
            v-for="(student, index) in cohort.students"
            :id="`student-${student.uid}`"
            :key="student.sid"
            class="border-right-0 list-group-item border-left-0 pl-0"
            :class="{'list-group-item-info': anchor === `#${student.uid}`}"
            list-type="cohort"
            :row-index="index"
            :sorted-by="context.currentUser.preferences.sortBy"
            :student="student"
            :term-id="context.currentUser.preferences.termId"
          />
        </v-container>
        <div v-if="cohort.domain === 'admitted_students'">
          <hr />
          <AdmitStudentsTable :include-curated-checkbox="true" :students="cohort.students" />
          <hr />
        </div>
        <Pagination
          v-if="cohort.totalStudentCount > cohort.pagination.itemsPerPage"
          :click-handler="goToPage"
          :index="1"
          :init-page-number="pageNumber"
          :limit="10"
          :per-page="cohort.pagination.itemsPerPage"
          :total-rows="cohort.totalStudentCount"
        />
      </div>
      <div v-if="showHistory">
        <CohortHistory />
      </div>
    </div>
  </div>
</template>

<script setup>
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
</script>

<script>
import {applyFilters, loadCohort, resetFiltersToLastApply, updateFilterOptions} from '@/stores/cohort-edit-session/utils'
import {get, size, startsWith} from 'lodash'
import {putFocusNextTick, scrollToTop, setPageTitle, toInt} from '@/lib/utils'
import {translateSortByOption} from '@/berkeley'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

export default {
  name: 'Cohort',
  data: () => ({
    cohort: undefined,
    context: undefined,
    pageNumber: undefined,
    showHistory: false
  }),
  computed: {
    anchor: () => location.hash,
    showFilters() {
      return !this.cohort.isCompactView
    },
    showStudentsSection() {
      return size(this.cohort.students) && this.cohort.editMode !== 'apply'
    },
    sortByKey() {
      return this.cohort.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
    }
  },
  watch: {
    domain(newVal) {
      this.context.removeEventHandler('admitSortBy-user-preference-change', this.onChangeSortBy)
      this.context.removeEventHandler('sortBy-user-preference-change', this.onChangeSortBy)
      this.context.setEventHandler(`${newVal === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, this.onChangeSortBy)
    }
  },
  mounted() {
    const forwardPath = window.history.state.forward
    const continueExistingSession = (startsWith(forwardPath, '/student') || startsWith(forwardPath, '/admit/student')) && size(this.cohort.filters)
    if (continueExistingSession) {
      this.pageNumber = this.cohort.pagination.currentPage
      setPageTitle(this.cohort.cohortName)
      this.context.loadingComplete(this.getLoadedAlert())
    } else {
      const cohortId = toInt(get(useRoute(), 'params.id'))
      const domain = useRoute().query.domain || 'default'
      const orderBy = get(this.context.currentUser.preferences, this.sortByKey)
      const termId = get(this.context.currentUser.preferences, 'termId')
      this.init(cohortId, domain, orderBy, termId).then(() => {
        this.pageNumber = this.cohort.pagination.currentPage
        const pageTitle = this.cohortId ? this.cohort.cohortName : 'Create Cohort'
        setPageTitle(pageTitle)
        this.context.loadingComplete(this.getLoadedAlert())
        putFocusNextTick(this.cohortId ? 'cohort-name' : 'create-cohort-h1')
      })
    }
  },
  created() {
    this.cohort = useCohortStore()
    this.context = useContextStore()
    this.context.setEventHandler(`${this.sortByKey}-user-preference-change`, this.onChangeSortBy)
    this.context.setEventHandler('cohort-apply-filters', this.resetPagination)
    this.context.setEventHandler('termId-user-preference-change', this.onChangeTerm)
  },
  unmounted() {
    this.context.removeEventHandler('admitSortBy-user-preference-change', this.onChangeSortBy)
    this.context.removeEventHandler('sortBy-user-preference-change', this.onChangeSortBy)
    this.context.removeEventHandler('cohort-apply-filters', this.resetPagination)
    this.context.removeEventHandler('termId-user-preference-change', this.onChangeTerm)
  },
  methods: {
    getLoadedAlert() {
      if (!this.cohortId) {
        return 'Create cohort page has loaded'
      } else {
        const sortByOption = translateSortByOption(get(this.context.currentUser.preferences, this.sortByKey))
        return `Cohort ${this.cohort.cohortName || ''}, sorted by ${sortByOption}, ${this.pageNumber > 1 ? `(page ${this.pageNumber})` : ''} has loaded`
      }
    },
    init(cohortId, domain, orderBy, termId) {
      return new Promise(resolve => {
        this.cohort.resetSession()
        this.cohort.setCompactView(!!cohortId)
        this.cohort.setModifiedSinceLastSearch(undefined)
        this.context.updateCurrentUserPreference(domain === 'admitted_students' ? 'admitSortBy' : 'sortBy', orderBy)
        this.context.updateCurrentUserPreference('termId', termId)

        if (cohortId) {
          loadCohort(cohortId, orderBy, termId).then(resolve)
        } else {
          if (domain) {
            this.cohort.setDomain(domain)
          } else {
            throw new TypeError('\'domain\' is required when creating a new cohort.')
          }
          updateFilterOptions(this.cohort.domain, this.cohort.cohortOwner, []).then(() => {
            this.cohort.resetSession()
            this.cohort.stashOriginalFilters()
            resolve()
          })
        }
      })
    },
    goToPage(page) {
      this.context.loadingStart()
      this.setPagination(page)
      this.onPageNumberChange().then(() => {
        scrollToTop()
        this.context.loadingComplete(this.getLoadedAlert())
      })
    },
    onChangeSortBy() {
      if (!this.context.loading) {
        this.goToPage(1)
      }
    },
    onChangeTerm() {
      if (!this.context.loading) {
        this.goToPage(this.pageNumber)
      }
    },
    onPageNumberChange() {
      return applyFilters(
        get(this.context.currentUser.preferences, this.sortByKey),
        get(this.context.currentUser.preferences, 'termId')
      )
    },
    resetPagination() {
      this.setPagination(1)
    },
    setPagination(page) {
      this.pageNumber = page
      this.cohort.setCurrentPage(this.pageNumber)
    },
    toggleShowHistory(value) {
      this.showHistory = value
      if (value && !this.cohort.isCompactView) {
        this.cohort.toggleCompactView()
      }
      if (!value) {
        this.onPageNumberChange().then(scrollToTop)
      }
    }
  }
}
</script>
