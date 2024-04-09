import _ from 'lodash'
import {nextTick} from 'vue'
import numeral from 'numeral'

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
  return _.isNil(s) || _.trim(s) === ''
}

export function numFormat(num, format=null) {
  numeral(num).format(format)
}

export function oxfordJoin(arr, zeroString) {
  switch((arr || []).length) {
    case 0: return _.isNil(zeroString) ? '' : zeroString
    case 1: return _.head(arr)
    case 2: return `${_.head(arr)} and ${_.last(arr)}`
    default: return _.join(_.concat(_.initial(arr), `and ${_.last(arr)}`), ', ')
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

export function setPageTitle(phrase: string) {
  document.title = `${phrase ? decodeHtml(phrase) : 'UC Berkeley'} | BOA`
}

export function scroll(anchor) {
  // TODO: Implement anchor
  console.log(`TODO: Scroll to ${anchor}`)
  window.scrollTo(0, 0)
}

export function scrollTo(anchor) {
  scroll(anchor)
}

export function scrollToTop() {
  window.scrollTo(0, 0)
}

export function sortComparator(a, b, nullFirst=true) {
  if (_.isNil(a) || _.isNil(b)) {
    if (nullFirst) {
      return _.isNil(a) ? (_.isNil(b) ? 0 : -1) : 1
    } else {
      return _.isNil(b) ? (_.isNil(a) ? 0 : -1) : 1
    }
  } else if (_.isNumber(a) && _.isNumber(b)) {
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
  return _.trim(text)
}

export function toInt(value, defaultValue = null) {
  const parsed = parseInt(value, 10)
  return Number.isInteger(parsed) ? parsed : defaultValue
}
