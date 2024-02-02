import _ from 'lodash'
import mitt from 'mitt'
import router from '@/router'
import store from '@/store'
import Vue from 'vue'

export function alertScreenReader(message: string, politeness?: string) {
  store.commit('context/setScreenReaderAlert', {message: ''})
  Vue.nextTick(() => {
    store.commit('context/setScreenReaderAlert', {message, politeness})
  })
}

const state = {
  announcement: undefined,
  config: undefined,
  currentUser: undefined,
  dismissedFooterAlert: false,
  dismissedServiceAnnouncement: false,
  eventHub: mitt(),
  loading: undefined,
  loadingStartTime: undefined,
  screenReaderAlert: {
    message: '',
    politeness: 'polite'
  }
}

const getters = {
  announcement: (state: any): string => state.announcement,
  config: (state: any): any => state.config,
  currentUser: (state: any): any => state.currentUser,
  dismissedFooterAlert: (): boolean => state.dismissedFooterAlert,
  dismissedServiceAnnouncement: (): boolean => state.dismissedServiceAnnouncement,
  loading: (state: any): boolean => state.loading,
  screenReaderAlert: (state: any): any => state.screenReaderAlert
}

const mutations = {
  addMyCohort: (state: any, cohort: any) => state.currentUser.myCohorts.push(cohort),
  addMyCuratedGroup: (state: any, curatedGroup: any) => {
    state.currentUser.myCuratedGroups.push(curatedGroup)
    state.currentUser.myCuratedGroups = _.sortBy(state.currentUser.myCuratedGroups, 'name')
  },
  broadcast: (state: any, {eventType, data}: any) => state.eventHub.emit(eventType, data),
  dismissFooterAlert: (state: any) => state.dismissedFooterAlert = true,
  dismissServiceAnnouncement: (state: any) => state.dismissedServiceAnnouncement = true,
  loadingComplete: (state: any, srAlert?: any) => {
    if (!store.getters['context/config'].isProduction) {
      console.log(`Page loaded in ${(new Date().getTime() - state.loadingStartTime) / 1000} seconds`)
    }
    state.loading = false
    alertScreenReader(srAlert || `${String(_.get(router.currentRoute, 'name', ''))} page loaded.`)

    const callable = () => {
      const elements = document.getElementsByTagName('h1')
      if (elements.length > 0) {
        elements[0].setAttribute('tabindex', '-1')
        elements[0].focus()
      }
      return elements.length > 0
    }
    Vue.nextTick(() => {
      let counter = 0
      const job = setInterval(() => (callable() || ++counter > 3) && clearInterval(job), 500)
    })
  },
  loadingStart: (state: any, route?: string|Object) => {
    state.loading = true
    state.loadingStartTime = new Date().getTime()
    alertScreenReader(`${String(_.get(route, 'name', ''))} page is loading`)
  },
  removeEventHandler: (state: any, {type, handler}: any) => state.eventHub.off(type, handler),
  removeMyCohort: (state: any, cohortId: number) => {
    const indexOf = state.currentUser.myCohorts.findIndex(cohort => cohort.id === cohortId)
    state.currentUser.myCohorts.splice(indexOf, 1)
  },
  removeMyCuratedGroup: (state: any, curatedGroupId: number) => {
    const indexOf = state.currentUser.myCuratedGroups.findIndex(curatedGroup => curatedGroup.id === curatedGroupId)
    state.currentUser.myCuratedGroups.splice(indexOf, 1)
  },
  restoreServiceAnnouncement: (state: any) => state.dismissedServiceAnnouncement = false,
  setConfig: (state: any, data: any) => state.config = data,
  setCurrentUser: (state: any, currentUser: any) => state.currentUser = currentUser,
  setDemoMode: (state: any, inDemoMode: any): void => state.currentUser.inDemoMode = inDemoMode,
  setEventHandler: (state: any, {type, handler}: any) => state.eventHub.on(type, handler),
  setMyDraftNoteCount: (state: any, count: number) => state.currentUser.myDraftNoteCount = count,
  setScreenReaderAlert: (state: any, screenReaderAlert: any) => {
    state.screenReaderAlert = {
      message: screenReaderAlert.message,
      politeness: screenReaderAlert.politeness || 'polite'
    }
  },
  setServiceAnnouncement: (state: any, data: any) => state.announcement = data,
  updateCurrentUserPreference: (state: any, {key, value}: any) => state.currentUser.preferences[key] = value,
  updateMyCohort: (state: any, updatedCohort: any) => {
    const cohort = state.currentUser.myCohorts.find(cohort => cohort.id === +updatedCohort.id)
    Object.assign(cohort, updatedCohort)
  },
  updateMyCuratedGroup: (state: any, updatedCuratedGroup: any) => {
    const group = state.currentUser.myCuratedGroups.find(group => group.id === +updatedCuratedGroup.id)
    Object.assign(group, updatedCuratedGroup)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations
}
