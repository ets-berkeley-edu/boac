import {get, size} from 'lodash'
import type {Pagination} from '@/lib/types'
import {getCohort, getStudentsPerFilters} from '@/api/cohort'
import {getCohortFilterCategories, translateToFilterOptions} from '@/api/cohort-filter-options'
import {useCohortStore} from '@/stores/cohort-edit-session/index'
import {useContextStore} from '@/stores/context'

export function updateFilterOptions(domain: string, ownerUid: string | undefined, existingFilters: object[]) {
  return new Promise<void>(resolve => {
    getCohortFilterCategories(domain, ownerUid, existingFilters).then((data: object) => {
      useCohortStore().setFilterCategories(data)
      resolve()
    })
  })
}

export function applyFilters(orderBy: string, termId: string) {
  return new Promise<void>(resolve => {
    const cohortStore = useCohortStore()
    const filters = cohortStore.filters
    if (size(filters)) {
      cohortStore.setEditMode('apply')
      const cohortId: number = Number(cohortStore.cohortId)
      const isOwnedByCurrentUser: boolean = Boolean(cohortStore.isOwnedByCurrentUser)
      const pagination: Pagination = cohortStore.pagination
      const limit: number = pagination.itemsPerPage
      const offset: number = (pagination.currentPage - 1) * limit
      const isReadOnly: boolean = !!cohortId && !isOwnedByCurrentUser
      const done = data => {
        cohortStore.updateStudents({students: data.students, totalStudentCount: data.totalStudentCount})
        cohortStore.stashOriginalFilters()
        cohortStore.setEditMode(null)
        resolve()
      }
      if (isReadOnly) {
        getCohort(cohortId, termId, true, limit, offset, orderBy).then(done)
      } else {
        const domain = String(cohortStore.domain)
        getStudentsPerFilters(domain, filters, orderBy, termId, offset, limit).then(done)
      }
    } else {
      resolve()
    }
  })
}

export function loadCohort(cohortId: number, orderBy: string, termId: string) {
  return new Promise<void>(resolve => {
    const cohortStore = useCohortStore()
    const pagination: Pagination = cohortStore.pagination
    getCohort(
      cohortId,
      termId,
      true,
      pagination.itemsPerPage,
      0,
      orderBy
    ).then(cohort => {
      if (cohort) {
        cohortStore.setDomain(cohort.domain)
        const ownerUid = get(cohort.owner, 'uid') || useContextStore().currentUser.uid
        translateToFilterOptions(cohort.domain, ownerUid, cohort.criteria).then((filters: object[]) => {
          cohortStore.updateSession(cohort, filters, cohort.students, cohort.totalStudentCount)
          cohortStore.stashOriginalFilters()
          updateFilterOptions(cohort.domain, ownerUid, filters).then(resolve)
        })
      } else {
        throw new TypeError(`Cohort ${cohortId} not found.`)
      }
    })
  })
}

export function resetFiltersToLastApply() {
  return new Promise(resolve => {
    const cohortStore = useCohortStore()
    cohortStore.restoreOriginalFilters()
    cohortStore.setEditMode(null)
    if (cohortStore.originalFilters.length) {
      cohortStore.setModifiedSinceLastSearch(false)
    } else {
      cohortStore.setModifiedSinceLastSearch(undefined)
    }

    const domain = String(cohortStore.domain)
    const filters = cohortStore.filters
    const ownerUid = get(cohortStore.owner, 'uid') || useContextStore().currentUser.uid
    updateFilterOptions(domain, ownerUid, filters).then(resolve)
  })
}
