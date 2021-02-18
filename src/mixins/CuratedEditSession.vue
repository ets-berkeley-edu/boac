<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'CuratedEditSession',
  computed: {
    ...mapGetters('curatedEditSession', [
      'curatedGroupId',
      'curatedGroupName',
      'itemsPerPage',
      'mode',
      'ownerId',
      'pageNumber',
      'referencingCohortIds',
      'students',
      'totalStudentCount'
    ])
  },
  methods: {
    ...mapActions('curatedEditSession', [
      'addStudents',
      'goToPage',
      'init',
      'removeStudent',
      'renameCuratedGroup',
      'setMode'
    ])
  }
}
</script>
