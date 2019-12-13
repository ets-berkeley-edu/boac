<script>
import _ from 'lodash';
import { mapActions, mapGetters } from 'vuex';
import Vue from "vue";

const $_myDeptCodes = roles => {
  return _.map(_.filter(Vue.prototype.$currentUser.departments, d => _.findIndex(roles, role => d[role]) > -1), 'code');
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
      const deptCodes = _.map(Vue.prototype.$currentUser.dropInAdvisorStatus || [], 'deptCode');
      return _.includes(deptCodes, _.upperCase(deptCode));
    },
    isUserSimplyScheduler() {
     const isScheduler = _.size($_myDeptCodes(['isScheduler']));
     return isScheduler && !Vue.prototype.$currentUser.isAdmin && !_.size($_myDeptCodes(['isAdvisor', 'isDirector']));
    },
    myDeptCodes: $_myDeptCodes
  }
};
</script>
