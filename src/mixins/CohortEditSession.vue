<script>
import {mapActions, mapGetters, mapMutations} from 'vuex'

export default {
  name: 'CohortEditSession',
  computed: {
    ...mapGetters('cohort', [
      'cohortId',
      'cohortName',
      'cohortOwner',
      'domain',
      'editMode',
      'filterOptionGroups',
      'filters',
      'isCompactView',
      'isModifiedSinceLastSearch',
      'isOwnedByCurrentUser',
      'pagination',
      'showApplyButton',
      'showSaveButton',
      'showSortBy',
      'students',
      'totalStudentCount'
    ])
  },
  methods: {
    ...mapActions('cohort', [
      'addFilter',
      'createCohort',
      'downloadCsvPerFilters',
      'removeFilter',
      'renameCohort',
      'resetFiltersToLastApply',
      'resetFiltersToSaved',
      'saveExistingCohort',
      'updateExistingFilter'
    ]),
    ...mapMutations('cohort', [
      'resetSession',
      'setCompactView',
      'setCurrentPage',
      'setDomain',
      'setEditMode',
      'setModifiedSinceLastSearch',
      'stashOriginalFilters',
      'toggleCompactView',
    ])
  }
}
</script>
