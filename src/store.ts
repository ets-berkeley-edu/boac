import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

const state = {
  apiBaseUrl: process.env.VUE_APP_API_BASE_URL,
  errors: [],
  user: null
};

const getters = {
  errors: (state: any) => {
    return state.errors;
  },
  user: (state: any) => {
    return state.user;
  }
};

const mutations = {
  logout: (state: any) => {
    state.user = null;
  },
  registerMe: (state: any, user: any) => {
    state.user = user;
  },
  reportError: (state: any, error: any) => {
    error.id = new Date().getTime();
    state.errors.push(error);
  },
  dismissError: (state: any, id: number) => {
    const indexOf = state.errors.findIndex((e: any) => e.id === id);
    if (indexOf > -1) {
      state.errors.splice(indexOf, 1);
    }
  }
};

export default new Vuex.Store({
  state,
  getters,
  mutations
});
