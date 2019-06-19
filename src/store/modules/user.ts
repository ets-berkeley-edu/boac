import _ from 'lodash';
import Vue from 'vue';
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
  registerUser: (state: any, user: any) => {
    if (user.uid) {
      state.user = user;
      Vue.prototype.$eventHub.$emit('user-profile-loaded');
    }
  },
  putCalnetUserByCsid: (state: any, { csid, calnetUser }: any) =>
    (state.calnetUsersByCsid[csid] = calnetUser),
  setUserGroups: (state: any, userGroups: any[]) => (state.userGroups = userGroups),
  setDemoMode: (state: any, demoMode: boolean) =>
    (state.user.inDemoMode = demoMode),
  setUserPreference: (state: any, { key, value }) => {
    if (_.has(state.preferences, key)) {
      state.preferences[key] = value;
      Vue.prototype.$eventHub.$emit(`${key}-user-preference-change`, value);
    } else {
      throw new TypeError('Invalid user preference type: ' + key);
    }
  }
};

const actions = {
  loadCalnetUserByCsid: ({ commit, state }, csid) => {
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
  loadUserGroups: ({ commit, state }) => {
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
  loadUser: ({ commit, state }) => {
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
  setUserPreference: ({ commit }, { key, value }) => commit('setUserPreference', { key, value })
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
