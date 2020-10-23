import { getServiceAnnouncement } from '@/api/config'

const state = {
  announcement: undefined,
  hasUserDismissedFooterAlert: false,
  loading: undefined
}

const getters = {
  announcement: (state: any): string => state.announcement,
  hasUserDismissedFooterAlert: (): boolean => state.hasUserDismissedFooterAlert,
  loading: (state: any): boolean => state.loading
}

const mutations = {
  dismissFooterAlert: (state: any) => state.hasUserDismissedFooterAlert = true,
  loadingComplete: (state: any) => (state.loading = false),
  loadingStart: (state: any) => (state.loading = true),
  storeAnnouncement: (state: any, data: any) => (state.announcement = data),
}

const actions = {
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
