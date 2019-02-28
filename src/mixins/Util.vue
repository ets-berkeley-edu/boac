<script>
import _ from 'lodash';

export default {
  name: 'Util',
  methods: {
    assign: _.assign,
    cloneDeep: _.cloneDeep,
    concat: _.concat,
    each: _.each,
    extend: _.extend,
    filterList: _.filter,
    find: _.find,
    findIndex: _.findIndex,
    flatten: _.flatten,
    focusModalById: id =>
      document.getElementById(id) && document.getElementById(id).focus(),
    forceUniquePath: routePath => `${routePath}?_=${new Date().getTime()}`,
    get: _.get,
    has: _.has,
    includes: _.includes,
    inRange: _.inRange,
    isEmpty: _.isEmpty,
    isNil: _.isNil,
    isUndefined: _.isUndefined,
    keys: _.keys,
    map: _.map,
    mapValues: _.mapValues,
    merge: _.merge,
    orderBy: _.orderBy,
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
    setPageTitle: phrase =>
      (document.title = `${phrase || 'UC Berkeley'} | BOAC`),
    size: _.size,
    slice: _.slice,
    split: _.split,
    toInt: (value, defaultValue = null) => {
      const parsed = parseInt(value, 10);
      return Number.isInteger(parsed) ? parsed : defaultValue;
    },
    trim: _.trim,
    truncate: _.truncate,
    uniq: _.uniq,
    without: _.without
  }
};
</script>
