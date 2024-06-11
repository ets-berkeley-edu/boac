import {concat, head, initial, isNil, isNumber, join, last, noop, trim} from 'lodash'
import {nextTick} from 'vue'
import numeral from 'numeral'
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

export function isNilOrBlank(s: string | null | undefined) {
  return isNil(s) || trim(s) === ''
}

export function lastNameFirst(u: {firstName?: string, lastName?: string}) {
  return u.lastName && u.firstName ? `${u.lastName}, ${u.firstName}` : (u.lastName || u.firstName || '')
}

export function numFormat(num, format=null) {
  numeral(num).format(format)
}

export function oxfordJoin(arr, zeroString) {
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
export function putFocusNextTick(id: string, cssSelector?: string) {
  nextTick(() => {
    let counter = 0
    const putFocus = setInterval(() => {
      let el = document.getElementById(id)
      el = el && cssSelector ? el.querySelector(cssSelector) : el
      el && el.focus()
      if (el || ++counter > 5) {
        // Abort after success or three attempts
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

export function scroll(anchor) {
  location.hash = `#${anchor}`
}

export function scrollTo(anchor) {
  scroll(anchor)
}

export function scrollToTop() {
  window.scrollTo(0, 0)
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

export function toInt(value, defaultValue = null) {
  const parsed = parseInt(value, 10)
  return Number.isInteger(parsed) ? parsed : defaultValue
}
