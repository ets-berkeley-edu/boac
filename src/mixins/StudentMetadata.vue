<script>
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
        ((user.isAsc && !student.athleticsProfile.isActiveAsc) ||
          (user.isCoe && !student.coeProfile.isActiveCoe))
      );
    },
    isAlertGrade(grade) {
      return grade && this.$options.alertGrades.test(grade);
    },
    setSortableName: student =>
      (student.sortableName = student.lastName + ', ' + student.firstName)
  }
};
</script>
