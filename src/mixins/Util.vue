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
    flatten: _.flatten,
    get: _.get,
    inRange: _.inRange,
    isEmpty: _.isEmpty,
    isNil: _.isNil,
    map: _.map,
    mapValues: _.mapValues,
    orderBy: _.orderBy,
    remove: _.remove,
    size: _.size,
    trim: _.trim
  }
};
</script>
