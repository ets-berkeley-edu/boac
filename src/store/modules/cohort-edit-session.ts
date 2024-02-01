import {cloneDeep, find, isNil, size} from 'lodash'

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
  showApplyButton: (state: any) => state.isModifiedSinceLastSearch === true && !!size(state.filters),
  showSaveButton: (state: any): boolean => state.isModifiedSinceLastSearch === false,
  showSortBy: (state: any) =>!state.isModifiedSinceLastSearch && state.totalStudentCount > 1,
  students: (state: any): any[] => state.students,
  totalStudentCount: (state: any): number => state.totalStudentCount
}

const mutations = {
  addFilter: (state: any, filter: any) => state.filters.push(filter),
  setCompactView: (state: any, compactView: boolean) => state.isCompactView = compactView,
  setEditMode(state: any, editMode: string) {
    if (isNil(editMode)) {
      state.editMode = null
    } else if (find(EDIT_MODE_TYPES, type => editMode.match(type))) {
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
  renameCohort: (state: any, name: string) => state.cohortName = name,
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
  restoreOriginalFilters: (state: any) => state.filters = cloneDeep(state.originalFilters),
  setCurrentPage: (state: any, currentPage: number) => state.pagination.currentPage = currentPage,
  setDomain: (state: any, domain: string) => state.domain = domain,
  setModifiedSinceLastSearch: (state: any, value: boolean) => state.isModifiedSinceLastSearch = value,
  // Store an unmodified copy of the most recently applied filters in case of cancellation.
  stashOriginalFilters: (state: any) => state.originalFilters = cloneDeep(state.filters),
  toggleCompactView: (state: any) => state.isCompactView = !state.isCompactView,
  updateFilterOptions: (state: any, filterOptionGroups: any[]) => state.filterOptionGroups = filterOptionGroups,
  updateExistingFilter: (state: any, {index, updatedFilter}) => state.filters[index] = updatedFilter,
  updateSession: (state: any, {cohort, filters, students, totalStudentCount}) => {
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
  updateStudents: (state: any, {students, totalStudentCount}) => {
    state.students = students
    state.totalStudentCount = totalStudentCount
  }
}

export default {
  getters,
  mutations,
  namespaced: true,
  state
}
