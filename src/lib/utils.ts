import numeral from 'numeral'
import {concat, head, initial, isNil, isNumber, join, last, toLower, trim} from 'lodash'
import {nextTick} from 'vue'
import type {BoaUser, Cohort, CuratedGroup, HasName, ScreenReaderAlert} from '@/lib/types'
import {getUserProfile} from '@/api/user'
import {useContextStore} from '@/stores/context'

export const ANONYMOUS_USER: BoaUser = {
  id: 0,
  automateDegreeProgressPermission: false,
  campusEmail: '',
  canAccessAdmittedStudents: false,
  canAccessAdvisingData: false,
  canAccessCanvasData: false,
  canAccessPrivateNotes: false,
  canEditDegreeProgress: false,
  canReadDegreeProgress: false,
  createdAt: '',
  csid: '',
  degreeProgressPermission: undefined,
  deletedAt: undefined,
  departments: [],
  email: '',
  firstName: '',
  inDemoMode: false,
  isAdmin: false,
  isAuthenticated: false,
  isBlocked: false,
  isDemoModeAvailable: false,
  isExpiredPerLdap: '',
  lastName: '',
  myCohorts: [] as Cohort[],
  myCuratedGroups: [] as CuratedGroup[],
  myDraftNoteCount: undefined as number | undefined,
  name: undefined,
  preferences: {
    termId: undefined as string | undefined
  },
  title: undefined,
  uid: ''
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

export function capitalizeAllWords(words: string) {
  return words.toLowerCase().split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

const decodeHtml = (snippet: string) => {
  let decoded: string
  if (snippet && snippet.indexOf('&') > 0) {
    const el = document.createElement('textarea')
    el.innerHTML = snippet
    decoded = el.value
  } else {
    decoded = snippet
  }
  return decoded
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

export function goToStudentDegreeChecks(sid: string): void {
  window.open(`${useContextStore().config.apiBaseUrl}/api/degree/student/${sid}/redirect`)
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

export function lastNameFirst(u: HasName): string {
  return u.lastName && u.firstName ? `${u.lastName}, ${u.firstName}` : (u.lastName || u.firstName || '')
}

export function normalizeId(id: string) {
  return toLower(id).replace(/\W/g, ' ').trim().replace(/[ _]+/g, '-')
}

export function numFormat(num, format?: string | null) {
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

export function sortComparator(a, b, nullFirst=true): number {
  let result: number
  if (isNil(a) || isNil(b)) {
    if (nullFirst) {
      result = isNil(a) ? (isNil(b) ? 0 : -1) : 1
    } else {
      result = isNil(b) ? (isNil(a) ? 0 : -1) : 1
    }
  } else if (isNumber(a) && isNumber(b)) {
    result = a < b ? -1 : a > b ? 1 : 0
  } else {
    const aInt = toInt(a)
    const bInt = toInt(b)
    if (aInt && bInt) {
      result = aInt < bInt ? -1 : aInt > bInt ? 1 : 0
    } else {
      result = a.toString().localeCompare(b.toString(), undefined, {
        numeric: true,
        usage: 'sort'
      })
    }
  }
  return result
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

export function toInt(value: string | number, defaultValue: number = NaN): number {
  const parsed = isNumber(value) ? value : parseInt(value, 10)
  return Number.isInteger(parsed) ? parsed : defaultValue
}

export function updateWindowLocationParam(key: string, value: string) {
  const url = new URL(window.location.toString())
  const params = new URLSearchParams(url.search)
  params.set(key, value)
  url.search = params.toString()
  window.history.pushState({}, '', url)
}
