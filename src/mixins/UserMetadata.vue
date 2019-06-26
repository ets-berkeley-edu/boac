<script>
import { mapActions, mapGetters } from 'vuex';

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
      'gaEvent',
      'gaCohortEvent',
      'gaCuratedEvent',
      'gaStudentAlert',
      'gaNoteEvent',
      'gaSearchEvent',
      'loadCalnetUserByCsid',
      'setUserPreference'
    ])
  }
};
</script>
