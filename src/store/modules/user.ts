import _ from 'lodash';
import Vue from 'vue';
import { event } from 'vue-analytics';

const gaEvent = (category, action, label, value) => event(category, action, label, value);

const state = {
  preferences: {
    sortBy: 'last_name'
  }
};

const getters = {
  preferences: (state: any): any => state.preferences,
  user: (): any => Vue.prototype.$currentUser
};

const mutations = {
  setDropInStatus: (state: any, {deptCode, available}) => {
    const currentUser = Vue.prototype.$currentUser;
    const dropInAdvisorStatus = _.find(currentUser.dropInAdvisorStatus, {'deptCode': deptCode.toUpperCase()});
    if (dropInAdvisorStatus) {
      dropInAdvisorStatus.available = available;
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
  gaAppointmentEvent: (state: any, {id, label, action}) => gaEvent('Appointment', action, label, id),
  gaCohortEvent: (state: any, {id, name, action}) => gaEvent('Cohort', action, name, id),
  gaCourseEvent: (state: any, {id, name, action}) => gaEvent('Course', action, name, id),
  gaCuratedEvent: (state: any, {id, name, action}) => gaEvent('Curated Group', action, name, id),
  gaNoteEvent: (state: any, {id, label, action}) => gaEvent('Advising Note', action, label, id),
  gaNoteTemplateEvent: (state: any, {id, label, action}) => gaEvent('Advising Note Template', action, label, id),
  gaSearchEvent: (state: any, action: string) => gaEvent('Search', action, null, null),
  gaStudentAlert: (state: any, action: string) => gaEvent('Student Alert', action, null, null),
  registerUser: ({ commit }, user) => commit('registerUser', user),
  setDropInStatus: ({ commit }, {deptCode, available}) => commit('setDropInStatus', {deptCode, available}),
  setUserPreference: ({ commit }, {key, value}) => commit('setUserPreference', { key, value })
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
