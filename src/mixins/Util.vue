<script>
import _ from 'lodash';

const toInt = (value, defaultValue = null) => {
  const parsed = parseInt(value, 10);
  return Number.isInteger(parsed) ? parsed : defaultValue;
};

export default {
  name: 'Util',
  methods: {
    assign: _.assign,
    clone: _.clone,
    cloneDeep: _.cloneDeep,
    concat: _.concat,
    debounce: _.debounce,
    each: _.each,
    extend: _.extend,
    filterList: _.filter,
    find: _.find,
    findIndex: _.findIndex,
    flatten: _.flatten,
    focusModalById: id =>
      document.getElementById(id) && document.getElementById(id).focus(),
    get: _.get,
    has: _.has,
    includes: _.includes,
    inRange: _.inRange,
    isEmpty: _.isEmpty,
    isNil: _.isNil,
    isNumber: _.isNumber,
    isUndefined: _.isUndefined,
    join: _.join,
    keys: _.keys,
    map: _.map,
    mapValues: _.mapValues,
    merge: _.merge,
    multiply: _.multiply,
    noop: _.noop,
    orderBy: _.orderBy,
    oxfordJoin: arr => {
      switch(arr.length) {
        case 1: return _.head(arr);
        case 2: return `${_.head(arr)} and ${_.last(arr)}`
        default: return _.join(_.concat(_.initial(arr), `and ${_.last(arr)}`));
      }
    },
    partition: _.partition,
    putFocusNextTick(id, cssSelector = null) {
      this.$nextTick(() => {
        let counter = 0;
        const putFocus = setInterval(() => {
          let el = document.getElementById(id);
          el = el && cssSelector ? el.querySelector(cssSelector) : el;
          el && el.focus();
          if (el || ++counter > 3) {
            // Abort after success or three attempts
            clearInterval(putFocus);
          }
        }, 500);
      });
    },
    remove: _.remove,
    set: _.set,
    setPageTitle: phrase =>
      (document.title = `${phrase || 'UC Berkeley'} | BOA`),
    size: _.size,
    slice: _.slice,
    sortComparator: (a, b) => {
      if (_.isNil(a) || _.isNil(b)) {
        return _.isNil(a) ? (_.isNil(b) ? 0 : -1) : 1;
      } else if (_.isNumber(a) && _.isNumber(b)) {
        return a < b ? -1 : a > b ? 1 : 0
      } else {
        const aInt = toInt(a);
        const bInt = toInt(b);
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
    stripHtmlAndTrim: html => {
      let text = html && html.replace(/<([^>]+)>/ig,"");
      text = text && text.replace(/&nbsp;/g, '');
      return _.trim(text);
    },
    studentRoutePath: (uid, inDemoMode) => inDemoMode ? `/student/${window.btoa(uid)}` : `/student/${uid}`,
    toInt,
    toString: _.toString,
    trim: _.trim,
    truncate: _.truncate,
    union: _.union,
    uniq: _.uniq,
    without: _.without
  }
};
</script>
