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
    const filters = useCohortStore().filters
    if (size(filters)) {
      useCohortStore().setEditMode('apply')
      const cohortId: number = Number(useCohortStore().cohortId)
      const isOwnedByCurrentUser: boolean = Boolean(useCohortStore().isOwnedByCurrentUser)
      const pagination: any = useCohortStore().pagination
      const limit: number = pagination.itemsPerPage
      const offset: number = (pagination.currentPage - 1) * limit
      const isReadOnly: boolean = !!cohortId && !isOwnedByCurrentUser

      const done = data => {
        useCohortStore().updateStudents({students: data.students, totalStudentCount: data.totalStudentCount})
        useCohortStore().stashOriginalFilters()
        useCohortStore().setEditMode(null)
        resolve()
      }
      if (isReadOnly) {
        getCohort(cohortId, true, limit, offset, orderBy, termId).then(done)
      } else {
        const domain = String(useCohortStore().domain)
        getStudentsPerFilters(domain, filters, orderBy, termId, offset, limit).then(done)
      }
    } else {
      resolve()
    }
  })
}

export function loadCohort(cohortId: number, orderBy: string, termId: string) {
  return new Promise<void>(resolve => {
    const pagination: any = useCohortStore().pagination
    getCohort(
      cohortId,
      true,
      pagination.itemsPerPage,
      0,
      orderBy,
      termId
    ).then(cohort => {
      if (cohort) {
        useCohortStore().setDomain(cohort.domain)
        const owner = cohort.isOwnedByCurrentUser ? 'me' : get(cohort, 'owner.uid')
        translateToFilterOptions(cohort.domain, owner, cohort.criteria).then((filters: any[]) => {
          useCohortStore().updateSession(cohort, filters, cohort.students, cohort.totalStudentCount)
          useCohortStore().stashOriginalFilters()
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
    useCohortStore().restoreOriginalFilters()
    useCohortStore().setEditMode(null)
    useCohortStore().setModifiedSinceLastSearch(false)

    const cohortOwner = useCohortStore().cohortOwner()
    const domain = String(useCohortStore().domain)
    const filters = useCohortStore().filters
    updateFilterOptions(domain, cohortOwner, filters).then(resolve)
  })
}
