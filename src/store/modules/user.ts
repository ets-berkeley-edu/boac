import _ from 'lodash';
import Vue from 'vue';
import { event } from 'vue-analytics';
import { getUserByCsid, getUserGroups, getUserProfile } from '@/api/user';
import { gaTrackUserSessionStart } from '@/api/ga';

const state = {
  calnetUsersByCsid: {},
  preferences: {
    sortBy: 'last_name'
  },
  user: undefined,
  userGroups: undefined
};

const getters = {
  preferences: (state: any): any => state.preferences,
  user: (state: any): any => state.user
};

const mutations = {
  gaEvent: (state: any, {category, action, label, value}: any) => {
    if (state.user) {
      event(category, action, label, value, {
        userId: state.user.uid
      });
    } else {
      event(category, action, label, value);
    }
  },
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
  setUserGroups: (state: any, userGroups: any[]) => (state.userGroups = userGroups),
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
  gaEvent: ({ commit }, {category, action, label, value}) => {
    commit('gaEvent', {category, action, label, value});
  },
  gaCohortEvent: ({ commit }, {id, name, action}) => {
    commit('gaEvent', {category: 'Cohort', action, name, id});
  },
  gaCuratedEvent: ({ commit }, {id, name, action}) => {
    commit('gaEvent', {category: 'Curated Group', action, name, id});
  },
  gaStudentAlert: ({ commit }, {id, name, action}) => {
    commit('gaEvent', {category: 'Student Alert', action, name, id});
  },
  gaNoteEvent: ({ commit }, {id, name, action}) => {
    commit('gaEvent', {category: 'Advising Note', action, name, id});
  },
  gaSearchEvent: ({ commit }, {id, name, action}) => {
    commit('gaEvent', {category: 'Search', action, name, id});
  },
  loadCalnetUserByCsid: ({commit, state}, csid) => {
    return new Promise(resolve => {
      if (state.calnetUsersByCsid[csid]) {
        resolve(state.calnetUsersByCsid[csid]);
      } else {
        getUserByCsid(csid)
          .then(calnetUser => {
            commit('putCalnetUserByCsid', {csid, calnetUser});
            resolve(state.calnetUsersByCsid[csid]);
          });
      }
    });
  },
  loadUserGroups: ({commit, state}) => {
    return new Promise(resolve => {
      if (state.userGroups) {
        resolve(state.userGroups);
      } else {
        getUserGroups('firstName')
          .then(data => {
            commit('setUserGroups', data);
            resolve(state.userGroups);
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
  setUserPreference: ({ commit }, {key, value}) => commit('setUserPreference', { key, value })
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
