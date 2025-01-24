import numeral from 'numeral'
import {Cohort, CuratedGroup} from '@/lib/cohort'
import {concat, head, initial, isNil, isNumber, join, last, toLower, trim} from 'lodash'
import {getUserProfile} from '@/api/user'
import {nextTick} from 'vue'
import {useContextStore} from '@/stores/context'

export type BoaConfig = {
  academicStandingDescriptions: object,
  apiBaseUrl: string,
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
  notesDraftAutoSaveInterval: number,
  supportEmailAddress: string,
  timezone: string
}

export type Course = {
  sections: Section[],
  waitlisted: boolean
}

export type CurrentUser = {
  canAccessAdmittedStudents: boolean,
  canAccessAdvisingData: boolean,
  canAccessCanvasData: boolean,
  canEditDegreeProgress: boolean,
  canReadDegreeProgress: boolean,
  departments: Department[],
  inDemoMode: boolean,
  isAdmin: boolean,
  isAuthenticated: boolean,
  isDemoModeAvailable: boolean,
  myCohorts: Cohort[],
  myCuratedGroups: CuratedGroup[],
  myDraftNoteCount: number | undefined,
  preferences: {
    termId: string | undefined
  },
  title: string,
  uid: string
}

export type Department = {
  code: string,
  role?: string
}

export type ExportListOption = {
  text: string,
  value: string,
  disabled?: boolean
}

export type Pagination = {
  currentPage: number,
  itemsPerPage: number
}

export type ScreenReaderAlert = {
  message: string,
  politeness: string
}

export type Section = {
  enrollmentStatus: string,
  gradingBasis: string,
  incompleteComments: string,
  incompleteLapseGradeDate: string,
  incompleteStatusCode: string
}

export type ServiceAnnouncement = {
  isPublished: boolean,
  text: string
}

export type Student = {
  sid: string
}

let $_screenReaderAlertExpiry: number

const clearScreenReaderAlert = () => {
  window.clearInterval($_screenReaderAlertExpiry)
  useContextStore().setScreenReaderAlert({message: ''} as ScreenReaderAlert)
}

export function alertScreenReader(message: string, persistent?: boolean, politeness?: string) {
  clearScreenReaderAlert()
  nextTick(() => {
    useContextStore().setScreenReaderAlert({message, politeness} as ScreenReaderAlert)
    window.clearInterval($_screenReaderAlertExpiry)
    if (!persistent) {
      $_screenReaderAlertExpiry = window.setInterval(clearScreenReaderAlert, 5000)
    }
  })
}

const decodeHtml = (snippet: string) => {
  if (snippet && snippet.indexOf('&') > 0) {
    const el = document.createElement('textarea')
    el.innerHTML = snippet
    return el.value
  } else {
    return snippet
  }
}

export function decodeStudentUriAnchor() {
  let decoded: (object | undefined) = undefined
  const anchor = location.hash
  if (anchor) {
    const match = anchor.match(/^#permalink-(\w+)-([\d\w-]+)/)
    if (match && match.length > 2) {
      decoded = {
        messageType: match[1].toLowerCase(),
        messageId: match[2]
      }
    }
  }
  return decoded
}

export function escapeForRegExp(s) {
  return s && s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

export function goToStudentDegreeChecks(uid: string): void {
  window.open(`${useContextStore().config.apiBaseUrl}/api/degree/student/${uid}/redirect`)
}

export function invokeIfAuthenticated(callback: () => void, onReject = () => {}) {
  return getUserProfile().then(data => {
    if (data.isAuthenticated) {
      callback()
    } else {
      onReject()
    }
  })
}

export function isNilOrBlank(s: string | null | undefined) {
  return isNil(s) || trim(s) === ''
}

export function lastNameFirst(u: {firstName?: string, lastName?: string}) {
  return u.lastName && u.firstName ? `${u.lastName}, ${u.firstName}` : (u.lastName || u.firstName || '')
}

export function normalizeId(id: string) {
  return toLower(id).replace(/\W/g, ' ').trim().replace(/ +/g, '-')
}

export function numFormat(num, format=null) {
  return numeral(num).format(format)
}

export function oxfordJoin(arr, zeroString?) {
  switch((arr || []).length) {
    case 0: return isNil(zeroString) ? '' : zeroString
    case 1: return head(arr)
    case 2: return `${head(arr)} and ${last(arr)}`
    default: return join(concat(initial(arr), `and ${last(arr)}`), ', ')
  }
}

export function pluralize(noun: string, count: number, substitutions = {}, pluralSuffix = 's') {
  return (`${substitutions[count] || substitutions['other'] || count.toLocaleString()} ` + (count !== 1 ? `${noun}${pluralSuffix}` : noun))
}

// eslint-disable-next-line no-undef
export function putFocusNextTick(id: string, {scroll=true, scrollBlock='center', cssSelector=undefined}: {scroll?: boolean, scrollBlock?: ScrollLogicalPosition, cssSelector?: string}={}) {
  nextTick(() => {
    let counter = 0
    const putFocus = setInterval(() => {
      let el = document.getElementById(id)
      el = el && cssSelector ? el.querySelector(cssSelector) : el
      if (el) {
        el.classList.add('scroll-margins')
        el.focus()
        if (scroll) {
          el.scrollIntoView({behavior: 'smooth', block: scrollBlock})
        }
      }
      if (el || ++counter > 5) {
        // Abort after success or five attempts
        clearInterval(putFocus)
      }
    }, 500)
  })
}

export function round(value: number, decimals: number) {
  return (Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)).toFixed(decimals)
}

export function setPageTitle(phrase: string): void {
  const title: string = phrase && decodeHtml(phrase)
  document.title = `${title || 'UC Berkeley'} | BOA`
}

// eslint-disable-next-line no-undef
export function scrollTo(anchor: string, scrollBlock?: ScrollLogicalPosition) {
  nextTick(() => {
    const element = document.getElementById(anchor)
    if (element) {
      element.classList.add('scroll-margins')
      element.scrollIntoView({behavior: 'smooth', block: scrollBlock || 'center'})
    }
  })
}

export function scrollToTop() {
  scrollTo('content', 'start')
}

export function setComboboxAccessibleLabel(container: Element, label: string) {
  // Vuetify puts a label on the <input> element inside the combobox, but the combobox itself
  // is unlabeled. As a result, JAWS lists it as "Unlabeled1 edit combo {input label}". This
  // workaround replaces "Unlabeled1" with the provided label.
  const combobox = container.querySelector('[role="combobox"]')
  if (combobox) {
    combobox.setAttribute('aria-label', label)
  }
}

export function sortComparator(a, b, nullFirst=true) {
  if (isNil(a) || isNil(b)) {
    if (nullFirst) {
      return isNil(a) ? (isNil(b) ? 0 : -1) : 1
    } else {
      return isNil(b) ? (isNil(a) ? 0 : -1) : 1
    }
  } else if (isNumber(a) && isNumber(b)) {
    return a < b ? -1 : a > b ? 1 : 0
  } else {
    const aInt = toInt(a)
    const bInt = toInt(b)
    if (aInt && bInt) {
      return aInt < bInt ? -1 : aInt > bInt ? 1 : 0
    } else {
      return a.toString().localeCompare(b.toString(), undefined, {
        numeric: true,
        usage: 'sort'
      })
    }
  }
}

export function stripHtmlAndTrim(html) {
  let text = html && html.replace(/<([^>]+)>/ig,'')
  text = text && text.replace(/&nbsp;/g, '')
  return trim(text)
}

export function studentRoutePath(uid: string, inDemoMode: boolean) {
  return inDemoMode ? `/student/${window.btoa(uid)}` : `/student/${uid}`
}

export function toBoolean(value: string) {
  return value && value !== 'false'
}

export function toInt(value: string, defaultValue: number = NaN): number {
  const parsed = parseInt(value, 10)
  return Number.isInteger(parsed) ? parsed : defaultValue
}

export function updateWindowLocationParam(key: string, value: string) {
  const url = new URL(window.location.toString())
  const params = new URLSearchParams(url.search)
  params.set(key, value)
  url.search = params.toString()
  window.history.pushState({}, '', url)
}
