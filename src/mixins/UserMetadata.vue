<script>
import { mapActions, mapGetters, mapMutations } from 'vuex';

export default {
  name: 'UserMetadata',
  computed: {
    ...mapGetters('user', [
      'preferences',
      'user'
    ]),
    ...mapGetters('cohort', ['myCohorts']),
    ...mapGetters('curated', ['myCuratedGroups'])
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
    ...mapMutations('user', [
    ])
  }
};
</script>
