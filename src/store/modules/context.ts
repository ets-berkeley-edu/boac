import _ from 'lodash';
import { getAppConfig } from '@/api/config';

const state = {
  legacyRedirectsEnabled:
    process.env.VUE_APP_ENABLE_LEGACY_REDIRECTS.toLowerCase() === 'true',
  config: null,
  loading: null,
  errors: []
};

const getters = {
  apiBaseUrl: (): any => {
    return process.env.VUE_APP_API_BASE_URL;
  },
  currentEnrollmentTermId: (state: any): boolean => {
    return _.get(state.config, 'currentEnrollmentTermId');
  },
  devAuthEnabled: (state: any): boolean => {
    return _.get(state.config, 'devAuthEnabled');
  },
  errors: (state: any): any => {
    return state.errors;
  },
  loading: (state: any): boolean => {
    return state.loading;
  },
  legacyRedirectsEnabled: (state: any): boolean => {
    return state.legacyRedirectsEnabled;
  },
  supportEmailAddress: (state: any): string => {
    return _.get(state.config, 'supportEmailAddress');
  },
  vuePaths: (state: any): string[] => {
    return _.get(state.config, 'vuePaths');
  }
};

const mutations = {
  dismissError: (state: any, id: number) => {
    const indexOf = state.errors.findIndex((e: any) => e.id === id);
    if (indexOf > -1) {
      state.errors.splice(indexOf, 1);
    }
  },
  loadingComplete: (state: any) => {
    state.loading = false;
  },
  loadingStart: (state: any) => {
    state.loading = true;
  },
  reportError: (state: any, error: any) => {
    error.id = new Date().getTime();
    state.errors.push(error);
  },
  storeConfig: (state: any, config: any) => {
    state.config = config;
  }
};

const actions = {
  dismissError: ({ commit }, id) => {
    commit('dismissError', id);
  },
  loadingComplete: ({ commit }) => {
    commit('loadingComplete');
  },
  loadingStart: ({ commit }) => {
    commit('loadingStart');
  },
  loadConfig: ({ commit, state }) => {
    return new Promise(resolve => {
      if (state.config) {
        resolve(state.config);
      } else {
        getAppConfig().then(config => {
          commit('storeConfig', config);
          resolve(config);
        });
      }
    });
  },
  reportError: ({ commit }, error) => {
    commit('reportError', error);
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
