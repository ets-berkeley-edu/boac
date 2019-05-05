import _ from 'lodash';
import { getConfig, getToolSettings } from '@/api/config';
import Vue from 'vue';

const state = {
  config: undefined,
  errors: [],
  loading: undefined,
  screenReaderAlert: undefined
};

const getters = {
  apiBaseUrl: (): any => process.env.VUE_APP_API_BASE_URL,
  currentEnrollmentTermId: (state: any): boolean => _.get(state.config, 'currentEnrollmentTermId'),
  devAuthEnabled: (state: any): boolean => _.get(state.config, 'devAuthEnabled'),
  disableMatrixViewThreshold: (state: any): string => _.get(state.config, 'disableMatrixViewThreshold'),
  errors: (state: any): any => state.errors,
  featureFlagEditNotes: (state: any): any => _.get(state.config, 'featureFlagEditNotes'),
  googleAnalyticsId: (state: any): string => _.get(state.config, 'googleAnalyticsId'),
  isDemoModeAvailable: (state: any): string => _.get(state.config, 'isDemoModeAvailable'),
  isServiceAlertPublished: (state: any): string => _.get(state.config, 'isServiceAlertPublished'),
  maxAttachmentsPerNote: (state: any): string => _.get(state.config, 'maxAttachmentsPerNote'),
  loading: (state: any): boolean => state.loading,
  serviceAlert: (state: any): string => _.get(state.config, 'serviceAlert'),
  srAlert: (state: any): string => state.screenReaderAlert,
  supportEmailAddress: (state: any): string => _.get(state.config, 'supportEmailAddress')
};

const mutations = {
  clearAlertsInStore: (state: any) => {
    state.errors = [];
    state.screenReaderAlert = undefined;
  },
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
    Vue.prototype.$eventHub.$emit('error-reported', error);
  },
  screenReaderAlert: (state: any, alert: any) => (state.screenReaderAlert = alert),
  storeConfig: (state: any, config: any) => (state.config = config)
};

const actions = {
  alertScreenReader: ({ commit }, alert) => commit('screenReaderAlert', alert),
  clearAlertsInStore: ({ commit }) => commit('clearAlertsInStore'),
  dismissError: ({ commit }, id) => commit('dismissError', id),
  loadingComplete: ({ commit }) => commit('loadingComplete'),
  loadingStart: ({ commit }) => commit('loadingStart'),
  loadConfig: ({ commit, state }) => {
    return new Promise(resolve => {
      if (state.config) {
        resolve(state.config);
      } else {
        getConfig().then(config => {
          const keys = [
            'SERVICE_ALERT',
            'IS_SERVICE_ALERT_PUBLISHED'
          ];
          getToolSettings(keys).then(toolSettings => {
            commit('storeConfig', _.assignIn(config, toolSettings));
            resolve(config);
          });
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
