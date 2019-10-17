<script>
import _ from 'lodash';

export default {
  name: 'Berkeley',
  methods: {
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
    sortableStudentsOptions(studentGroup, compact=false) {
      if (studentGroup.studentsWithAlerts && _.size(studentGroup.studentsWithAlerts) === 50) {
        return {
          compact,
          includeCuratedCheckbox: false,
          reverse: true,
          sortBy: 'alertCount'
        };
      } else {
        return {
          compact,
          includeCuratedCheckbox: false,
          reverse: false,
          sortBy: 'name'
        };
      }
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
