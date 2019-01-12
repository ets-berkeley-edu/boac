<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'CohortEditSession',
  methods: {
    ...mapActions('cohortEditSession', [
      'addFilter',
      'applyFilters',
      'createCohort',
      'init',
      'removeFilter',
      'renameCohort',
      'saveExistingCohort',
      'setCurrentPage',
      'setEditMode',
      'toggleCompactView',
      'updateExistingFilter'
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
