<script>
import _ from 'lodash';

export default {
  name: 'Util',
  methods: {
    cloneDeep: _.cloneDeep,
    concat: _.concat,
    each: _.each,
    extend: _.extend,
    find: _.find,
    filterList: _.filter,
    flatten: _.flatten,
    get: _.get,
    isEmpty: _.isEmpty,
    isNil: _.isNil,
    map: _.map,
    mapValues: _.mapValues,
    orderBy: _.orderBy,
    trim: _.trim,
    size: _.size
  }
};
</script>
