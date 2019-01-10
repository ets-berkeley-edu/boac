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
    size: _.size
  }
};
</script>
