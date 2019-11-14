<script>
import _ from 'lodash';
import store from '@/store';
import { mapActions, mapGetters } from 'vuex';

const $_myDeptCodes = roles => {
  const user = store.getters['user/user'];
  return _.map(_.filter(user.departments, d => _.findIndex(roles, role => d[role]) > -1), 'code');
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
      'gaAppointmentEvent',
      'gaCohortEvent',
      'gaCourseEvent',
      'gaCuratedEvent',
      'gaNoteEvent',
      'gaSearchEvent',
      'gaStudentAlert',
      'loadCalnetUserByCsid',
      'setUserPreference'
    ]),
    getBoaUserRoles(user, department) {
      const roles = [];
      if (department.isAdvisor) {
        roles.push('Advisor');
      }
      if (department.isDirector) {
        roles.push('Director');
      }
      if (department.isScheduler) {
        roles.push('Scheduler');
      }
      if (_.find(user.dropInAdvisorStatus, ['deptCode', department.code])) {
        roles.push('Drop-in Advisor');
      }
      return roles;
    },
    isUserDropInAdvisor(deptCode) {
      const deptCodes = _.map(store.getters['user/user'].dropInAdvisorStatus || [], 'deptCode');
      return _.includes(deptCodes, _.upperCase(deptCode));
    },
    isUserSimplyScheduler() {
     const user = store.getters['user/user'];
     const isScheduler = _.size($_myDeptCodes(['isScheduler']));
     return isScheduler && !user.isAdmin && !_.size($_myDeptCodes(['isAdvisor', 'isDirector']));
    },
    myDeptCodes: $_myDeptCodes
  }
};
</script>
