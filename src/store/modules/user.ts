import _ from 'lodash';
import store from '@/store';
import Vue from 'vue';
import { getUserByCsid, getUserGroups, getUserProfile, getUserStatus } from '@/api/user';

const state = {
  calnetUsersByCsid: {},
  preferences: {
    sortBy: 'last_name'
  },
  user: undefined,
  userAuthStatus: undefined,
  userGroups: undefined
};

const getters = {
  userAuthStatus: (state: any): boolean => state.userAuthStatus,
  preferences: (state: any): any => state.preferences,
  user: (state: any): any => state.user
};

const mutations = {
  registerUser: (state: any, user: any) => {
    if (user.uid) {
      state.user = user;
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
  },
  setUserAuthStatus: (state: any, userAuthStatus: any) => (state.userAuthStatus = userAuthStatus)
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
  loadUserAuthStatus: ({ commit, state }) => {
    return new Promise(resolve => {
      if (_.get(state.userAuthStatus, 'isAuthenticated')) {
        resolve(state.userAuthStatus);
      } else {
        getUserStatus()
          .then(data => {
            commit('setUserAuthStatus', data);
          })
          .then(() => {
            resolve(state.userAuthStatus);
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
          let googleAnalyticsId = store.getters['context/googleAnalyticsId'];
          if (googleAnalyticsId) {
            Vue.prototype.$ga.set('userId', user.uid);
            const dept_code = user.isAdmin
              ? 'ADMIN'
              : _.keys(user.departments)[0];
            if (dept_code) {
              Vue.prototype.$ga.set('dimension1', dept_code);
            }
          }
          commit('registerUser', user);
          Vue.prototype.$eventHub.$emit('user-profile-loaded');
          resolve(user);
        });
      }
    });
  },
  logout: ({ commit }) => commit('logout'),
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
