<script>
import _ from 'lodash'
import numeral from 'numeral'
import {nextTick} from 'vue'
import {oxfordJoin, putFocusNextTick, stripHtmlAndTrim, toInt} from '@/lib/utils'
import {
  assign, capitalize, clone, cloneDeep, compact, concat, debounce, difference, differenceBy, each, eachRight, every,
  extend, filter, find, findIndex, flatten, get, groupBy, includes, indexOf, inRange, isEmpty, isEqual, isNaN, isNil, isNumber,
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
    _findIndex: findIndex,
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
    escapeForRegExp: s => s && s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'),
    isNilOrBlank: s => _.isNil(s) || _.trim(s) === '',
    lastNameFirst: u => u.lastName && u.firstName ? `${u.lastName}, ${u.firstName}` : (u.lastName || u.firstName),
    nextTick,
    numFormat: (num, format=null) => numeral(num).format(format),
    oxfordJoin,
    pluralize: (noun, count, substitutions = {}, pluralSuffix = 's') => {
      return (`${substitutions[count] || substitutions['other'] || count} ` + (count !== 1 ? `${noun}${pluralSuffix}` : noun))
    },
    putFocusNextTick,
    round: (value, decimals) => (Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)).toFixed(decimals),
    setPageTitle: phrase => (document.title = `${phrase ? decodeHtml(phrase) : 'UC Berkeley'} | BOA`),
    stripHtmlAndTrim,
    studentRoutePath: (uid, inDemoMode) => inDemoMode ? `/student/${window.btoa(uid)}` : `/student/${uid}`,
    toBoolean: value => value && value !== 'false',
    toInt
  }
}
</script>
