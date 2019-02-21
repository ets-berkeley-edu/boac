import _ from 'lodash';
import store from '@/store';
import Vue from 'vue';
import { getCalnetUserByCsid, getUserGroups, getUserProfile, getUserStatus } from '@/api/user';

const $_user_isDepartmentMember = (state, deptCode) => {
  let membership = _.get(state.user, `departments.${deptCode}`);
  return membership && (membership.isAdvisor || membership.isDirector);
};

const $_user_canViewDepartment = (state, deptCode) => {
  return (
    $_user_isDepartmentMember(state, deptCode) || _.get(state.user, 'isAdmin')
  );
};

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
  canViewAsc: (state: any): boolean => $_user_canViewDepartment(state, 'UWASC'),
  canViewCoe: (state: any): boolean => $_user_canViewDepartment(state, 'COENG'),
  isAscUser: (state: any): boolean => $_user_isDepartmentMember(state, 'UWASC'),
  isCoeUser: (state: any): boolean => $_user_isDepartmentMember(state, 'COENG'),
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
        getCalnetUserByCsid(csid)
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
