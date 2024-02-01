import store from '@/store'
import {getCohort, getCohortFilterOptions, getStudentsPerFilters} from '@/api/cohort'
import {get} from 'lodash'

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
    const cohortId = store.getters['cohort/cohortId']
    const domain = store.getters['cohort/domain']
    const filters = store.getters['cohort/filters']
    const isOwnedByCurrentUser = store.getters['cohort/isOwnedByCurrentUser']

    const pagination = store.getters['cohort/pagination']
    if (!get(filters, 'length')) {
      return resolve()
    }
    store.commit('cohort/setEditMode', 'apply')
    const limit = pagination.itemsPerPage
    const offset = (pagination.currentPage - 1) * limit
    const done = data => {
      store.commit('cohort/updateStudents', {
        students: data.students,
        totalStudentCount: data.totalStudentCount
      })
      store.commit('cohort/stashOriginalFilters')
      store.commit('cohort/setEditMode', null)
      resolve()
    }
    const isReadOnly = cohortId && !isOwnedByCurrentUser
    if (isReadOnly) {
      getCohort(cohortId, true, limit, offset, orderBy, termId).then(done)
    } else {
      getStudentsPerFilters(domain, filters, orderBy, termId, offset, limit).then(done)
    }
  })
}

