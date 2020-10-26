import _ from 'lodash'
import Vue from 'vue'
import { getMyCohorts } from '@/api/cohort'
import { getMyCuratedGroups } from '@/api/curated'

const state = {
  includeAdmits: false,
  myAdmitCohorts: undefined,
  myCohorts: undefined,
  myCuratedGroups: undefined,
  preferences: {
    admitSortBy: 'last_name',
    sortBy: 'last_name'
  }
}

const getters = {
  includeAdmits: (state: any): any => state.includeAdmits,
  myAdmitCohorts: (state: any): any => state.myAdmitCohorts,
  myCohorts: (state: any): any => state.myCohorts,
  myCuratedGroups: (state: any): any => state.myCuratedGroups,
  preferences: (state: any): any => state.preferences
}

const mutations = {
  cohortCreated: (state: any, cohort: any) => {
    const cohorts = cohort.domain === 'admitted_students' ? state.myAdmitCohorts : state.myCohorts
    cohorts.push(cohort)
  },
  cohortDeleted: (state: any, id: any) => {
    const removeFromList = cohorts => {
      const indexOf = cohorts.findIndex(cohort => cohort.id === id)
      if (indexOf > -1) {
        cohorts.splice(indexOf, 1)
        return true
      }
    }
    if (!removeFromList(state.myCohorts)) {
      removeFromList(state.myAdmitCohorts)
    }
  },
  cohortUpdated: (state: any, updatedCohort: any) => {
    const cohorts = state.myCohorts.concat(state.myAdmitCohorts)
    const cohort = cohorts.find(cohort => cohort.id === +updatedCohort.id)
    Object.assign(cohort, updatedCohort)
  },
  curatedGroupCreated: (state: any, group: any) => state.myCuratedGroups.push(group),
  curatedGroupDeleted: (state: any, id: any) => {
    const indexOf = state.myCuratedGroups.findIndex(curatedGroup => {
      return curatedGroup.id === id
    })
    state.myCuratedGroups.splice(indexOf, 1)
  },
  curatedGroupUpdated: (state: any, updatedGroup: any) => {
    const group = state.myCuratedGroups.find(group => group.id === +updatedGroup.id)
    Object.assign(group, updatedGroup)
  },
  dropInAdvisorAdded:(state: any, dropInAdvisor: any) => {
    Vue.prototype.$currentUser.dropInAdvisorStatus = _.concat(Vue.prototype.$currentUser.dropInAdvisorStatus, dropInAdvisor)
  },
  dropInAdvisorDeleted:(state: any, deptCode: string) => _.remove(Vue.prototype.$currentUser.dropInAdvisorStatus, {'deptCode': deptCode.toUpperCase()}),
  loadMyCohorts: (state: any, cohorts: any[]) => state.myCohorts = cohorts,
  loadMyAdmitCohorts: (state: any, cohorts: any[]) => state.myAdmitCohorts = cohorts,
  loadMyCuratedGroups: (state: any, curatedGroups: any) => state.myCuratedGroups = curatedGroups,
  setDropInStatus: (state: any, {deptCode, available, status}) => {
    const currentUser = Vue.prototype.$currentUser
    const dropInAdvisorStatus = _.find(currentUser.dropInAdvisorStatus, {'deptCode': deptCode.toUpperCase()})
    if (dropInAdvisorStatus) {
      dropInAdvisorStatus.available = available
      dropInAdvisorStatus.status = status
      Vue.prototype.$eventHub.emit('drop-in-status-change', dropInAdvisorStatus)
    }
  },
  setIncludeAdmits: (state: any, includeAdmits: Boolean) => state.includeAdmits = includeAdmits,
  setUserPreference: (state: any, {key, value}) => {
    if (_.has(state.preferences, key)) {
      state.preferences[key] = value
      Vue.prototype.$eventHub.emit(`${key}-user-preference-change`, value)
    } else {
      throw new TypeError('Invalid user preference type: ' + key)
    }
  }
}

const actions = {
  async loadMyCohorts({ commit, state }) {
    getMyCohorts('default').then(cohorts => commit('loadMyCohorts', cohorts))
    if (state.includeAdmits) {
      getMyCohorts('admitted_students').then(cohorts => commit('loadMyAdmitCohorts', cohorts))
    }
  },
  async loadMyCuratedGroups({ commit }) {
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
