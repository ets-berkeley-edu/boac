<script>
import _ from 'lodash'
import Context from '@/mixins/Context'

export default {
  name: 'MatrixUtil',
  mixins: [Context],
  methods: {
    exceedsMatrixThreshold(studentCount) {
      return (
        parseInt(studentCount, 10) >
        parseInt(this.$config.disableMatrixViewThreshold, 10)
      )
    },
    getPlottableProperty(obj, prop) {
      if (_.has(obj, prop + '.percentile')) {
        return _.get(obj, prop + '.percentile')
      }
      return _.get(obj, prop)
    },
    hasPlottableProperty(obj, prop) {
      // In the case of cumulative GPA, zero indicates missing data rather than a real zero.
      if (prop === 'cumulativeGPA') {
        return !!this.getPlottableProperty(obj, prop)
      }
      return _.isFinite(this.getPlottableProperty(obj, prop))
    },
    partitionPlottableStudents() {
      var xAxisMeasure =
        _.get(this, 'selectedAxes.x') || 'analytics.currentScore'
      var yAxisMeasure = _.get(this, 'selectedAxes.y') || 'cumulativeGPA'
      return _.partition(
        this.section.students,
        student =>
          this.hasPlottableProperty(student, xAxisMeasure) &&
          this.hasPlottableProperty(student, yAxisMeasure)
      )
    }
  }
}
</script>
