<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'CohortEditSession',
  computed: {
    ...mapGetters('cohortEditSession', [
      'cohortId',
      'cohortName',
      'cohortOwner',
      'domain',
      'editMode',
      'filters',
      'isCompactView',
      'isModifiedSinceLastSearch',
      'isOwnedByCurrentUser',
      'menu',
      'pagination',
      'showApplyButton',
      'showSaveButton',
      'showSortBy',
      'students',
      'totalStudentCount'
    ])
  },
  methods: {
    ...mapActions('cohortEditSession', [
      'addFilter',
      'applyFilters',
      'createCohort',
      'downloadCsvPerFilters',
      'init',
      'onPageNumberChange',
      'removeFilter',
      'renameCohort',
      'resetFiltersToLastApply',
      'resetFiltersToSaved',
      'saveExistingCohort',
      'setCurrentPage',
      'setEditMode',
      'toggleCompactView',
      'updateExistingFilter'
    ])
  }
}
</script>
