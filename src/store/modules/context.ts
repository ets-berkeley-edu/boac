import _ from 'lodash'
import mitt from 'mitt'
import store from '@/store'
import Vue from 'vue'

const state = {
  announcement: undefined,
  config: undefined,
  currentUser: undefined,
  dismissedFooterAlert: false,
  dismissedServiceAnnouncement: false,
  eventHub: mitt(),
  loading: undefined,
  loadingStartTime: undefined
}

const getters = {
  announcement: (state: any): string => state.announcement,
  config: (state: any): any => state.config,
  currentUser: (state: any): any => state.currentUser,
  dismissedFooterAlert: (): boolean => state.dismissedFooterAlert,
  dismissedServiceAnnouncement: (): boolean => state.dismissedServiceAnnouncement,
  loading: (state: any): boolean => state.loading
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
  loadingComplete: (state: any) => {
    if (!store.getters['context/config'].isProduction) {
      console.log(`Page loaded in ${(new Date().getTime() - state.loadingStartTime) / 1000} seconds`)
    }
    state.loading = false
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
  loadingStart: (state: any) => {
    state.loading = true
    state.loadingStartTime = new Date().getTime()
  },
  removeMyCohort: (state: any, cohortId: number) => {
    const indexOf = state.currentUser.myCohorts.findIndex(cohort => cohort.id === cohortId)
    state.currentUser.myCohorts.splice(indexOf, 1)
  },
  removeMyCuratedGroup: (state: any, curatedGroupId: number) => {
    const indexOf = state.currentUser.myCuratedGroups.findIndex(curatedGroup => curatedGroup.id === curatedGroupId)
    state.currentUser.myCuratedGroups.splice(indexOf, 1)
  },
  setCurrentUser: (state: any, currentUser: any) => state.currentUser = currentUser,
  setEventHandler: (state: any, {type, handler}: any) => state.eventHub.on(type, handler),
  setServiceAnnouncement: (state: any, data: any) => state.announcement = data,
  removeEventHandler: (state: any, {type, handler}: any) => state.eventHub.off(type, handler),
  restoreServiceAnnouncement: (state: any) => state.dismissedServiceAnnouncement = false,
  setConfig: (state: any, data: any) => state.config = data,
  setDemoMode: (state: any, inDemoMode: any): void => state.currentUser.inDemoMode = inDemoMode,
  setMyDraftNoteCount: (state: any, count: number) => state.currentUser.myDraftNoteCount = count,
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
