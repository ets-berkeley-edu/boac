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
      'applyFilters',
      'createCohort',
      'removeFilter',
      'renameCohort',
      'saveCohort',
      'setCurrentPage',
      'setEditMode',
      'toggleCompactView'
    ])
  },
  computed: {
    ...mapGetters('cohortEditSession', [
      'cohortId',
      'cohortName',
      'editMode',
      'filters',
      'isCompactView',
      'isModifiedSinceLastSearch',
      'isOwnedByCurrentUser',
      'menu',
      'pagination',
      'showApplyButton',
      'showSaveButton',
      'students',
      'totalStudentCount'
    ])
  }
};
</script>
