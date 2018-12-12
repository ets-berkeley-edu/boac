import _ from 'lodash';
import { getUserProfile, getUserStatus } from '@/api/user';

const state = {
  currentUser: null,
  isUserAuthenticated: null
};

const getters = {
  currentUser: (state: any): any => {
    return state.currentUser;
  },
  isUserAuthenticated: (state: any): boolean => {
    return state.isUserAuthenticated;
  }
};

const mutations = {
  logout: (state: any) => {
    state.isUserAuthenticated = false;
    state.currentUser = null;
  },
  registerUser: (state: any, user: any) => {
    state.isUserAuthenticated = user.isAuthenticated;
    if (user.uid) {
      state.currentUser = user;
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
        getUserStatus().then(data => {
          if (data.isAuthenticated) {
            commit('userAuthenticated');
          }
          resolve(data.isUserAuthenticated);
        });
      } else {
        resolve(state.isUserAuthenticated);
      }
    });
  },
  loadUser: ({ commit, state }) => {
    return new Promise(resolve => {
      if (state.currentUser) {
        resolve(state.currentUser);
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
