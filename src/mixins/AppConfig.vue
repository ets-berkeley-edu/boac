<script>
import _ from 'lodash';
import store from '@/store';

export default {
  name: 'AppConfig',
  computed: {
    currentEnrollmentTermId: () =>
      _.get(store.getters.config, 'currentEnrollmentTermId'),
    devAuthEnabled: () => _.get(store.getters.config, 'devAuthEnabled'),
    supportEmailAddress: () =>
      _.get(store.getters.config, 'supportEmailAddress')
  }
};
</script>
