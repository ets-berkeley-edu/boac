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
      'removeFilter',
      'renameCohort',
      'resetFiltersToLastApply',
      'resetFiltersToSaved',
      'saveExistingCohort',
      'updateExistingFilter'
    ]),
    ...mapMutations('cohort', [
      'addFilter',
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
