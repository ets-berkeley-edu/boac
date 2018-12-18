import _ from 'lodash';
import { getUserProfile, getUserStatus } from '@/api/user';

const $_user_isDepartmentMember = (state, deptCode) => {
  let membership = _.get(state.user, `departments.${deptCode}`);
  return membership && (membership.isAdvisor || membership.isDirector);
};

const state = {
  user: null,
  isUserAuthenticated: null
};

const getters = {
  user: (state: any): any => state.user,
  isAscUser: (state: any): boolean => $_user_isDepartmentMember(state, 'UWASC'),
  isCoeUser: (state: any): boolean => $_user_isDepartmentMember(state, 'COENG'),
  isUserAuthenticated: (state: any): boolean => state.isUserAuthenticated
};

const mutations = {
  logout: (state: any) => {
    state.isUserAuthenticated = false;
    state.user = null;
  },
  registerUser: (state: any, user: any) => {
    state.isUserAuthenticated = user.isAuthenticated;
    if (user.uid) {
      state.user = user;
    }
  },
  userAuthenticated: (state: any) => {
    state.isUserAuthenticated = true;
  }
};

const actions = {
  logout: ({ commit }) => {
    commit('logout');
  },
  userAuthenticated: ({ commit }) => {
    commit('userAuthenticated');
  },
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
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
