import _ from 'lodash';
import { getConfig } from '@/api/config';

const state = {
  config: undefined,
  errors: [],
  loading: undefined
};

const getters = {
  apiBaseUrl: (): any => process.env.VUE_APP_API_BASE_URL,
  currentEnrollmentTermId: (state: any): boolean =>
    _.get(state.config, 'currentEnrollmentTermId'),
  devAuthEnabled: (state: any): boolean =>
    _.get(state.config, 'devAuthEnabled'),
  disableMatrixViewThreshold: (state: any): string =>
    _.get(state.config, 'disableMatrixViewThreshold'),
  errors: (state: any): any => state.errors,
  googleAnalyticsId: (state: any): string => state.config.googleAnalyticsId,
  loading: (state: any): boolean => state.loading,
  supportEmailAddress: (state: any): string =>
    _.get(state.config, 'supportEmailAddress')
};

const mutations = {
  clearErrors: (state: any) => (state.errors = []),
  dismissError: (state: any, id: number) => {
    const indexOf = state.errors.findIndex((e: any) => e.id === id);
    if (indexOf > -1) {
      state.errors.splice(indexOf, 1);
    }
  },
  loadingComplete: (state: any) => (state.loading = false),
  loadingStart: (state: any) => (state.loading = true),
  reportError: (state: any, error: any) => {
    error.id = new Date().getTime();
    state.errors.push(error);
  },
  storeConfig: (state: any, config: any) => (state.config = config)
};

const actions = {
  clearErrors: ({ commit }) => commit('clearErrors'),
  dismissError: ({ commit }, id) => commit('dismissError', id),
  loadingComplete: ({ commit }) => commit('loadingComplete'),
  loadingStart: ({ commit }) => commit('loadingStart'),
  loadConfig: ({ commit, state }) => {
    return new Promise(resolve => {
      if (state.config) {
        resolve(state.config);
      } else {
        getConfig().then(config => {
          commit('storeConfig', config);
          resolve(config);
        });
      }
    });
  },
  reportError: ({ commit }, error) => commit('reportError', error)
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
