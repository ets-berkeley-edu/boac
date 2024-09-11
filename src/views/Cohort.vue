<template>
  <div v-if="!contextStore.loading" class="default-margins">
    <CohortPageHeader :show-history="showHistory" :toggle-show-history="toggleShowHistory" />
    <div v-if="cohortStore.domain === 'admitted_students' && cohortStore.students">
      <AdmitDataWarning :updated-at="get(cohortStore.students, '[0].updatedAt')" />
    </div>
    <v-expand-transition>
      <div v-if="!cohortStore.isCompactView">
        <FilterRow
          v-for="(filter, index) in cohortStore.filters"
          :key="`${filter.key}-${index}`"
          :position="index"
        />
        <FilterRow v-if="cohortStore.isOwnedByCurrentUser" />
        <ApplyAndSaveButtons v-if="cohortStore.isOwnedByCurrentUser" />
      </div>
    </v-expand-transition>
    <div v-if="!showHistory && size(cohortStore.students) && cohortStore.editMode !== 'apply'">
      <div class="align-center d-flex flex-column flex-column-reverse flex-sm-row justify-space-between w-100 pt-2">
        <CuratedGroupSelector
          :class="{'mt-2': $vuetify.display.smAndDown}"
          :context-description="cohortStore.domain === 'default' ? `Cohort ${cohortStore.cohortName || ''}` : `Admitted Students Cohort ${cohortStore.cohortName || ''}`"
          :domain="cohortStore.domain"
          :on-create-curated-group="resetFiltersToLastApply"
          :students="cohortStore.students"
        />
        <div class="d-flex flex-wrap justify-end pr-3">
          <TermSelector v-if="cohortStore.domain === 'default'" />
          <SortBy
            v-if="cohortStore.showSortBy"
            class="lr-5"
            :class="{'mt-2': $vuetify.display.smAndDown}"
            :domain="cohortStore.domain"
          />
        </div>
      </div>
      <div v-if="cohortStore.totalStudentCount > cohortStore.pagination.itemsPerPage" :class="{'mt-6': cohortStore.domain === 'default'}">
        <Pagination
          class="my-3"
          :click-handler="goToPage"
          :init-page-number="pageNumber"
          :limit="10"
          :per-page="cohortStore.pagination.itemsPerPage"
          :total-rows="cohortStore.totalStudentCount"
        />
      </div>
      <hr class="my-4" />
      <v-container
        v-if="cohortStore.domain === 'default'"
        id="cohort-students"
        class="pl-3"
        fluid
      >
        <StudentRow
          v-for="(student, index) in cohortStore.students"
          :id="`student-${student.uid}`"
          :key="student.sid"
          :class="{'list-group-item-info': anchor === `#${student.uid}`}"
          list-type="cohort"
          :row-index="index"
          :sorted-by="currentUser.preferences.sortBy"
          :student="student"
          :term-id="currentUser.preferences.termId"
        />
      </v-container>
      <div v-if="cohortStore.domain === 'admitted_students'">
        <AdmitStudentsTable :include-curated-checkbox="true" :students="cohortStore.students" />
        <hr />
      </div>
      <div class="mt-3">
        <Pagination
          v-if="cohortStore.totalStudentCount > cohortStore.pagination.itemsPerPage"
          :click-handler="goToPage"
          id-prefix="auxiliary-pagination"
          :init-page-number="pageNumber"
          :limit="10"
          :per-page="cohortStore.pagination.itemsPerPage"
          :total-rows="cohortStore.totalStudentCount"
        />
      </div>
    </div>
    <div v-if="showHistory">
      <CohortHistory />
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
import SortBy from '@/components/student/SortBy'
import StudentRow from '@/components/student/StudentRow'
import TermSelector from '@/components/student/TermSelector'
import {applyFilters, loadCohort, resetFiltersToLastApply, updateFilterOptions} from '@/stores/cohort-edit-session/utils'
import {computed, onMounted, onUnmounted, reactive, ref, watch} from 'vue'
import {get, size, startsWith} from 'lodash'
import {putFocusNextTick, scrollToTop, setPageTitle, toInt} from '@/lib/utils'
import {translateSortByOption} from '@/berkeley'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const cohortStore = useCohortStore()
const contextStore = useContextStore()
const currentUser = reactive(contextStore.currentUser)
const pageNumber = ref(undefined)
const showHistory = ref(false)

contextStore.loadingStart()

const anchor = computed(() => window.location)
const sortByKey = computed(() => cohortStore.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy')

watch(() => cohortStore.domain, value => {
  contextStore.removeEventHandler('admitSortBy-user-preference-change', onChangeSortBy)
  contextStore.removeEventHandler('sortBy-user-preference-change', onChangeSortBy)
  contextStore.setEventHandler(`${value === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, onChangeSortBy)
})

onMounted(() => {
  contextStore.setEventHandler(`${sortByKey.value}-user-preference-change`, onChangeSortBy)
  contextStore.setEventHandler('cohort-apply-filters', resetPagination)
  contextStore.setEventHandler('termId-user-preference-change', onChangeTerm)
  const forwardPath = window.history.state.forward
  const continueExistingSession = (startsWith(forwardPath, '/student') || startsWith(forwardPath, '/admit/student')) && size(cohortStore.filters)
  if (continueExistingSession) {
    pageNumber.value = cohortStore.pagination.currentPage
    setPageTitle(cohortStore.cohortName)
    contextStore.loadingComplete(getLoadedAlert())
  } else {
    const cohortId = toInt(get(useRoute(), 'params.id'))
    const domain = useRoute().query.domain || 'default'
    const orderBy = get(currentUser.preferences, sortByKey.value)
    const termId = get(currentUser.preferences, 'termId')
    init(cohortId, domain, orderBy, termId).then(() => {
      pageNumber.value = cohortStore.pagination.currentPage
      const pageTitle = cohortId ? cohortStore.cohortName : 'Create Cohort'
      setPageTitle(pageTitle)
      contextStore.loadingComplete(getLoadedAlert())
      putFocusNextTick(cohortId ? 'cohort-name' : 'create-cohort-h1')
    })
  }
})

onUnmounted(() => {
  contextStore.removeEventHandler('admitSortBy-user-preference-change', onChangeSortBy)
  contextStore.removeEventHandler('sortBy-user-preference-change', onChangeSortBy)
  contextStore.removeEventHandler('cohort-apply-filters', resetPagination)
  contextStore.removeEventHandler('termId-user-preference-change', onChangeTerm)
})

const getLoadedAlert = () => {
  if (!cohortStore.cohortId) {
    return 'Create cohort page has loaded'
  } else {
    const sortByOption = translateSortByOption(get(currentUser.preferences, sortByKey.value))
    return `Cohort ${cohortStore.cohortName || ''}, sorted by ${sortByOption}, ${pageNumber.value > 1 ? `(page ${pageNumber.value})` : ''} has loaded`
  }
}

const init = (cohortId, domain, orderBy, termId) => {
  return new Promise(resolve => {
    cohortStore.resetSession()
    cohortStore.setCompactView(!!cohortId)
    cohortStore.setModifiedSinceLastSearch(undefined)
    contextStore.updateCurrentUserPreference(domain === 'admitted_students' ? 'admitSortBy' : 'sortBy', orderBy)
    contextStore.updateCurrentUserPreference('termId', termId)

    if (cohortId) {
      loadCohort(cohortId, orderBy, termId).then(resolve)
    } else {
      if (domain) {
        cohortStore.setDomain(domain)
      } else {
        throw new TypeError('\'domain\' is required when creating a new cohort.')
      }
      updateFilterOptions(cohortStore.domain, cohortStore.cohortOwner, []).then(() => {
        cohortStore.resetSession()
        cohortStore.stashOriginalFilters()
        resolve()
      })
    }
  })
}

const goToPage = page => {
  contextStore.loadingStart()
  setPagination(page)
  onPageNumberChange().then(() => {
    scrollToTop()
    contextStore.loadingComplete(getLoadedAlert())
  })
}

const onChangeSortBy = () => {
  if (!contextStore.loading) {
    goToPage(1)
  }
}

const onChangeTerm = () => {
  if (!contextStore.loading) {
    goToPage(pageNumber.value)
  }
}

const onPageNumberChange = () => {
  return applyFilters(
    get(currentUser.preferences, sortByKey.value),
    get(currentUser.preferences, 'termId')
  )
}

const resetPagination = () => setPagination(1)

const setPagination = page => {
  pageNumber.value = page
  cohortStore.setCurrentPage(pageNumber.value)
}

const toggleShowHistory = value => {
  showHistory.value = value
  if (value && !cohortStore.isCompactView) {
    cohortStore.toggleCompactView()
  }
  if (!value) {
    putFocusNextTick('show-cohort-history-button')
    onPageNumberChange().then(scrollToTop)
  }
}
</script>
