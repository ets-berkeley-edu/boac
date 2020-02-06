import _ from 'lodash';
import Vue from 'vue';
import { getMyCohorts } from "@/api/cohort";
import { getMyCuratedGroups } from "@/api/curated";

const state = {
  myAdmitCohorts: undefined,
  myCohorts: undefined,
  myCuratedGroups: undefined,
  preferences: {
    sortBy: 'last_name'
  }
};

const getters = {
  myAdmitCohorts: (state: any): any => state.myAdmitCohorts,
  myCohorts: (state: any): any => state.myCohorts,
  myCuratedGroups: (state: any): any => state.myCuratedGroups,
  preferences: (state: any): any => state.preferences
};

const mutations = {
  cohortCreated: (state: any, cohort: any) => {
    const cohorts = cohort.domain === 'admitted_students' ? state.myAdmitCohorts : state.myCohorts;
    cohorts.push(cohort);
  },
  cohortDeleted: (state: any, id: any) => {
    const removeFromList = cohorts => {
      let indexOf = cohorts.findIndex(cohort => cohort.id === id);
      if (indexOf > -1) {
        cohorts.splice(indexOf, 1);
        return true;
      }
    };
    if (!removeFromList(state.myCohorts)) {
      removeFromList(state.myAdmitCohorts);
    }
  },
  cohortUpdated: (state: any, updatedCohort: any) => {
    const cohorts = state.myCohorts.concat(state.myAdmitCohorts);
    let cohort = cohorts.find(cohort => cohort.id === +updatedCohort.id);
    Object.assign(cohort, updatedCohort);
  },
  curatedGroupCreated: (state: any, group: any) => state.myCuratedGroups.push(group),
  curatedGroupDeleted: (state: any, id: any) => {
    let indexOf = state.myCuratedGroups.findIndex(curatedGroup => {
      return curatedGroup.id === id;
    });
    state.myCuratedGroups.splice(indexOf, 1);
  },
  curatedGroupUpdated: (state: any, updatedGroup: any) => {
    let group = state.myCuratedGroups.find(group => group.id === +updatedGroup.id);
    Object.assign(group, updatedGroup);
  },
  dropInAdvisorAdded:(state: any, dropInAdvisor: any) => {
    Vue.prototype.$currentUser.dropInAdvisorStatus = _.concat(Vue.prototype.$currentUser.dropInAdvisorStatus, dropInAdvisor)
  },
  dropInAdvisorDeleted:(state: any, deptCode: string) => _.remove(Vue.prototype.$currentUser.dropInAdvisorStatus, {'deptCode': deptCode.toUpperCase()}),
  loadMyCohorts: (state: any, cohorts: any[]) => state.myCohorts = cohorts,
  loadMyAdmitCohorts: (state: any, cohorts: any[]) => state.myAdmitCohorts = cohorts,
  loadMyCuratedGroups: (state: any, curatedGroups: any) => state.myCuratedGroups = curatedGroups,
  setDropInStatus: (state: any, {deptCode, available, status}) => {
    const currentUser = Vue.prototype.$currentUser;
    const dropInAdvisorStatus = _.find(currentUser.dropInAdvisorStatus, {'deptCode': deptCode.toUpperCase()});
    if (dropInAdvisorStatus) {
      dropInAdvisorStatus.available = available;
      dropInAdvisorStatus.status = status;
      Vue.prototype.$eventHub.$emit('drop-in-status-change', dropInAdvisorStatus);
    }
  },
  setUserPreference: (state: any, {key, value}) => {
    if (_.has(state.preferences, key)) {
      state.preferences[key] = value;
      Vue.prototype.$eventHub.$emit(`${key}-user-preference-change`, value);
    } else {
      throw new TypeError('Invalid user preference type: ' + key);
    }
  }
};

const actions = {
  async loadMyCohorts({ commit }) {
    getMyCohorts('default').then(cohorts => commit('loadMyCohorts', cohorts));
    if (Vue.prototype.$config.featureFlagAdmittedStudents) {
      getMyCohorts('admitted_students').then(cohorts => commit('loadMyAdmitCohorts', cohorts));
    }
  },
  async loadMyCuratedGroups({ commit }) {
    getMyCuratedGroups().then(curatedGroups => commit('loadMyCuratedGroups', curatedGroups));
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
