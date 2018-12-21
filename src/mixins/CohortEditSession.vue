<script>
import store from '@/store';
import { mapGetters, mapMutations } from 'vuex';

export default {
  name: 'CohortEditSession',
  methods: {
    initSession: id =>
      new Promise(resolve =>
        store.dispatch('cohortEditSession/init', id).then(resolve)
      ),
    ...mapMutations('cohortEditSession', [
      'removeFilter',
      'toggleShowFilters',
      'toggleRenameMode'
    ])
  },
  computed: {
    ...mapGetters('cohortEditSession', [
      'cohortId',
      'cohortName',
      'getFilterId',
      'isOwnedByCurrentUser',
      'filters',
      'students',
      'totalStudentCount',
      'renameMode',
      'searchingMode',
      'showFiltersMode'
    ])
  }
};
</script>
