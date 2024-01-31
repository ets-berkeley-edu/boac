import {find, isNil} from 'lodash'

const VALID_MODES = ['bulkAdd', 'rename']

const state = {
  curatedGroupId: undefined,
  curatedGroupName: undefined,
  domain: undefined,
  itemsPerPage: 50,
  mode: undefined,
  ownerId: undefined,
  pageNumber: undefined,
  referencingCohortIds: undefined,
  students: undefined,
  totalStudentCount: undefined
}

const getters = {
  curatedGroupId: (state: any): number => state.curatedGroupId,
  curatedGroupName: (state: any): string => state.curatedGroupName,
  domain: (state: any): string => state.domain,
  itemsPerPage: (state: any): number => state.itemsPerPage,
  mode: (state: any): string => state.mode,
  ownerId: (state: any): number => state.ownerId,
  pageNumber: (state: any): number => state.pageNumber,
  referencingCohortIds: (state: any): number[] => state.referencingCohortIds,
  students: (state: any): any[] => state.students,
  totalStudentCount: (state: any): number => state.totalStudentCount
}

const mutations = {
  removeStudent: (state: any, sid: string) => {
    const deleteIndex = state.students.findIndex(student => student.sid === sid)
    if (deleteIndex > -1) {
      state.students.splice(deleteIndex, 1)
    }
  },
  resetMode: (state: any) => state.mode = undefined,
  setCuratedGroupId: (state: any, curatedGroupId: number) => state.curatedGroupId = curatedGroupId,
  setCuratedGroupName: (state: any, curatedGroupName: string) => state.curatedGroupName = curatedGroupName,
  setDomain: (state: any, domain: string) => state.domain = domain,
  setMode(state: any, mode: string) {
    if (isNil(mode)) {
      state.mode = undefined
    } else if (find(VALID_MODES, type => mode.match(type))) {
      state.mode = mode
    } else {
      throw new TypeError('Invalid mode: ' + mode)
    }
  },
  setOwnerId: (state: any, ownerId: number) => state.ownerId = ownerId,
  setPageNumber: (state: any, pageNumber: number) => state.pageNumber = pageNumber,
  setReferencingCohortIds: (state: any, referencingCohortIds: number[]) => state.referencingCohortIds = referencingCohortIds,
  setStudents: (state: any, students: any[]) => state.students = students,
  setTotalStudentCount: (state: any, totalStudentCount: number) => state.totalStudentCount = totalStudentCount
}


export default {
  getters,
  mutations,
  namespaced: true,
  state
}
