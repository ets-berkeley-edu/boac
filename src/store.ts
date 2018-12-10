import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

const state = {
  apiBaseUrl: process.env.VUE_APP_API_BASE_URL,
  legacyRedirectsEnabled:
    process.env.VUE_APP_ENABLE_LEGACY_REDIRECTS.toLowerCase() === 'true',
  config: null,
  loading: null,
  errors: [],
  user: null,
  isUserAuthenticated: null
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
  },
  isUserAuthenticated: (state: any) => {
    return state.isUserAuthenticated;
  },
  legacyRedirectsEnabled: (state: any) => {
    return state.legacyRedirectsEnabled;
  }
};

const mutations = {
  logout: (state: any) => {
    state.isUserAuthenticated = false;
    state.user = null;
  },
  loadingStart: (state: any) => {
    state.loading = true;
  },
  loadingComplete: (state: any) => {
    state.loading = false;
  },
  registerUser: (state: any, user: any) => {
    state.isUserAuthenticated = user.isAuthenticated;
    if (user.uid) {
      state.user = user;
    }
  },
  userAuthenticated: (state: any) => {
    state.isUserAuthenticated = true;
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
  },
  updateCuratedGroup: (state: any, data: any) => {
    let group = state.user.myCuratedCohorts.find(
      group => group.id === +data.id
    );
    group.name = data.name;
    group.studentCount = data.studentCount;
  },
  createdCuratedGroup: (state: any, group: any) => {
    state.user.myCuratedCohorts.push(group);
  }
};

export default new Vuex.Store({
  state,
  getters,
  mutations
});
