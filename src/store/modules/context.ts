import Vue from 'vue'
import { getServiceAnnouncement } from '@/api/config'

const state = {
  announcement: undefined,
  hasUserDismissedFooterAlert: false,
  loading: undefined,
  screenReaderAlert: undefined
}

const getters = {
  announcement: (state: any): string => state.announcement,
  hasUserDismissedFooterAlert: (): boolean => state.hasUserDismissedFooterAlert,
  loading: (state: any): boolean => state.loading,
  screenReaderAlert: (state: any): string => state.screenReaderAlert
}

const mutations = {
  dismissFooterAlert: (state: any) => state.hasUserDismissedFooterAlert = true,
  loadingComplete: (state: any) => (state.loading = false),
  loadingStart: (state: any) => (state.loading = true),
  setScreenReaderAlert: (state: any, alert: any) => (state.screenReaderAlert = alert),
  storeAnnouncement: (state: any, data: any) => (state.announcement = data),
}

const actions = {
  alertScreenReader: ({ commit }, alert) => {
    commit('setScreenReaderAlert', '')
    Vue.nextTick(() => commit('setScreenReaderAlert', alert))
  },
  dismissFooterAlert: ({ commit }) => commit('dismissFooterAlert'),
  loadingComplete: ({ commit }) => commit('loadingComplete'),
  loadingStart: ({ commit }) => commit('loadingStart'),
  loadServiceAnnouncement: ({ commit }) => new Promise(() => getServiceAnnouncement().then(data => commit('storeAnnouncement', data)))
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
