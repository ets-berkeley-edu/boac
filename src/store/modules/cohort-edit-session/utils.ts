import store from '@/store'
import {getCohort, getCohortFilterOptions, getStudentsPerFilters, translateToFilterOptions} from '@/api/cohort'
import {get, size} from 'lodash'

export function updateFilterOptions(domain: string, owner: string, existingFilters: any[]) {
  return new Promise<void>(resolve => {
    getCohortFilterOptions(domain, owner, existingFilters).then(data => {
      store.commit('cohort/updateFilterOptions', data)
      resolve()
    })
  })
}

export function applyFilters(orderBy: string, termId: string) {
  return new Promise<void>(resolve => {
    const filters = store.getters['cohort/filters']
    if (size(filters)) {
      store.commit('cohort/setEditMode', 'apply')
      const cohortId: number = store.getters['cohort/cohortId']
      const isOwnedByCurrentUser: boolean = store.getters['cohort/isOwnedByCurrentUser']
      const pagination: any = store.getters['cohort/pagination']
      const limit: number = pagination.itemsPerPage
      const offset: number = (pagination.currentPage - 1) * limit
      const isReadOnly: boolean = !!cohortId && !isOwnedByCurrentUser

      const done = data => {
        store.commit('cohort/updateStudents', {
          students: data.students,
          totalStudentCount: data.totalStudentCount
        })
        store.commit('cohort/stashOriginalFilters')
        store.commit('cohort/setEditMode', null)
        resolve()
      }
      if (isReadOnly) {
        getCohort(cohortId, true, limit, offset, orderBy, termId).then(done)
      } else {
        const domain = store.getters['cohort/domain']
        getStudentsPerFilters(domain, filters, orderBy, termId, offset, limit).then(done)
      }
    } else {
      resolve()
    }
  })
}

export function loadCohort(cohortId: number, orderBy: string, termId: string) {
  return new Promise<void>(resolve => {
    const pagination: any = store.getters['cohort/pagination']
    getCohort(
      cohortId,
      true,
      pagination.itemsPerPage,
      0,
      orderBy,
      termId
    ).then(cohort => {
      if (cohort) {
        store.commit('cohort/setDomain', cohort.domain)
        const owner = cohort.isOwnedByCurrentUser ? 'me' : get(cohort, 'owner.uid')
        translateToFilterOptions(cohort.domain, owner, cohort.criteria).then(filters => {
          store.commit('cohort/updateSession', {
            cohort,
            filters: filters,
            students: cohort.students,
            totalStudentCount: cohort.totalStudentCount
          })
          store.commit('cohort/stashOriginalFilters')
          updateFilterOptions(cohort.domain, owner, filters).then(resolve)
        })
      } else {
        throw new TypeError(`Cohort ${cohortId} not found.`)
      }
    })
  })
}

export function resetFiltersToLastApply() {
  return new Promise(resolve => {
    store.commit('cohort/restoreOriginalFilters')
    store.commit('cohort/setEditMode', null)
    store.commit('cohort/setModifiedSinceLastSearch', false)

    const cohortOwner = store.getters['cohort/cohortOwner']
    const domain = store.getters['cohort/domain']
    const filters = store.getters['cohort/filters']
    updateFilterOptions(domain, cohortOwner, filters).then(resolve)
  })
}
