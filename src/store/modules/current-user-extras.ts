import _ from 'lodash'
import Vue from 'vue'
import {getMyCuratedGroups} from '@/api/curated'

const state = {
  myAdmitCuratedGroups: undefined,
  myCuratedGroups: undefined
}

const getters = {
  myAdmitCuratedGroups: (state: any): any => state.myAdmitCuratedGroups,
  myCuratedGroups: (state: any): any => state.myCuratedGroups
}

const mutations = {
  curatedGroupCreated: (state: any, group: any) => {
    const groups = group.domain === 'admitted_students' ? state.myAdmitCuratedGroups : state.myCuratedGroups
    groups.push(group)
    Vue.prototype.$eventHub.emit('my-curated-groups-updated')
  },
  curatedGroupDeleted: (state: any, id: any) => {
    const indexOf = state.myCuratedGroups.findIndex(curatedGroup => {
      return curatedGroup.id === id
    })
    state.myCuratedGroups.splice(indexOf, 1)
    Vue.prototype.$eventHub.emit('my-curated-groups-updated')
  },
  curatedGroupUpdated: (state: any, updatedGroup: any) => {
    const group = state.myCuratedGroups.find(group => group.id === +updatedGroup.id)
    Object.assign(group, updatedGroup)
    Vue.prototype.$eventHub.emit('my-curated-groups-updated')
  },
  dropInAdvisorAdded: (state: any, dropInAdvisor: any) => {
    Vue.prototype.$currentUser.dropInAdvisorStatus = _.concat(Vue.prototype.$currentUser.dropInAdvisorStatus, dropInAdvisor)
  },
  dropInAdvisorDeleted: (state: any, deptCode: string) => _.remove(Vue.prototype.$currentUser.dropInAdvisorStatus, {'deptCode': deptCode.toUpperCase()}),
  loadMyCuratedGroups: (state: any, curatedGroups: any) => {
    state.myCuratedGroups = _.filter(curatedGroups, c => c['domain'] === 'default')
    state.myAdmitCuratedGroups = _.filter(curatedGroups, c => c['domain'] === 'admitted_students')
  },
  setDropInStatus: (state: any, {deptCode, available, status}) => {
    const currentUser = Vue.prototype.$currentUser
    const dropInAdvisorStatus = _.find(currentUser.dropInAdvisorStatus, {'deptCode': deptCode.toUpperCase()})
    if (dropInAdvisorStatus) {
      dropInAdvisorStatus.available = available
      dropInAdvisorStatus.status = status
      Vue.prototype.$eventHub.emit('drop-in-status-change', dropInAdvisorStatus)
    }
  }
}

const actions = {
  async loadMyCuratedGroups({commit}) {
    getMyCuratedGroups().then(curatedGroups => commit('loadMyCuratedGroups', curatedGroups))
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
