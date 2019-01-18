import _ from 'lodash';
import { getUserProfile, getUserStatus } from '@/api/user';

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
  isUserAuthenticated: undefined,
  preferences: {
    sortBy: 'last_name'
  },
  user: undefined
};

const getters = {
  canViewAsc: (state: any): boolean => $_user_canViewDepartment(state, 'UWASC'),
  canViewCoe: (state: any): boolean => $_user_canViewDepartment(state, 'COENG'),
  isAscUser: (state: any): boolean => $_user_isDepartmentMember(state, 'UWASC'),
  isCoeUser: (state: any): boolean => $_user_isDepartmentMember(state, 'COENG'),
  isUserAuthenticated: (state: any): boolean => state.isUserAuthenticated,
  preferences: (state: any): any => state.preferences,
  user: (state: any): any => state.user
};

const mutations = {
  registerUser: (state: any, user: any) => {
    state.isUserAuthenticated = user.isAuthenticated;
    if (user.uid) {
      state.user = user;
    }
  },
  setDemoMode: (state: any, demoMode: boolean) =>
    (state.user.demoMode = demoMode),
  setUserPreference: (state: any, { key, value }) => {
    if (_.has(state.preferences, key)) {
      state.preferences[key] = value;
    } else {
      throw new TypeError('Invalid user preference type: ' + key);
    }
  },
  userAuthenticated: (state: any) => (state.isUserAuthenticated = true)
};

const actions = {
  loadUserStatus: ({ commit, state }) => {
    return new Promise(resolve => {
      if (_.isNil(state.isUserAuthenticated)) {
        getUserStatus()
          .then(data => {
            if (data.isAuthenticated) {
              commit('userAuthenticated');
            }
          })
          .then(() => {
            resolve(state.isUserAuthenticated);
          });
      } else {
        resolve(state.isUserAuthenticated);
      }
    });
  },
  loadUser: ({ commit, state }) => {
    return new Promise(resolve => {
      if (state.user) {
        resolve(state.user);
      } else {
        getUserProfile().then(user => {
          commit('registerUser', user);
          resolve(user);
        });
      }
    });
  },
  logout: ({ commit }) => commit('logout'),
  setDemoMode: ({ commit }, demoMode) => commit('setDemoMode', demoMode),
  setUserPreference: ({ commit }, { key, value }) =>
    commit('setUserPreference', { key, value }),
  userAuthenticated: ({ commit }) => commit('userAuthenticated')
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
