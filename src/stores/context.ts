import _ from 'lodash'
import mitt from 'mitt'
import router from '@/router'
import {defineStore} from 'pinia'
import {nextTick} from 'vue'

export type BoaConfig = {
  isProduction: boolean,
  maxAttachmentsPerNote: number
}

export const useContextStore = defineStore('context', {
  state: () => ({
    announcement: undefined,
    config: undefined as BoaConfig | undefined,
    currentUser: {
      inDemoMode: false,
      myCohorts: [] as Array<any>,
      myCuratedGroups: [] as Array<any>,
      myDraftNoteCount: undefined as number | undefined,
      preferences: {}
    },
    dismissedFooterAlert: false,
    dismissedServiceAnnouncement: false,
    eventHub: mitt(),
    loading: false,
    loadingStartTime: undefined as number | undefined,
    screenReaderAlert: {
      message: '',
      politeness: 'polite'
    }
  }),
  actions: {
    addMyCohort(cohort: any) {
      this.currentUser.myCohorts.push(cohort)
    },
    addMyCuratedGroup(curatedGroup: any) {
      this.currentUser.myCuratedGroups.push(curatedGroup)
      this.currentUser.myCuratedGroups = _.sortBy(this.currentUser.myCuratedGroups, 'name')
    },
    alertScreenReader(message: string, politeness='polite') {
      this.screenReaderAlert.message = ''
      nextTick(() => {
        this.screenReaderAlert = {message, politeness}
      }).then(_.noop)
    },
    broadcast(eventType, data) {
      this.eventHub.emit(eventType, data)
    },
    dismissFooterAlert() {
      this.dismissedFooterAlert = true
    },
    dismissServiceAnnouncement() {
      this.dismissedServiceAnnouncement = true
    },
    loadingComplete(srAlert?: any) {
      if (!this.config.isProduction) {
        console.log(`Page loaded in ${(new Date().getTime() - (this.loadingStartTime || 0)) / 1000} seconds`)
      }
      this.loading = false
      this.alertScreenReader(srAlert || `${String(_.get(router.currentRoute, 'name', ''))} page loaded.`)

      const callable = () => {
        const elements = document.getElementsByTagName('h1')
        if (elements.length > 0) {
          elements[0].setAttribute('tabindex', '-1')
          elements[0].focus()
        }
        return elements.length > 0
      }
      nextTick(() => {
        let counter = 0
        const job = setInterval(() => (callable() || ++counter > 3) && clearInterval(job), 500)
      }).then(_.noop)
    },
    loadingStart(route?: string|Object) {
      this.loading = true
      this.loadingStartTime = new Date().getTime()
      this.alertScreenReader(`${String(_.get(route, 'name', ''))} page is loading`)
    },
    removeEventHandler(type, handler) {
      this.eventHub.off(type, handler)
    },
    removeMyCohort(cohortId: number) {
      const indexOf = this.currentUser.myCohorts.findIndex(cohort => cohort.id === cohortId)
      this.currentUser.myCohorts.splice(indexOf, 1)
    },
    removeMyCuratedGroup(curatedGroupId: number) {
      const indexOf = this.currentUser.myCuratedGroups.findIndex(curatedGroup => curatedGroup.id === curatedGroupId)
      this.currentUser.myCuratedGroups.splice(indexOf, 1)
    },
    restoreServiceAnnouncement() {
      this.dismissedServiceAnnouncement = false
    },
    setConfig(data: any) {
      this.config = data
    },
    setCurrentUser(currentUser: any) {
      this.currentUser = currentUser
    },
    setDemoMode(inDemoMode: any): void {
      this.currentUser.inDemoMode = inDemoMode
    },
    setEventHandler(type, handler) {
      this.eventHub.on(type, handler)
    },
    setMyDraftNoteCount(count: number) {
      this.currentUser.myDraftNoteCount = count
    },
    setScreenReaderAlert(screenReaderAlert: any) {
      this.screenReaderAlert = {
        message: screenReaderAlert.message,
        politeness: screenReaderAlert.politeness || 'polite'
      }
    },
    setServiceAnnouncement(data: any) {
      this.announcement = data
    },
    updateCurrentUserPreference(key, value) {
      this.currentUser.preferences[key] = value
    },
    updateMyCohort(updatedCohort: any) {
      const cohort = this.currentUser.myCohorts.find(cohort => cohort.id === +updatedCohort.id)
      Object.assign(cohort, updatedCohort)
    },
    updateMyCuratedGroup(updatedCuratedGroup: any) {
      const group = this.currentUser.myCuratedGroups.find(group => group.id === +updatedCuratedGroup.id)
      Object.assign(group, updatedCuratedGroup)
    }
  }
})
