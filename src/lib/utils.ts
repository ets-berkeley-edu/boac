import numeral from 'numeral'
import {concat, find, head, initial, isNil, isNumber, join, last, noop, toLower, trim} from 'lodash'
import {getUserProfile} from '@/api/user'
import {nextTick} from 'vue'
import {useContextStore} from '@/stores/context'

export function alertScreenReader(message: string, politeness?: string) {
  useContextStore().setScreenReaderAlert({message: ''})
  nextTick(() => {
    useContextStore().setScreenReaderAlert({message, politeness})
  }).then(noop)
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
  let decoded: any = undefined
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

export function getDegreeCheckPath(student) {
  const currentUser = useContextStore().currentUser
  const currentDegreeCheck = find(student.degreeChecks, 'isCurrent')
  if (currentDegreeCheck) {
    return `/student/degree/${currentDegreeCheck.id}`
  } else if (currentUser.canEditDegreeProgress) {
    return `${studentRoutePath(student.uid, currentUser.inDemoMode)}/degree/create`
  } else {
    return `${studentRoutePath(student.uid, currentUser.inDemoMode)}/degree/history`
  }
}

export function invokeIfAuthenticated(callback: Function, onReject = () => {}) {
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
  return (`${substitutions[count] || substitutions['other'] || count} ` + (count !== 1 ? `${noun}${pluralSuffix}` : noun))
}

// eslint-disable-next-line no-undef
export function putFocusNextTick(id: string, {scroll=true, scrollBlock='center', cssSelector=undefined}: {scroll?: Boolean, scrollBlock?: ScrollLogicalPosition, cssSelector?: string}={}) {
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

export function setPageTitle(phrase: string) {
  document.title = `${phrase ? decodeHtml(phrase) : 'UC Berkeley'} | BOA`
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
        numeric: true
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

export function toBoolean(value: any) {
  return value && value !== 'false'
}

export function toInt(value, defaultValue = null) {
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
