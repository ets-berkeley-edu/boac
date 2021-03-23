<script>
import _ from 'lodash'
import Berkeley from '@/mixins/Berkeley'

export default {
  name: 'StudentMetadata',
  mixins: [Berkeley],
  // Grades deserving alerts: D(+/-), F, I, NP, RD.
  alertGrades: /^[DFINR]/,
  methods: {
    displayAsAscInactive(student) {
      return (
        _.includes(this.myDeptCodes(['advisor', 'director']), 'UWASC') &&
        _.get(student, 'athleticsProfile') &&
        !_.get(student, 'athleticsProfile.isActiveAsc')
      )
    },
    displayAsCoeInactive(student) {
      return (
        _.includes(this.myDeptCodes(['advisor', 'director']), 'COENG') &&
        _.get(student, 'coeProfile') &&
        !_.get(student, 'coeProfile.isActiveCoe')
      )
    },
    isAlertGrade(grade) {
      return grade && this.$options.alertGrades.test(grade)
    }
  }
}
</script>
