<script>
import {mapState} from 'pinia'
import {useCuratedGroupStore} from '@/stores/curated-group'

export default {
  name: 'CuratedEditSession',
  computed: {
    ...mapState(useCuratedGroupStore, [
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
