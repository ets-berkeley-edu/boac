<script>
import {mapGetters} from 'vuex'

export default {
  name: 'CuratedEditSession',
  computed: {
    ...mapGetters('curatedGroup', [
      'curatedGroupId',
      'curatedGroupName',
      'domain',
      'itemsPerPage',
      'mode',
      'ownerId',
      'pageNumber',
      'referencingCohortIds',
      'students',
      'totalStudentCount'
    ])
  }
}
</script>
