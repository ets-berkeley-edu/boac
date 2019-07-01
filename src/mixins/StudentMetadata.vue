<script>
import _ from 'lodash';
import store from '@/store';

export default {
  name: 'StudentMetadata',
  // Grades deserving alerts: D(+/-), F, I, NP.
  alertGrades: /^[DFIN]/,
  methods: {
    displayAsInactive(student) {
      const user = store.getters['user/user'];
      return (
        user &&
        (
          (user.isAsc && _.get(student, 'athleticsProfile') && !_.get(student, 'athleticsProfile.isActiveAsc')) ||
          (user.isCoe && _.get(student, 'coeProfile') && !_.get(student, 'coeProfile.isActiveCoe'))
        )
      );
    },
    isAlertGrade(grade) {
      return grade && this.$options.alertGrades.test(grade);
    }
  }
};
</script>
