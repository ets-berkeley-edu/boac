<script>
import _ from 'lodash';
import store from '@/store';

export default {
  name: 'UserMetadata',
  computed: {
    inDemoMode() {
      return _.get(store.getters, 'user.inDemoMode');
    }
  }
};
</script>
