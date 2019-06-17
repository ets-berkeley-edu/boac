<script>
import _ from 'lodash';

export default {
  name: 'HomeUtil',
  methods: {
    getSortOptions(studentGroup) {
      if (studentGroup.studentsWithAlerts && _.size(studentGroup.studentsWithAlerts) === 50) {
        return {
          includeCuratedCheckbox: false,
          reverse: true,
          sortBy: 'alertCount'
        };
      } else {
        return {
          includeCuratedCheckbox: false,
          reverse: false,
          sortBy: 'lastName'
        };
      }
    }
  }
};
</script>
