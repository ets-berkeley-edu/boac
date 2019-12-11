import _ from 'lodash';
import router from '@/router';
import store from '@/store';
import Vue from 'vue';
import VueAnalytics from 'vue-analytics';
import { getConfig, getServiceAnnouncement } from '@/api/config';

const isAdvisor = user => {
  return !!_.size(_.filter(user.departments, d => d.isAdvisor || d.isDirector));
};

const state = {
  announcement: undefined,
  config: undefined,
  hasUserDismissedFooterAlert: false,
  loading: undefined,
  screenReaderAlert: undefined
};

const getters = {
  announcement: (state: any): string => state.announcement,
  apiBaseUrl: (): any => process.env.VUE_APP_API_BASE_URL,
  apptDeskRefreshInterval: (state: any): string => _.get(state.config, 'apptDeskRefreshInterval'),
  currentEnrollmentTerm: (state: any): boolean => _.get(state.config, 'currentEnrollmentTerm'),
  currentEnrollmentTermId: (state: any): boolean => _.get(state.config, 'currentEnrollmentTermId'),
  devAuthEnabled: (state: any): boolean => _.get(state.config, 'devAuthEnabled'),
  disableMatrixViewThreshold: (state: any): string => _.get(state.config, 'disableMatrixViewThreshold'),
  ebEnvironment: (state: any): boolean => _.get(state.config, 'ebEnvironment'),
  featureFlagPassengerEdit: (state: any): boolean => _.get(state.config, 'featureFlagPassengerEdit'),
  fixedWarningOnAllPages: (state: any): string => _.get(state.config, 'fixedWarningOnAllPages'),
  googleAnalyticsId: (state: any): string => _.get(state.config, 'googleAnalyticsId'),
  hasUserDismissedFooterAlert: (state: any): boolean => state.hasUserDismissedFooterAlert,
  isDemoModeAvailable: (state: any): string => _.get(state.config, 'isDemoModeAvailable'),
  isVueAppDebugMode: (): any => _.trim(process.env.VUE_APP_DEBUG).toLowerCase() === 'true',
  maxAttachmentsPerNote: (state: any): string => _.get(state.config, 'maxAttachmentsPerNote'),
  pingFrequency: (state: any): string => _.get(state.config, 'pingFrequency'),
  loading: (state: any): boolean => state.loading,
  screenReaderAlert: (state: any): string => state.screenReaderAlert,
  supportEmailAddress: (state: any): string => _.get(state.config, 'supportEmailAddress'),
  timezone: (state: any): string => _.get(state.config, 'timezone')
};

const mutations = {
  dismissFooterAlert: (state: any) => state.hasUserDismissedFooterAlert = true,
  loadingComplete: (state: any) => (state.loading = false),
  loadingStart: (state: any) => (state.loading = true),
  setScreenReaderAlert: (state: any, alert: any) => (state.screenReaderAlert = alert),
  storeConfig: (state: any, config: any) => (state.config = config),
  storeAnnouncement: (state: any, data: any) => (state.announcement = data),
};

const actions = {
  alertScreenReader: ({ commit }, alert) => {
    commit('setScreenReaderAlert', '');
    Vue.nextTick(() => {
      commit('setScreenReaderAlert', alert);
    });
  },
  dismissFooterAlert: ({ commit }) => commit('dismissFooterAlert'),
  async initUserSession() {
    store.dispatch('context/loadConfig').then(config => {
      store.dispatch('user/loadUser').then(user => {
        if (user.isAuthenticated) {
          if (isAdvisor(user) || user.isAdmin) {
            store.dispatch('cohort/loadMyCohorts');
            store.dispatch('curated/loadMyCuratedGroups');
            store.dispatch('note/loadNoteTemplates');
            store.dispatch('note/loadSuggestedNoteTopics');
          }
          store.dispatch('context/loadServiceAnnouncement');
        }
        let googleAnalyticsId = _.get(config, 'googleAnalyticsId');
        if (googleAnalyticsId) {
          let options = {
            id: googleAnalyticsId,
            checkDuplicatedScript: true,
            debug: {
              // If debug.enabled is true then browser console gets GA debug info.
              enabled: false
            },
            fields: {},
            router
          };
          const uid = store.getters['user/uid'];
          if (uid) {
            options.fields['userId'] = uid;
          }
          Vue.use(VueAnalytics, options);
        }
      });
    });
  },
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
  loadServiceAnnouncement: ({ commit, state }) => {
    return new Promise(() => {
      if (_.isUndefined(state.announcement)) {
        getServiceAnnouncement().then(data => {
          commit('storeAnnouncement', data);
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
