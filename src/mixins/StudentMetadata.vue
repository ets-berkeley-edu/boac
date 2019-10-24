<script>
import _ from 'lodash';
import UserMetadata from '@/mixins/UserMetadata';

export default {
  name: 'StudentMetadata',
  mixins: [UserMetadata],
  // Grades deserving alerts: D(+/-), F, I, NP.
  alertGrades: /^[DFIN]/,
  methods: {
    displayAsAscInactive(student) {
      return (
        _.includes(this.myDeptCodes(['isAdvisor', 'isDirector']), 'UWASC') &&
        _.get(student, 'athleticsProfile') &&
        !_.get(student, 'athleticsProfile.isActiveAsc')
      );
    },
    displayAsCoeInactive(student) {
      return (
        _.includes(this.myDeptCodes(['isAdvisor', 'isDirector']), 'COENG') &&
        _.get(student, 'coeProfile') &&
        !_.get(student, 'coeProfile.isActiveCoe')
      );
    },
    isAlertGrade(grade) {
      return grade && this.$options.alertGrades.test(grade);
    }
  }
};
</script>
