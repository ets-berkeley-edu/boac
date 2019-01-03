<script>
import store from '@/store';
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'CohortEditSession',
  methods: {
    initSession(id) {
      return new Promise(resolve =>
        store.dispatch('cohortEditSession/init', id).then(resolve)
      );
    },
    ...mapActions('cohortEditSession', [
      'addFilter',
      'removeFilter',
      'readyForSave',
      'setPageMode',
      'toggleCompactView'
    ])
  },
  computed: {
    ...mapGetters('cohortEditSession', [
      'cohortId',
      'cohortName',
      'filters',
      'isOwnedByCurrentUser',
      'isCompactView',
      'menu',
      'pageMode',
      'students',
      'totalStudentCount'
    ])
  }
};
</script>
