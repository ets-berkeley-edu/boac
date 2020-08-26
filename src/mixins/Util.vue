<script>
import _ from 'lodash'
import numeral from 'numeral'

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

const toBoolean = (value) => {
  if (!value || value === 'false') {
    return false
  } else {
    return true
  }
}

export default {
  name: 'Util',
  methods: {
    assign: _.assign,
    capitalize: _.capitalize,
    clone: _.clone,
    cloneDeep: _.cloneDeep,
    concat: _.concat,
    debounce: _.debounce,
    each: _.each,
    escapeForRegExp: s => s && s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'),
    extend: _.extend,
    filterList: _.filter,
    find: _.find,
    findIndex: _.findIndex,
    flatMap: _.flatMap,
    flatten: _.flatten,
    focusModalById: id => document.getElementById(id) && document.getElementById(id).focus(),
    get: _.get,
    groupBy: _.groupBy,
    groupObjectsBy: (objects, property) => {
      const groupings = {}
      _.each(objects, object => {
        const key = object[property]
        if (!_.has(groupings, key)) {
          groupings[key] = []
        }
        groupings[key].push(object)
      })
      return groupings
    },
    has: _.has,
    includes: _.includes,
    indexOf: _.indexOf,
    inRange: _.inRange,
    isEmpty: _.isEmpty,
    isEqual: _.isEqual,
    isNaN: _.isNaN,
    isNil: _.isNil,
    isNumber: _.isNumber,
    isString: _.isString,
    isUndefined: _.isUndefined,
    join: _.join,
    keys: _.keys,
    map: _.map,
    mapValues: _.mapValues,
    merge: _.merge,
    multiply: _.multiply,
    noop: _.noop,
    numFormat: (num, format=null) => numeral(num).format(format),
    orderBy: _.orderBy,
    oxfordJoin: arr => {
      switch(arr.length) {
      case 1: return _.head(arr)
      case 2: return `${_.head(arr)} and ${_.last(arr)}`
      default: return _.join(_.concat(_.initial(arr), ` and ${_.last(arr)}`), ', ')
      }
    },
    partition: _.partition,
    pluralize: (noun, count, substitutions = {}, pluralSuffix = 's') => {
      return (`${substitutions[count] || substitutions['other'] || count} ` + (count !== 1 ? `${noun}${pluralSuffix}` : noun))
    },
    putFocusNextTick(id, cssSelector = null) {
      this.$nextTick(() => {
        let counter = 0
        const putFocus = setInterval(() => {
          let el = document.getElementById(id)
          el = el && cssSelector ? el.querySelector(cssSelector) : el
          el && el.focus()
          if (el || ++counter > 3) {
            // Abort after success or three attempts
            clearInterval(putFocus)
          }
        }, 500)
      })
    },
    pull: _.pull,
    reduce: _.reduce,
    remove: _.remove,
    round: (value, decimals) => (Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)).toFixed(decimals),
    set: _.set,
    setPageTitle: phrase => (document.title = `${phrase ? decodeHtml(phrase) : 'UC Berkeley'} | BOA`),
    size: _.size,
    slice: _.slice,
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
    split: _.split,
    startsWith: _.startsWith,
    stripAnchorRef: fullPath => _.split(fullPath, '#', 1)[0],
    stripHtmlAndTrim: html => {
      let text = html && html.replace(/<([^>]+)>/ig,'')
      text = text && text.replace(/&nbsp;/g, '')
      return _.trim(text)
    },
    studentRoutePath: (uid, inDemoMode) => inDemoMode ? `/student/${window.btoa(uid)}` : `/student/${uid}`,
    toBoolean,
    toInt,
    toString: _.toString,
    trim: _.trim,
    truncate: _.truncate,
    union: _.union,
    unionBy: _.unionBy,
    uniq: _.uniq,
    uniqBy: _.uniqBy,
    upperCase: _.upperCase,
    upperFirst: _.upperFirst,
    without: _.without,
    xor: _.xor,
    xorBy: _.xorBy
  }
}
</script>
