import mitt from 'mitt'
import type {Handler} from 'mitt'
import {defineStore} from 'pinia'
import {each, get, noop, sortBy} from 'lodash'
import {nextTick} from 'vue'
import router from '@/router'
import {ANONYMOUS_USER, alertScreenReader} from '@/lib/utils'
import type {
  BoaConfig,
  BoaUser,
  Cohort,
  CuratedGroup,
  Department,
  PeerAdvisingDepartment,
  ScreenReaderAlert,
  ServiceAnnouncement,
} from '@/lib/types'
import {getDepartments} from '@/api/user'

const $_getDefaultApplicationState = () => ({
  message: undefined as string | undefined,
  stacktrace: undefined as string | undefined | null,
  status: 200
})

let HAS_LAZY_LOADED = false

export const useContextStore = defineStore('context', {
  state: () => ({
    allBerkeleyDepartments: [] as Department[],
    allPeerAdvisingDepartments: [] as PeerAdvisingDepartment[],
    announcement: undefined as ServiceAnnouncement | undefined,
    applicationState: $_getDefaultApplicationState(),
    config: {} as BoaConfig,
    currentUser: ANONYMOUS_USER as BoaUser,
    dismissedFooterAlert: false,
    dismissedServiceAnnouncement: false,
    eventHub: mitt(),
    gaMeasurementId: undefined as string | undefined,
    loading: false,
    loadingStartTime: undefined as number | undefined,
    routeKeyId: 0,
    screenReaderAlert: {
      message: '',
      politeness: 'polite'
    } as ScreenReaderAlert
  }),
  actions: {
    addMyCohort(cohort: Cohort) {
      this.currentUser.myCohorts.push(cohort)
    },
    addMyCuratedGroup(curatedGroup: CuratedGroup) {
      this.currentUser.myCuratedGroups.push(curatedGroup)
      this.currentUser.myCuratedGroups = sortBy(this.currentUser.myCuratedGroups, 'name')
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
      alertScreenReader(srAlert || `${String(get(route, 'name', ''))} page loaded.`, true)
      const callable = () => {
        let element: HTMLElement | null
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
          if (putFocusElementId) {
            element.scrollIntoView({behavior: 'smooth', block: 'start'})
          }
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
      alertScreenReader(srAlert || `${String(get(route, 'name', ''))} page is loading.`, true)
    },
    removeEventHandler(type: string, handler?: Handler) {
      this.eventHub.off(type, handler)
    },
    removeMyCohort(cohortId: number) {
      const indexOf = this.currentUser.myCohorts.findIndex(cohort => cohort.id === cohortId)
      this.currentUser.myCohorts.splice(indexOf, 1)
    },
    resetApplicationState() {
      this.applicationState = $_getDefaultApplicationState()
    },
    restoreServiceAnnouncement() {
      this.dismissedServiceAnnouncement = false
    },
    setApplicationState(status: number, message?: string, stacktrace?: string | null) {
      this.applicationState = {message, stacktrace, status}
    },
    setConfig(data: BoaConfig) {
      this.config = data
    },
    setCurrentUser(currentUser: BoaUser) {
      this.currentUser = currentUser
      // Lazy-load departmental data (and more?) when user is first authenticated.
      if (this.currentUser.isAuthenticated && !HAS_LAZY_LOADED) {
        HAS_LAZY_LOADED = true
        getDepartments().then(data => {
          this.allBerkeleyDepartments = data
          this.allPeerAdvisingDepartments = []
          each(this.allBerkeleyDepartments, (d: Department) => {
            each(d.peerAdvisingDepartments, (p: PeerAdvisingDepartment) => {
              this.allPeerAdvisingDepartments.push({
                ...p,
                ...{
                  deptCode: d.deptCode,
                  deptName: d.deptName,
                  deptId: d.id
                }
              })
            })
          })
          this.allPeerAdvisingDepartments = sortBy(this.allPeerAdvisingDepartments, 'name')
        })
      }
    },
    setDemoMode(inDemoMode: boolean): void {
      this.currentUser.inDemoMode = inDemoMode
    },
    setEventHandler(type: string, handler: Handler) {
      this.eventHub.on(type, handler)
    },
    setMyDraftNoteCount(count: number) {
      this.currentUser.myDraftNoteCount = count
    },
    setRouteKeyId(id: number) {
      this.routeKeyId = id
    },
    setScreenReaderAlert(screenReaderAlert: ScreenReaderAlert) {
      this.screenReaderAlert = {
        message: screenReaderAlert.message,
        politeness: screenReaderAlert.politeness || 'polite'
      }
    },
    setServiceAnnouncement(data: ServiceAnnouncement) {
      this.announcement = data
    },
    updateCurrentUserPreference(key, value) {
      this.currentUser.preferences[key] = value
    },
    updateMyCohort(updatedCohort: Cohort) {
      const cohort = this.currentUser.myCohorts.find((cohort: Cohort) => cohort.id === +updatedCohort.id)
      Object.assign(cohort as Cohort, updatedCohort)
    },
    updateMyCuratedGroup(updatedCuratedGroup: CuratedGroup) {
      const group = this.currentUser.myCuratedGroups.find((group: CuratedGroup) => group.id === +updatedCuratedGroup.id)
      Object.assign(group as CuratedGroup, updatedCuratedGroup)
    }
  }
})
