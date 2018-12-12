<script>
import _ from 'lodash';
import store from '@/store';

export default {
  name: 'Validator',
  methods: {
    validateCohortName: cohort => {
      const user = store.getters['user/currentUser'];
      const name = _.trim(cohort.name);
      const isReservedName = name =>
        user.isAsc &&
        _.includes(
          ['intensive students', 'inactive students'],
          name.toLowerCase()
        );
      let msg = null;
      if (_.isEmpty(name)) {
        msg = 'Required';
      } else if (_.size(name) > 255) {
        msg = 'Name must be 255 characters or fewer';
      } else if (isReservedName(name)) {
        msg = `Sorry, '${name}' is a reserved name. Please choose a different name.`;
      } else {
        let all = {
          'curated group': store.getters['curated/myCuratedGroups'],
          cohort: store.getters['cohort/myCohorts']
        };
        _.each(all, (cohorts, cohortType) => {
          _.each(cohorts, existing => {
            if (
              (!cohort['id'] || cohort.id !== existing.id) &&
              name === existing.name
            ) {
              msg = `You have an existing ${cohortType} with this name. Please choose a different name.`;
              return false;
            }
          });
        });
      }
      return msg;
    }
  }
};
</script>
