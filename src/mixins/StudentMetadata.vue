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
        ((user.isAsc && !student.athleticsProfile.isActiveAsc) ||
          (user.isCoe && !student.coeProfile.isActiveCoe))
      );
    },
    isAlertGrade(grade) {
      return grade && this.$options.alertGrades.test(grade);
    },
    lastActivityDays(analytics) {
      let timestamp = parseInt(
        _.get(analytics, 'lastActivity.student.raw'),
        10
      );
      if (!timestamp || isNaN(timestamp)) {
        return 'Never';
      }
      // Days tick over at midnight according to the user's browser.
      let daysSince = Math.round(
        new Date().setHours(0, 0, 0, 0) -
          new Date(timestamp * 1000).setHours(0, 0, 0, 0) / 86400000
      );
      switch (daysSince) {
        case 0:
          return 'Today';
        case 1:
          return 'Yesterday';
        default:
          return daysSince + ' days ago';
      }
    },
    setSortableName: student =>
      (student.sortableName = student.lastName + ', ' + student.firstName)
  }
};
</script>
