import _ from 'lodash'
import {addStudentsToCuratedGroup, getCuratedGroup, removeFromCuratedGroup, renameCuratedGroup} from '@/api/curated'
import store from '@/store'

const $_goToPage = ({commit, state}, pageNumber: number) => {
  return new Promise(resolve => {
    commit('setPageNumber', pageNumber)
    const user = store.getters['context/currentUser']
    const offset = _.multiply(pageNumber - 1, state.itemsPerPage)
    const orderBy = _.get(user.preferences, state.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy')
    getCuratedGroup(
      state.curatedGroupId,
      state.itemsPerPage,
      offset,
      orderBy,
      user.preferences.termId
    ).then(group => {
      if (group) {
        commit('setCuratedGroupName', group.name)
        commit('setDomain', group.domain)
        commit('setOwnerId', group.ownerId)
        commit('setReferencingCohortIds', group.referencingCohortIds)
        commit('setStudents', group.students)
        commit('setTotalStudentCount', group.totalStudentCount)
        return resolve(group)
      } else {
        return resolve(null)
      }
    })
  })
}

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
  setCuratedGroupId: (state: any, curatedGroupId: number) => state.curatedGroupId = curatedGroupId,
  setCuratedGroupName: (state: any, curatedGroupName: string) => state.curatedGroupName = curatedGroupName,
  setDomain: (state: any, domain: string) => state.domain = domain,
  setMode(state: any, mode: string) {
    if (_.isNil(mode)) {
      state.mode = undefined
    } else if (_.find(VALID_MODES, type => mode.match(type))) {
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

const actions = {
  addStudents: ({commit, state}, sids: string[]) => {
    return new Promise(resolve => {
      addStudentsToCuratedGroup(state.curatedGroupId, sids, true).then(() => {
        return $_goToPage({commit, state}, 1).then(resolve)
      })
    })
  },
  goToPage: ({commit, state}, pageNumber) => $_goToPage({commit, state}, pageNumber),
  init: ({commit}, id) => {
    commit('setCuratedGroupId', id)
    return $_goToPage({commit, state}, 1)
  },
  removeStudent: ({commit, state}, sid: string) => {
    return new Promise<void>(resolve => {
      commit('removeStudent', sid)
      removeFromCuratedGroup(state.curatedGroupId, sid).then(group => {
        commit('setTotalStudentCount', group.totalStudentCount)
        return resolve()
      })
    })
  },
  renameCuratedGroup: ({commit, state}, name: string) => {
    return new Promise<void>(resolve => {
      renameCuratedGroup(state.curatedGroupId, name).then(group => {
        commit('setCuratedGroupName', group.name)
        return resolve()
      })
    })
  },
  setMode: ({commit}, mode: string) => commit('setMode', mode)
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
