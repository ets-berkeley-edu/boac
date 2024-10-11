<template>
  <div v-if="!contextStore.loading" class="default-margins">
    <CohortPageHeader :is-cohort-history-page="false" />
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
    <div v-if="size(cohortStore.students) && cohortStore.editMode !== 'apply'">
      <div class="align-center d-flex flex-column flex-column-reverse flex-sm-row justify-space-between w-100 pt-2">
        <CuratedGroupSelector
          class="mr-auto"
          :context-description="cohortStore.domain === 'default' ? `Cohort ${cohortStore.cohortName || ''}` : `Admitted Students Cohort ${cohortStore.cohortName || ''}`"
          :domain="cohortStore.domain"
          :on-create-curated-group="resetFiltersToLastApply"
          :students="cohortStore.students"
        />
        <div class="d-flex flex-wrap justify-end pr-3">
          <TermSelector v-if="cohortStore.domain === 'default'" class="mb-1" />
          <SortBy
            v-if="cohortStore.showSortBy"
            class="ml-5 mb-1"
            :domain="cohortStore.domain"
          />
        </div>
      </div>
      <div v-if="cohortStore.totalStudentCount > cohortStore.pagination.itemsPerPage" :class="{'mt-6': cohortStore.domain === 'default'}">
        <Pagination
          class="my-3"
          :click-handler="goToPage"
          :init-page-number="cohortStore.pagination.currentPage"
          :limit="10"
          :per-page="cohortStore.pagination.itemsPerPage"
          :total-rows="cohortStore.totalStudentCount"
        />
      </div>
      <hr class="my-4" />
      <v-container
        v-if="cohortStore.domain === 'default'"
        id="cohort-students"
        class="pl-3 scroll-margins"
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
          :init-page-number="cohortStore.pagination.currentPage"
          :is-widget-at-bottom-of-page="true"
          :limit="10"
          :per-page="cohortStore.pagination.itemsPerPage"
          :total-rows="cohortStore.totalStudentCount"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdmitStudentsTable from '@/components/admit/AdmitStudentsTable'
import ApplyAndSaveButtons from '@/components/cohort/ApplyAndSaveButtons'
import CohortPageHeader from '@/components/cohort/CohortPageHeader'
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector'
import FilterRow from '@/components/cohort/FilterRow'
import Pagination from '@/components/util/Pagination'
import SortBy from '@/components/student/SortBy'
import StudentRow from '@/components/student/StudentRow'
import TermSelector from '@/components/student/TermSelector'
import {applyFilters, loadCohort, resetFiltersToLastApply, updateFilterOptions} from '@/stores/cohort-edit-session/utils'
import {computed, onMounted, onUnmounted, reactive, watch} from 'vue'
import {get, size, startsWith} from 'lodash'
import {nextTick} from 'vue'
import {putFocusNextTick, setPageTitle, toInt} from '@/lib/utils'
import {translateSortByOption} from '@/berkeley'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const cohortStore = useCohortStore()
const contextStore = useContextStore()
const currentUser = reactive(contextStore.currentUser)

contextStore.loadingStart()

const anchor = computed(() => window.location)
const pageLoadAlert = computed(() => {
  const loadStatus = contextStore.loading ? 'has loaded' : 'is loading'
  if (!cohortStore.cohortId) {
    return `Create cohort page ${loadStatus}`
  } else {
    const sortByOption = translateSortByOption(get(currentUser.preferences, sortByKey.value))
    const page = cohortStore.pagination.currentPage
    const pageDesc = page > 1 ? `(page ${page})` : ''
    return `Cohort ${cohortStore.cohortName || ''} ${pageDesc} ${loadStatus}. Sorted by ${sortByOption}.`
  }
})
const sortByKey = computed(() => cohortStore.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy')

watch(() => cohortStore.domain, value => {
  contextStore.removeEventHandler('admitSortBy-user-preference-change')
  contextStore.removeEventHandler('sortBy-user-preference-change')
  contextStore.setEventHandler(
    `${value === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`,
    () => goToPage(1)
  )
})

onMounted(() => {
  contextStore.setEventHandler(
    `${sortByKey.value}-user-preference-change`,
    () => goToPage(1)
  )
  contextStore.setEventHandler(
    'cohort-apply-filters',
    () => cohortStore.setCurrentPage(1)
  )
  contextStore.setEventHandler(
    'termId-user-preference-change',
    () => goToPage(cohortStore.pagination.currentPage)
  )
  const refererURI = window.history.state.forward
  const isBackButtonToCohort = (startsWith(refererURI, '/student') || startsWith(refererURI, '/admit/student')) && size(cohortStore.filters)
  const focusElementId = getFocusElementId(isBackButtonToCohort)
  if (isBackButtonToCohort) {
    contextStore.loadingComplete(pageLoadAlert.value)
    afterLoadingComplete(focusElementId)
  } else {
    const cohortId = toInt(get(useRoute(), 'params.id'))
    const domain = useRoute().query.domain || 'default'
    const orderBy = get(currentUser.preferences, sortByKey.value)
    const termId = get(currentUser.preferences, 'termId')
    init(cohortId, domain, orderBy, termId).then(() => {
      contextStore.loadingComplete(pageLoadAlert.value)
      afterLoadingComplete(focusElementId)
    })
  }
})

onUnmounted(() => {
  contextStore.removeEventHandler('admitSortBy-user-preference-change')
  contextStore.removeEventHandler('sortBy-user-preference-change')
  contextStore.removeEventHandler('cohort-apply-filters')
  contextStore.removeEventHandler('termId-user-preference-change')
})

const afterLoadingComplete = focusId => {
  const pageTitle = cohortStore.cohortId ? cohortStore.cohortName : 'Create Cohort'
  setPageTitle(pageTitle)
  nextTick(() => putFocusNextTick(focusId, {scrollBlock: 'start'}))
}

const getFocusElementId = isBackButtonToCohort => {
  const refererURI = window.history.state.forward
  let focusId = 'page-header'
  if (isBackButtonToCohort) {
    const matches = refererURI.match(/\d+$/)
    if (matches) {
      focusId = `student-${matches[0]}`
    }
  }
  return focusId
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
  return new Promise(resolve => {
    if (contextStore.loading) {
      resolve()
    } else {
      cohortStore.setCurrentPage(page)
      contextStore.loadingStart(pageLoadAlert.value)
      return onPageNumberChange().then(() => {
        afterLoadingComplete(getFocusElementId(false))
        contextStore.loadingComplete(pageLoadAlert.value)
      }).then(resolve)
    }
  })
}

const onPageNumberChange = () => {
  return applyFilters(
    get(currentUser.preferences, sortByKey.value),
    get(currentUser.preferences, 'termId')
  )
}
</script>
