<script>
import _ from 'lodash'
import numeral from 'numeral'
import Vue from 'vue'
import {oxfordJoin, putFocusNextTick} from '@/utils'
import {
  assign, capitalize, clone, cloneDeep, compact, concat, debounce, difference, differenceBy, each, eachRight, every,
  extend, filter, find, flatten, get, groupBy, includes, indexOf, inRange, isEmpty, isEqual, isNaN, isNil, isNumber,
  isString, isUndefined, join, keys, map, mapValues, max, merge, noop, omit, orderBy, partition, reject, remove,
  reverse, set, size, slice, some, sortBy, split, startsWith, sumBy, toString, trim, truncate, union, uniq, unset,
  upperCase, upperFirst, values, without, xor, xorBy
} from 'lodash'

const decodeHtml = (snippet) => {
  if (snippet && snippet.indexOf('&') > 0) {
    const el = document.createElement('textarea')
    el.innerHTML = snippet
    return el.value
  } else {
    return snippet
  }
}

const toInt = (value, defaultValue = null) => {
  const parsed = parseInt(value, 10)
  return Number.isInteger(parsed) ? parsed : defaultValue
}

const toBoolean = value => value && value !== 'false'

export default {
  name: 'Util',
  methods: {
    _assign: assign,
    _capitalize: capitalize,
    _clone: clone,
    _cloneDeep: cloneDeep,
    _compact: compact,
    _concat: concat,
    _debounce: debounce,
    _difference: difference,
    _differenceBy: differenceBy,
    _each: each,
    _eachRight: eachRight,
    _every: every,
    _extend: extend,
    _filter: filter,
    _find: find,
    _flatten: flatten,
    _get: get,
    _groupBy: groupBy,
    _includes: includes,
    _indexOf: indexOf,
    _inRange: inRange,
    _isEmpty: isEmpty,
    _isEqual: isEqual,
    _isNaN: isNaN,
    _isNil: isNil,
    _isNumber: isNumber,
    _isString: isString,
    _isUndefined: isUndefined,
    _join: join,
    _keys: keys,
    _map: map,
    _mapValues: mapValues,
    _max: max,
    _merge: merge,
    _noop: noop,
    _omit: omit,
    _orderBy: orderBy,
    _partition: partition,
    _reject: reject,
    _remove: remove,
    _reverse: reverse,
    _set: set,
    _size: size,
    _slice: slice,
    _some: some,
    _sortBy: sortBy,
    _split: split,
    _startsWith: startsWith,
    _sumBy: sumBy,
    _toInt: toInt,
    _toString: toString,
    _trim: trim,
    _truncate: truncate,
    _union: union,
    _uniq: uniq,
    _unset: unset,
    _upperCase: upperCase,
    _upperFirst: upperFirst,
    _values: values,
    _without: without,
    _xor: xor,
    _xorBy: xorBy,
    describeCuratedGroupDomain(domain, capitalize) {
      const format = s => capitalize ? _.capitalize(s) : s
      return format(domain === 'admitted_students' ? 'admissions ' : 'curated ') + format('group')
    },
    escapeForRegExp: s => s && s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'),
    isNilOrBlank: s => _.isNil(s) || _.trim(s) === '',
    lastNameFirst: u => u.lastName && u.firstName ? `${u.lastName}, ${u.firstName}` : (u.lastName || u.firstName),
    nextTick: Vue.nextTick,
    numFormat: (num, format=null) => numeral(num).format(format),
    oxfordJoin,
    pluralize: (noun, count, substitutions = {}, pluralSuffix = 's') => {
      return (`${substitutions[count] || substitutions['other'] || count} ` + (count !== 1 ? `${noun}${pluralSuffix}` : noun))
    },
    putFocusNextTick,
    round: (value, decimals) => (Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)).toFixed(decimals),
    setPageTitle: phrase => (document.title = `${phrase ? decodeHtml(phrase) : 'UC Berkeley'} | BOA`),
    sortComparator: (a, b, nullFirst=true) => {
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
    },
    stripAnchorRef: fullPath => _.split(fullPath, '#', 1)[0],
    stripHtmlAndTrim: html => {
      let text = html && html.replace(/<([^>]+)>/ig,'')
      text = text && text.replace(/&nbsp;/g, '')
      return _.trim(text)
    },
    studentRoutePath: (uid, inDemoMode) => inDemoMode ? `/student/${window.btoa(uid)}` : `/student/${uid}`,
    toBoolean,
    toInt
  }
}
</script>
