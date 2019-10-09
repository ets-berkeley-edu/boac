<script>
import _ from 'lodash';
import store from '@/store';
import { mapActions, mapGetters } from 'vuex';

const $_myDeptCodes = roles => {
  const user = store.getters['user/user'];
  return _.map(_.filter(user.departments, d => _.findIndex(roles, role => d[role]) > -1), ['deptCode']);
};

export default {
  name: 'UserMetadata',
  computed: {
    ...mapGetters('user', [
      'preferences',
      'user'
    ]),
    ...mapGetters('cohort', ['myCohorts']),
    ...mapGetters('curated', ['myCuratedGroups']),
    ...mapGetters('note', [
      'noteTemplates',
      'suggestedNoteTopics'
    ])
  },
  methods: {
    ...mapActions('user', [
      'gaCohortEvent',
      'gaCourseEvent',
      'gaCuratedEvent',
      'gaNoteEvent',
      'gaSearchEvent',
      'gaStudentAlert',
      'loadCalnetUserByCsid',
      'setUserPreference'
    ]),
    isUserSimplyScheduler() {
     const user = store.getters['user/user'];
     const isScheduler = _.size($_myDeptCodes(['isScheduler']));
     return isScheduler && !user.isAdmin && !_.size($_myDeptCodes(['isAdvisor', 'isDirector']));
    },
    myDeptCodes: $_myDeptCodes
  }
};
</script>
