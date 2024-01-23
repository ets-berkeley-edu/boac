import mitt from 'mitt'
import Vue from 'vue'
import {getServiceAnnouncement} from '@/api/config'

const state = {
  announcement: undefined,
  dismissedFooterAlert: false,
  dismissedServiceAnnouncement: false,
  eventHub: mitt(),
  loading: undefined,
  loadingStartTime: undefined
}

const getters = {
  announcement: (state: any): string => state.announcement,
  dismissedFooterAlert: (): boolean => state.dismissedFooterAlert,
  dismissedServiceAnnouncement: (): boolean => state.dismissedServiceAnnouncement,
  loading: (state: any): boolean => state.loading
}

const mutations = {
  broadcast: (state: any, {eventType, data}: any) => state.eventHub.emit(eventType, data),
  dismissFooterAlert: (state: any) => state.dismissedFooterAlert = true,
  dismissServiceAnnouncement: (state: any) => state.dismissedServiceAnnouncement = true,
  loadingComplete: (state: any, focusTarget?: string) => {
    if (!Vue.prototype.$config.isProduction) {
      console.log(`Page loaded in ${(new Date().getTime() - state.loadingStartTime) / 1000} seconds`)
    }
    state.loading = false
    if (focusTarget) {
      Vue.prototype.$putFocusNextTick(focusTarget)
    } else {
      const callable = () => {
        const elements = document.getElementsByTagName('h1')
        if (elements.length > 0) {
          elements[0].setAttribute('tabindex', '-1')
          elements[0].focus()
        }
        return elements.length > 0
      }
      Vue.prototype.$nextTick(() => {
        let counter = 0
        const job = setInterval(() => (callable() || ++counter > 3) && clearInterval(job), 500)
      })
    }
  },
  loadingStart: (state: any) => {
    state.loading = true
    state.loadingStartTime = new Date().getTime()
  },
  setEventHandler: (state: any, {type, handler}: any) => {
    state.eventHub.on(type, handler)
  },
  removeEventHandler: (state: any, {type, handler}: any) => state.eventHub.off(type, handler),
  restoreServiceAnnouncement: (state: any) => state.dismissedServiceAnnouncement = false,
  setAnnouncement: (state: any, data: any) => (state.announcement = data),
}

const actions = {
  dismissFooterAlert: ({commit}) => commit('dismissFooterAlert'),
  dismissServiceAnnouncement: ({commit}) => commit('dismissServiceAnnouncement'),
  loadServiceAnnouncement: ({commit}) => getServiceAnnouncement().then(data => commit('setAnnouncement', data)),
  restoreServiceAnnouncement: ({commit}) => commit('restoreServiceAnnouncement'),
  loadingStart: ({commit}) => commit('loadingStart')
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
