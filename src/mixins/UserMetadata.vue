<script>
import _ from 'lodash';
import store from '@/store';
import { mapActions, mapGetters } from 'vuex';

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
    myDeptCodesWhereAdvising() {
      const user = store.getters['user/user'];
      return _.map(_.filter(user.departments, d => d.isAdvisor || d.isDirector), ['deptCode']);
    }
  }
};
</script>
