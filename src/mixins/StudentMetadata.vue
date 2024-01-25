<script>
import _ from 'lodash'
import {myDeptCodes} from '@/berkeley'

export default {
  name: 'StudentMetadata',
  // Grades deserving alerts: D(+/-), F, I, NP, RD.
  alertGrades: /^[DFINR]/,
  methods: {
    displayAsAscInactive(student) {
      return (
        _.includes(myDeptCodes(['advisor', 'director']), 'UWASC') &&
        _.get(student, 'athleticsProfile') &&
        !_.get(student, 'athleticsProfile.isActiveAsc')
      )
    },
    displayAsCoeInactive(student) {
      return (
        _.includes(myDeptCodes(['advisor', 'director']), 'COENG') &&
        _.get(student, 'coeProfile') &&
        !_.get(student, 'coeProfile.isActiveCoe')
      )
    },
    isAlertGrade(grade) {
      return grade && this.$options.alertGrades.test(grade)
    },
    isGraduate(student) {
      return _.get(student, 'sisProfile.level.description') === 'Graduate'
    }
  }
}
</script>
