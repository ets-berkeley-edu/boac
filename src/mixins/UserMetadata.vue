<script>
import _ from 'lodash';
import store from '@/store';

// If you must bind a user attribute to a form input field then declare it in data block below.
export default {
  name: 'UserMetadata',
  data: () => ({
    inDemoMode: null
  }),
  created() {
    this.inDemoMode = _.get(store.getters, 'user.inDemoMode');
  },
  computed: {
    user: () => store.getters.user
  }
};
</script>
