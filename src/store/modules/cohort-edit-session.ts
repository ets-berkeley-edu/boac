import _ from 'lodash'
import router from '@/router'
import store from '@/store'
import {
  createCohort,
  downloadCohortCsv,
  downloadCsv,
  getCohort,
  saveCohort,
  translateToFilterOptions
} from '@/api/cohort'
import {updateFilterOptions} from '@/store/utils/cohort'

const EDIT_MODE_TYPES = ['add', 'apply', 'edit-[0-9]+', 'rename']

const state = {
  cohortId: undefined,
  cohortName: undefined,
  cohortOwnerUid: undefined,
  domain: undefined,
  editMode: undefined,
  filterOptionGroups: undefined,
  filters: undefined,
  isCompactView: undefined,
  isModifiedSinceLastSearch: undefined,
  isOwnedByCurrentUser: undefined,
  orderBy: undefined,
  originalFilters: undefined,
  pagination: {
    currentPage: undefined,
    itemsPerPage: 50
  },
  students: undefined,
  termId: undefined,
  totalStudentCount: undefined
}

const getters = {
  cohortId: (state: any): number => state.cohortId,
  cohortName: (state: any): string => state.cohortName,
  cohortOwner: (state: any) => state.isOwnedByCurrentUser ? 'me' : state.cohortOwnerUid,
  domain: (state: any) => state.domain,
  editMode: (state: any) => state.editMode,
  filterOptionGroups: (state: any): any[] => state.filterOptionGroups,
  filters: (state: any): any[] => state.filters,
  isCompactView: (state: any): boolean => state.isCompactView,
  isModifiedSinceLastSearch: (state: any): boolean => state.isModifiedSinceLastSearch,
  isOwnedByCurrentUser: (state: any): boolean => state.isOwnedByCurrentUser,
  pagination: (state: any) => state.pagination,
  showApplyButton: (state: any) => state.isModifiedSinceLastSearch === true && !!_.size(state.filters),
  showSaveButton: (state: any): boolean => state.isModifiedSinceLastSearch === false,
  showSortBy: (state: any) =>!state.isModifiedSinceLastSearch && state.totalStudentCount > 1,
  students: (state: any): any[] => state.students,
  totalStudentCount: (state: any): number => state.totalStudentCount
}

const mutations = {
  addFilter: (state: any, filter: any) => {
    state.filters.push(filter)
    state.isModifiedSinceLastSearch = true
  },
  setCompactView: (state: any, compactView: boolean) => state.isCompactView = compactView,
  setEditMode(state: any, editMode: string) {
    if (_.isNil(editMode)) {
      state.editMode = null
    } else if (_.find(EDIT_MODE_TYPES, type => editMode.match(type))) {
      // Valid mode
      state.editMode = editMode
    } else {
      throw new TypeError('Invalid page mode: ' + editMode)
    }
  },
  removeFilter: (state: any, index: number) => {
    state.filters.splice(index, 1)
    state.isModifiedSinceLastSearch = true
  },
  renameCohort: (state: any, name: string) => (state.cohortName = name),
  resetSession: (state: any) => {
    state.editMode = undefined
    state.cohortId = undefined
    state.cohortName = undefined
    state.cohortOwnerUid = undefined
    state.isModifiedSinceLastSearch = true
    state.isOwnedByCurrentUser = true
    state.filters = []
    state.students = undefined
    state.totalStudentCount = undefined
    state.pagination.currentPage = 1
  },
  updatedSession: (state: any, {cohort, filters, students, totalStudentCount}) => {
    state.editMode = null
    state.cohortId = cohort && cohort.id
    state.cohortName = cohort && cohort.name
    state.cohortOwnerUid = cohort && cohort.owner && cohort.owner.uid
    state.isOwnedByCurrentUser = !cohort || cohort.isOwnedByCurrentUser
    state.filters = filters || []
    state.students = students
    state.totalStudentCount = totalStudentCount
    state.pagination.currentPage = 1
    if (!state.cohortId) {
      // If cohortId is null then show 'Save Cohort' for unsaved search results
      state.isModifiedSinceLastSearch = true
    }
  },
  restoreOriginalFilters: (state: any) => state.filters = _.cloneDeep(state.originalFilters),
  setCurrentPage: (state: any, currentPage: number) => state.pagination.currentPage = currentPage,
  setDomain: (state: any, domain: string) => state.domain = domain,
  setModifiedSinceLastSearch: (state: any, value: boolean) => state.isModifiedSinceLastSearch = value,
  // Store an unmodified copy of the most recently applied filters in case of cancellation.
  stashOriginalFilters: (state: any) => state.originalFilters = _.cloneDeep(state.filters),
  toggleCompactView: (state: any) => state.isCompactView = !state.isCompactView,
  updateFilterOptions: (state: any, filterOptionGroups: any[]) => state.filterOptionGroups = filterOptionGroups,
  updateStudents: (state: any, {students, totalStudentCount}) => {
    state.students = students
    state.totalStudentCount = totalStudentCount
  },
  updateExistingFilter: (state: any, {index, updatedFilter}) => {
    state.filters[index] = updatedFilter
    state.isModifiedSinceLastSearch = true
  }
}

const actions = {
  addFilter: ({commit, state}, filter: any) => {
    return new Promise(resolve => {
      commit('addFilter', filter)
      commit('setModifiedSinceLastSearch', true)
      updateFilterOptions(state.domain, getters.cohortOwner(state), state.filters).then(resolve)
    })
  },
  createCohort: ({commit, state}, name: string) => {
    return new Promise<void>(resolve => {
      createCohort(state.domain, name, state.filters).then(
        cohort => {
          commit('updatedSession', {
            cohort,
            filters: state.filters,
            students: state.students,
            totalStudentCount: cohort.totalStudentCount
          })
          commit('stashOriginalFilters')
          commit('setModifiedSinceLastSearch', null)
          resolve()
        }
      )
    })
  },
  downloadCsvPerFilters: ({state}, csvColumnsSelected: any) => {
    return new Promise(resolve => {
      const isReadOnly = state.cohortId && !state.isOwnedByCurrentUser
      if (isReadOnly) {
        downloadCohortCsv(state.cohortId, state.cohortName, csvColumnsSelected).then(resolve)
      } else {
        downloadCsv(state.domain, state.cohortName, state.filters, csvColumnsSelected).then(resolve)
      }
    })
  },
  loadCohort: ({commit, state}, {id, orderBy, termId} ) => {
    return new Promise(resolve => {
      getCohort(id, true, state.pagination.itemsPerPage, 0, orderBy, termId).then(cohort => {
        if (cohort) {
          commit('setDomain', cohort.domain)
          const owner = cohort.isOwnedByCurrentUser ? 'me' : _.get(cohort, 'owner.uid')
          translateToFilterOptions(state.domain, owner, cohort.criteria).then(filters => {
            commit('updatedSession', {
              cohort,
              filters: filters,
              students: cohort.students,
              totalStudentCount: cohort.totalStudentCount
            })
            commit('stashOriginalFilters')
            updateFilterOptions(state.domain, owner, filters).then(resolve)
          })
        } else {
          router.push({path: '/404'})
        }
      })
    })
  },
  renameCohort: ({commit, state}, name: string) => {
    return new Promise(resolve => {
      commit('renameCohort', name)
      saveCohort(
        state.cohortId,
        state.cohortName,
        state.filters
      ).then(resolve)
    })
  },
  removeFilter: ({commit, state}, index: number) => {
    return new Promise(resolve => {
      commit('removeFilter', index)
      commit('setModifiedSinceLastSearch', true)
      updateFilterOptions(state.domain, getters.cohortOwner(state), state.filters).then(resolve)
    })
  },
  resetFiltersToLastApply: ({commit, state}) => {
    return new Promise(resolve => {
      commit('restoreOriginalFilters')
      commit('setEditMode', null)
      commit('setModifiedSinceLastSearch', false)
      updateFilterOptions(state.domain, getters.cohortOwner(state), state.filters).then(resolve)
    })
  },
  resetFiltersToSaved: ({commit, state}, cohortId) => {
    commit('setCurrentPage', 0)
    commit('setModifiedSinceLastSearch', null)
    commit('setEditMode', 'apply')
    return new Promise<void>(resolve => {
      store.dispatch('cohort/loadCohort', {
        id: cohortId,
        orderBy: state.orderBy,
        termId: state.termId
      }).then(() => {
        commit('setEditMode', null)
        resolve()
      })
    })
  },
  saveExistingCohort: ({commit, state}) => {
    return new Promise<void>(resolve => {
      saveCohort(
        state.cohortId,
        state.cohortName,
        state.filters
      ).then(() => {
        commit('setModifiedSinceLastSearch', null)
        resolve()
      })
    })
  },
  updateExistingFilter: ({commit, state}, {index, updatedFilter}: any) => {
    return new Promise(resolve => {
      commit('updateExistingFilter', {index, updatedFilter})
      commit('setModifiedSinceLastSearch', true)
      updateFilterOptions(state.domain, getters.cohortOwner(state), state.filters).then(resolve)
    })
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
