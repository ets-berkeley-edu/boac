import _ from 'lodash'
import Vue from 'vue'

export function oxfordJoin(arr, zeroString) {
  switch((arr || []).length) {
  case 0: return _.isNil(zeroString) ? '' : zeroString
  case 1: return _.head(arr)
  case 2: return `${_.head(arr)} and ${_.last(arr)}`
  default: return _.join(_.concat(_.initial(arr), `and ${_.last(arr)}`), ', ')
  }
}

export function putFocusNextTick(id: string, cssSelector?: string) {
  Vue.nextTick(() => {
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
