<script>
import store from '@/store';
import { mapGetters } from 'vuex';

export default {
  name: 'CohortEditSession',
  methods: {
    initSession(id) {
      return new Promise(resolve => {
        store.dispatch('cohortEditSession/init', id).then(resolve);
      });
    },
    remove(filter) {
      store.dispatch('cohortEditSession/removeFilter', filter);
    }
  },
  computed: {
    ...mapGetters('cohortEditSession', [
      'id',
      'isOwnedByCurrentUser',
      'name',
      'filters',
      'students',
      'totalStudentCount'
    ])
  }
};
</script>
