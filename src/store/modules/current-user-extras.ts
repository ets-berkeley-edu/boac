import _ from 'lodash'
import Vue from 'vue'

const state = {
  myAdmitCuratedGroups: undefined,
  myCuratedGroups: undefined
}

const getters = {
  myAdmitCuratedGroups: (state: any): any => state.myAdmitCuratedGroups,
  myCuratedGroups: (state: any): any => state.myCuratedGroups
}

const mutations = {
  dropInAdvisorAdded: (state: any, dropInAdvisor: any) => {
    Vue.prototype.$currentUser.dropInAdvisorStatus = _.concat(Vue.prototype.$currentUser.dropInAdvisorStatus, dropInAdvisor)
  },
  dropInAdvisorDeleted: (state: any, deptCode: string) => _.remove(Vue.prototype.$currentUser.dropInAdvisorStatus, {'deptCode': deptCode.toUpperCase()}),
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

export default {
  namespaced: true,
  state,
  getters,
  mutations
}
