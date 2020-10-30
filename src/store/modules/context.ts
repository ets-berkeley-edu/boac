import { getServiceAnnouncement } from '@/api/config'

const state = {
  announcement: undefined,
  dismissedFooterAlert: false,
  dismissedServiceAnnouncement: false,
  loading: undefined
}

const getters = {
  announcement: (state: any): string => state.announcement,
  dismissedFooterAlert: (): boolean => state.dismissedFooterAlert,
  dismissedServiceAnnouncement: (): boolean => state.dismissedServiceAnnouncement,
  loading: (state: any): boolean => state.loading
}

const mutations = {
  dismissFooterAlert: (state: any) => state.dismissedFooterAlert = true,
  dismissServiceAnnouncement: (state: any) => state.dismissedServiceAnnouncement = true,
  loadingComplete: (state: any) => (state.loading = false),
  loadingStart: (state: any) => (state.loading = true),
  restoreServiceAnnouncement: (state: any) => state.dismissedServiceAnnouncement = false,
  setAnnouncement: (state: any, data: any) => (state.announcement = data),
}

const actions = {
  dismissFooterAlert: ({ commit }) => commit('dismissFooterAlert'),
  dismissServiceAnnouncement: ({ commit }) => commit('dismissServiceAnnouncement'),
  loadingComplete: ({ commit }) => commit('loadingComplete'),
  loadingStart: ({ commit }) => commit('loadingStart'),
  loadServiceAnnouncement: ({ commit }) => getServiceAnnouncement().then(data => commit('setAnnouncement', data)),
  restoreServiceAnnouncement: ({ commit }) => commit('restoreServiceAnnouncement')
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
