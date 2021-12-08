import _ from 'lodash'
import {addStudents, getCuratedGroup, removeFromCuratedGroup, renameCuratedGroup} from '@/api/curated'
import Vue from 'vue'

const $_goToPage = ({commit, state}, pageNumber: number) => {
  return new Promise(resolve => {
    commit('setPageNumber', pageNumber)
    const offset = _.multiply(pageNumber - 1, state.itemsPerPage)
    const preferences = Vue.prototype.$currentUser.preferences
    getCuratedGroup(state.curatedGroupId, preferences.sortBy, preferences.termId, offset, state.itemsPerPage).then(group => {
      if (group) {
        commit('setCuratedGroupName', group.name)
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
      addStudents(state.curatedGroupId, sids, true).then(() => {
        return $_goToPage({commit, state}, 1).then(resolve)
      })
    })
  },
  goToPage: ({commit, state}, pageNumber) => $_goToPage({commit, state}, pageNumber),
  init: ({commit}, curatedGroupId: number) => {
    commit('setCuratedGroupId', curatedGroupId)
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
