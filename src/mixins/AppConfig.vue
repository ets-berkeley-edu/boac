<script>
import _ from 'lodash';
import store from '@/store';

export default {
  name: 'AppConfig',
  computed: {
    currentEnrollmentTermId: () =>
      _.get(store.getters.config, 'currentEnrollmentTermId'),
    baseUrl: () => store.state.apiBaseUrl,
    devAuthEnabled: () => _.get(store.getters.config, 'devAuthEnabled'),
    supportEmailAddress: () =>
      _.get(store.getters.config, 'supportEmailAddress')
  }
};
</script>
