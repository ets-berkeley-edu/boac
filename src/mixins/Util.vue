<script>
import _ from 'lodash';

export default {
  name: 'Util',
  methods: {
    cloneDeep: _.cloneDeep,
    concat: _.concat,
    each: _.each,
    extend: _.extend,
    filterList: _.filter,
    find: _.find,
    focusModalById: id =>
      document.getElementById(id) && document.getElementById(id).focus(),
    flatten: _.flatten,
    get: _.get,
    includes: _.includes,
    inRange: _.inRange,
    isEmpty: _.isEmpty,
    isNil: _.isNil,
    map: _.map,
    mapValues: _.mapValues,
    orderBy: _.orderBy,
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
    trim: _.trim
  }
};
</script>
