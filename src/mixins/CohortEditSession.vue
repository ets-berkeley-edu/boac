<script>
import {mapActions, mapState} from 'pinia'
import {useCohortStore} from '@/stores/cohort-edit-session'

export default {
  name: 'CohortEditSession',
  computed: {
    ...mapState(useCohortStore, [
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
    ...mapActions(useCohortStore, [
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
