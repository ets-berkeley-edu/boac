<script>
import _ from 'lodash'
import {getDistinctSids} from '@/api/student'

export default {
  name: 'StudentAggregator',
  data: () => ({
    distinctSids: [],
    isRecalculating: false
  }),
  methods: {
    recalculateStudentCount(sids, cohorts, curatedGroups) {
      this.isRecalculating = true
      return new Promise(resolve => {
        const cohortIds = _.map(cohorts, 'id')
        const curatedGroupIds = _.map(curatedGroups, 'id')
        if (cohortIds.length || curatedGroupIds.length) {
          getDistinctSids(sids, cohortIds, curatedGroupIds).then(data => {
            this.distinctSids = data.sids
          }).finally(() => {
            this.isRecalculating = false
            resolve()
          })
        } else {
          this.distinctSids = _.uniq(sids)
          this.isRecalculating = false
          resolve()
        }
      })
    }
  }
}
</script>
