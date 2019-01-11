<script>
import _ from 'lodash';

export default {
  name: 'Util',
  methods: {
    cloneDeep: _.cloneDeep,
    extend: _.extend,
    find: _.find,
    flatten: _.flatten,
    get: _.get,
    isEmpty: _.isEmpty,
    isNil: _.isNil,
    mapValues: _.mapValues,
    trim: _.trim,
    scrollTo(id) {
      const e = document.getElementById(id);
      if (e) {
        window.scrollTo(0, e.offsetTop);
      }
    },
    size: _.size
  }
};
</script>
