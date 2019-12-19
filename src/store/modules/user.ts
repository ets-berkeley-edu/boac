import _ from 'lodash';
import Vue from 'vue';

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
