import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

const state = {
  apiBaseUrl: process.env.VUE_APP_API_BASE_URL,
  config: null,
  loading: null,
  errors: [],
  user: null
};

const getters = {
  config: (state: any) => {
    return state.config;
  },
  errors: (state: any) => {
    return state.errors;
  },
  loading: (state: any) => {
    return state.loading;
  },
  user: (state: any) => {
    return state.user;
  }
};

const mutations = {
  logout: (state: any) => {
    state.user = null;
  },
  loadingStart: (state: any) => {
    state.loading = true;
  },
  loadingComplete: (state: any) => {
    state.loading = false;
  },
  registerUser: (state: any, user: any) => {
    state.user = user;
  },
  reportError: (state: any, error: any) => {
    error.id = new Date().getTime();
    state.errors.push(error);
  },
  storeConfig: (state: any, config: any) => {
    state.config = config;
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
