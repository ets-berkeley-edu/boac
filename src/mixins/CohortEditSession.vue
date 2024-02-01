<script>
import {mapGetters, mapMutations} from 'vuex'

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
    ...mapMutations('cohort', [
      'addFilter',
      'removeFilter',
      'renameCohort',
      'resetSession',
      'restoreOriginalFilters',
      'setCompactView',
      'setCurrentPage',
      'setDomain',
      'setEditMode',
      'setModifiedSinceLastSearch',
      'stashOriginalFilters',
      'toggleCompactView',
      'updateExistingFilter'
    ])
  }
}
</script>
