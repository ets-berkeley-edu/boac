<script>
import _ from 'lodash'

export default {
  name: 'StudentAnalytics',
  methods: {
    lastActivityDays(analytics) {
      const timestamp = parseInt(
        _.get(analytics, 'lastActivity.student.raw'),
        10
      )
      if (!timestamp || isNaN(timestamp)) {
        return 'Never'
      }
      // Days tick over at midnight according to the user's browser.
      const daysSince = Math.round(
        (new Date().setHours(0, 0, 0, 0) -
          new Date(timestamp * 1000).setHours(0, 0, 0, 0)) /
          86400000
      )
      switch (daysSince) {
      case 0:
        return 'Today'
      case 1:
        return 'Yesterday'
      default:
        return daysSince + ' days ago'
      }
    },
    lastActivityInContext(analytics) {
      var describe = ''
      if (analytics.courseEnrollmentCount) {
        var total = analytics.courseEnrollmentCount
        var percentAbove =
          (100 - analytics.lastActivity.student.roundedUpPercentile) / 100
        describe += `${Math.round(
          percentAbove * total
        )} out of ${total} enrolled students have done so more recently.`
      }
      return describe
    }
  }
}
</script>
