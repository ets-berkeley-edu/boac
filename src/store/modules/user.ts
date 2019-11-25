import _ from 'lodash';
import Vue from 'vue';
import { event } from 'vue-analytics';
import { getCalnetProfileByCsid, getUserProfile } from '@/api/user';
import { gaTrackUserSessionStart } from '@/api/ga';

const gaEvent = (category, action, label, value) => event(category, action, label, value);

const state = {
  calnetUsersByCsid: {},
  preferences: {
    sortBy: 'last_name'
  },
  user: undefined
};

const getters = {
  preferences: (state: any): any => state.preferences,
  uid: (state: any): string => state.user && state.user.uid,
  user: (state: any): any => state.user
};

const mutations = {
  putCalnetUserByCsid: (state: any, {csid, calnetUser}: any) =>
    (state.calnetUsersByCsid[csid] = calnetUser),
  registerUser: (state: any, user: any) => {
    if (user.uid) {
      state.user = user;
      Vue.prototype.$eventHub.$emit('user-profile-loaded');
    }
  },
  setDemoMode: (state: any, demoMode: boolean) =>
    (state.user.inDemoMode = demoMode),
  setDropInStatus: (state: any, {deptCode, available}) => {
    const dropInAdvisorStatus = _.find(state.user.dropInAdvisorStatus, {'deptCode': deptCode.toUpperCase()});
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
  loadCalnetUserByCsid: ({commit, state}, csid) => {
    return new Promise(resolve => {
      if (state.calnetUsersByCsid[csid]) {
        resolve(state.calnetUsersByCsid[csid]);
      } else {
        getCalnetProfileByCsid(csid)
          .then(calnetUser => {
            commit('putCalnetUserByCsid', {csid, calnetUser});
            resolve(state.calnetUsersByCsid[csid]);
          });
      }
    });
  },
  loadUser: ({commit, state}) => {
    return new Promise(resolve => {
      if (state.user) {
        resolve(state.user);
      } else {
        getUserProfile().then(user => {
          gaTrackUserSessionStart(user);
          commit('registerUser', user);
          resolve(user);
        });
      }
    });
  },
  logout: ({ commit }) => commit('logout'),
  registerUser: ({ commit }, user) => commit('registerUser', user),
  setDemoMode: ({ commit }, demoMode) => commit('setDemoMode', demoMode),
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
