import _ from 'lodash';
import router from '@/router';
import store from '@/store';
import Vue from 'vue';
import VueAnalytics from 'vue-analytics';
import { getServiceAnnouncement } from '@/api/config';

const state = {
  announcement: undefined,
  hasUserDismissedFooterAlert: false,
  loading: undefined,
  screenReaderAlert: undefined
};

const getters = {
  announcement: (state: any): string => state.announcement,
  apiBaseUrl: (): any => process.env.VUE_APP_API_BASE_URL,
  currentEnrollmentTerm: (): boolean => _.get(Vue.prototype.$config, 'currentEnrollmentTerm'),
  currentEnrollmentTermId: (): boolean => _.get(Vue.prototype.$config, 'currentEnrollmentTermId'),
  disableMatrixViewThreshold: (): string => _.get(Vue.prototype.$config, 'disableMatrixViewThreshold'),
  hasUserDismissedFooterAlert: (): boolean => state.hasUserDismissedFooterAlert,
  isVueAppDebugMode: (): any => _.trim(process.env.VUE_APP_DEBUG).toLowerCase() === 'true',
  maxAttachmentsPerNote: (): string => _.get(Vue.prototype.$config, 'maxAttachmentsPerNote'),
  loading: (state: any): boolean => state.loading,
  screenReaderAlert: (state: any): string => state.screenReaderAlert,
  supportEmailAddress: (): string => _.get(Vue.prototype.$config, 'supportEmailAddress'),
  timezone: (): string => _.get(Vue.prototype.$config, 'timezone')
};

const mutations = {
  dismissFooterAlert: (state: any) => state.hasUserDismissedFooterAlert = true,
  loadingComplete: (state: any) => (state.loading = false),
  loadingStart: (state: any) => (state.loading = true),
  setScreenReaderAlert: (state: any, alert: any) => (state.screenReaderAlert = alert),
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
    const currentUser = Vue.prototype.$currentUser;
    if (currentUser.isAuthenticated) {
      const isAdvisor = !!_.size(_.filter(currentUser.departments, d => d.isAdvisor || d.isDirector));
      if (isAdvisor || currentUser.isAdmin) {
        store.dispatch('cohort/loadMyCohorts');
        store.dispatch('curated/loadMyCuratedGroups');
      }
      store.dispatch('context/loadServiceAnnouncement');
    }
    let googleAnalyticsId = _.get(Vue.prototype.$config, 'googleAnalyticsId');
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
  },
  loadingComplete: ({ commit }) => commit('loadingComplete'),
  loadingStart: ({ commit }) => commit('loadingStart'),
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
