import {getCohort, getCohortFilterOptions, getStudentsPerFilters, translateToFilterOptions} from '@/api/cohort'
import {get, size} from 'lodash'
import {useCohortStore} from '@/stores/cohort-edit-session/index'

export function updateFilterOptions(domain: string, owner: string | undefined, existingFilters: any[]) {
  return new Promise<void>(resolve => {
    getCohortFilterOptions(domain, owner, existingFilters).then((data: any) => {
      useCohortStore().updateFilterOptions(data)
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
      const pagination: any = cohortStore.pagination
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
        getCohort(cohortId, true, limit, offset, orderBy, termId).then(done)
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
    const pagination: any = cohortStore.pagination
    getCohort(
      cohortId,
      true,
      pagination.itemsPerPage,
      0,
      orderBy,
      termId
    ).then(cohort => {
      if (cohort) {
        cohortStore.setDomain(cohort.domain)
        const owner = cohort.isOwnedByCurrentUser ? 'me' : get(cohort, 'owner.uid')
        translateToFilterOptions(cohort.domain, owner, cohort.criteria).then((filters: any[]) => {
          cohortStore.updateSession(cohort, filters, cohort.students, cohort.totalStudentCount)
          cohortStore.stashOriginalFilters()
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
    const cohortStore = useCohortStore()
    cohortStore.restoreOriginalFilters()
    cohortStore.setEditMode(null)
    cohortStore.setModifiedSinceLastSearch(false)

    const cohortOwner = cohortStore.cohortOwner
    const domain = String(cohortStore.domain)
    const filters = cohortStore.filters
    updateFilterOptions(domain, cohortOwner, filters).then(resolve)
  })
}
