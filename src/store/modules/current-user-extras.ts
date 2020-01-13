import _ from 'lodash';
import Vue from 'vue';
import { getMyCohorts } from "@/api/cohort";
import { getMyCuratedGroups } from "@/api/curated";

const state = {
  myCohorts: undefined,
  myCuratedGroups: undefined,
  preferences: {
    sortBy: 'last_name'
  }
};

const getters = {
  myCohorts: (state: any): any => state.myCohorts,
  myCuratedGroups: (state: any): any => state.myCuratedGroups,
  preferences: (state: any): any => state.preferences
};

const mutations = {
  cohortCreated: (state: any, cohort: any) => state.myCohorts.push(cohort),
  cohortDeleted: (state: any, id: any) => {
    let indexOf = state.myCohorts.findIndex(cohort => cohort.id === id);
    state.myCohorts.splice(indexOf, 1);
  },
  cohortsLoaded: (state: any, cohorts: any[]) => state.myCohorts = cohorts,
  cohortUpdated: (state: any, updatedCohort: any) => {
    let cohort = state.myCohorts.find(
      cohort => cohort.id === +updatedCohort.id
    );
    Object.assign(cohort, updatedCohort);
  },
  curatedGroupCreated: (state: any, group: any) => state.myCuratedGroups.push(group),
  curatedGroupDeleted: (state: any, id: any) => {
    let indexOf = state.myCuratedGroups.findIndex(curatedGroup => {
      return curatedGroup.id === id;
    });
    state.myCuratedGroups.splice(indexOf, 1);
  },
  curatedGroupsLoaded: (state: any, curatedGroups: any) => state.myCuratedGroups = curatedGroups,
  curatedGroupUpdated: (state: any, updatedGroup: any) => {
    let group = state.myCuratedGroups.find(group => group.id === +updatedGroup.id);
    Object.assign(group, updatedGroup);
  },
  setDropInStatus: (state: any, {deptCode, status}) => {
    const currentUser = Vue.prototype.$currentUser;
    const dropInAdvisorStatus = _.find(currentUser.dropInAdvisorStatus, {'deptCode': deptCode.toUpperCase()});
    if (dropInAdvisorStatus) {
      dropInAdvisorStatus.status = status;
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
  async cohortsLoaded({ commit }) {
    getMyCohorts().then(cohorts => commit('cohortsLoaded', cohorts))
  },
  async curatedGroupsLoaded({ commit }) {
    getMyCuratedGroups().then(curatedGroups => commit('curatedGroupsLoaded', curatedGroups));
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
