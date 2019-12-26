<script>
import _ from 'lodash';
import Vue from 'vue';

export default {
  name: 'Berkeley',
  methods: {
    isSupervisorOnCall: (advisor, deptCode) => {
      return !!_.find(advisor.dropInAdvisorStatus, (status) => {
        return status.deptCode === deptCode && status.supervisorOnCall;
      });
    },
    myDeptCodes: (roles) => {
      return _.map(_.filter(Vue.prototype.$currentUser.departments, d => _.findIndex(roles, role => d[role]) > -1), 'code');
    },
    previousSisTermId(termId) {
      let previousTermId = '';
      let strTermId = termId.toString();
      switch (strTermId.slice(3)) {
        case '2':
          previousTermId =
            (parseInt(strTermId.slice(0, 3), 10) - 1).toString() + '8';
          break;
        case '5':
          previousTermId = strTermId.slice(0, 3) + '2';
          break;
        case '8':
          previousTermId = strTermId.slice(0, 3) + '5';
          break;
        default:
          break;
      }
      return previousTermId;
    },
    setWaitlistedStatus(course) {
      _.each(course.sections, function(section) {
        course.waitlisted =
          course.waitlisted || section.enrollmentStatus === 'W';
      });
    },
    termNameForSisId(termId) {
      let termName = '';
      if (termId) {
        const strTermId = termId.toString();
        termName = '20' + strTermId.slice(1, 3);
        switch (strTermId.slice(3)) {
          case '2':
            termName = 'Spring ' + termName;
            break;
          case '5':
            termName = 'Summer ' + termName;
            break;
          case '8':
            termName = 'Fall ' + termName;
            break;
          default:
            break;
        }
      }
      return termName;
    }
  }
};
</script>
