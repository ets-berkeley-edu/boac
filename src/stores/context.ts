import {get, noop, sortBy} from 'lodash'
import mitt from 'mitt'
import router from '@/router'
import {alertScreenReader} from '@/lib/utils'
import {defineStore} from 'pinia'
import {nextTick} from 'vue'

const $_getDefaultApplicationState = () => ({
  message: undefined,
  stacktrace: undefined,
  status: 200
})

export type BoaConfig = {
  currentEnrollmentTerm: string,
  currentEnrollmentTermId: number,
  defaultTermUnitsAllowed: {
    max: number,
    min: number
  },
  draftNoteSubjectPlaceholder: string,
  fixedWarningOnAllPages: boolean,
  gaMeasurementId: string,
  isProduction: boolean,
  isVueAppDebugMode: boolean,
  maxAttachmentsPerNote: number,
  supportEmailAddress: string,
  timezone: string
}

export type CurrentUser = {
  canAccessAdmittedStudents: boolean,
  canAccessAdvisingData: boolean,
  canAccessCanvasData: boolean,
  canEditDegreeProgress: boolean,
  canReadDegreeProgress: boolean,
  departments: any[],
  inDemoMode: boolean,
  isAdmin: boolean,
  isAuthenticated: boolean,
  isDemoModeAvailable: boolean,
  myCohorts: any[],
  myCuratedGroups: any[],
  myDraftNoteCount: number | undefined,
  preferences: {
    termId: string | undefined
  },
  title: string,
  uid: string
}

export const useContextStore = defineStore('context', {
  state: () => ({
    announcement: undefined,
    applicationState: $_getDefaultApplicationState(),
    config: {} as BoaConfig,
    currentUser: {
      canAccessAdmittedStudents: false,
      canAccessAdvisingData: false,
      canAccessCanvasData: false,
      canEditDegreeProgress: false,
      canReadDegreeProgress: false,
      inDemoMode: false,
      isAdmin: false,
      isAuthenticated: false,
      isDemoModeAvailable: false,
      myCohorts: [] as any[],
      myCuratedGroups: [] as any[],
      myDraftNoteCount: undefined as number | undefined,
      preferences: {
        termId: undefined as string | undefined
      }
    } as CurrentUser,
    dismissedFooterAlert: false,
    dismissedServiceAnnouncement: false,
    eventHub: mitt(),
    gaMeasurementId: undefined as string | undefined,
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
      this.currentUser.myCuratedGroups = sortBy(this.currentUser.myCuratedGroups, 'name')
    },
    alertScreenReader(message: string, politeness='polite') {
      this.screenReaderAlert.message = ''
      nextTick(() => {
        this.screenReaderAlert = {message, politeness}
      }).then(noop)
    },
    broadcast(eventType, data?) {
      this.eventHub.emit(eventType, data)
    },
    dismissFooterAlert() {
      this.dismissedFooterAlert = true
    },
    dismissServiceAnnouncement() {
      this.dismissedServiceAnnouncement = true
    },
    loadingComplete(srAlert?: string, putFocusElementId?: string) {
      if (!get(this.config, 'isProduction')) {
        // eslint-disable-next-line no-console
        console.log(`Page loaded in ${(new Date().getTime() - (this.loadingStartTime || 0)) / 1000} seconds`)
      }
      const route = router.currentRoute.value
      this.loading = false
      alertScreenReader(srAlert || `${String(get(route, 'name', ''))} page loaded.`)
      const callable = () => {
        let element: any
        if (putFocusElementId) {
          element = document.getElementById(putFocusElementId)
        } else {
          element = document.getElementById('page-header')
          if (!element) {
            const elements = document.getElementsByTagName('h1')
            element = elements.length > 0 ? elements[0] : null
          }
        }
        if (element) {
          element.setAttribute('tabindex', '-1')
          element.classList.add('scroll-margins')
          element.focus()
          element.scrollIntoView({behavior: 'smooth', block: 'start'})
        }
        return !!element
      }
      nextTick(() => {
        let counter = 0
        const job = setInterval(() => (callable() || ++counter > 3) && clearInterval(job), 500)
      }).then(noop)
    },
    loadingStart(srAlert?: string) {
      this.loading = true
      this.loadingStartTime = new Date().getTime()
      const route = router.currentRoute.value
      alertScreenReader(srAlert || `${String(get(route, 'name', ''))} page is loading.`)
    },
    removeEventHandler(type: string, handler?: any) {
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
    resetApplicationState() {
      this.applicationState = $_getDefaultApplicationState()
    },
    restoreServiceAnnouncement() {
      this.dismissedServiceAnnouncement = false
    },
    setApplicationState(status: number, message?: any, stacktrace?: any) {
      this.applicationState = {message, stacktrace, status}
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
    setEventHandler(type: string, handler: any) {
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
