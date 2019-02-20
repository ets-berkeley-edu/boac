<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'UserMetadata',
  computed: {
    ...mapGetters('user', [
      'canViewAsc',
      'canViewCoe',
      'isAscUser',
      'isCoeUser',
      'preferences',
      'user'
    ]),
    ...mapGetters('cohort', ['myCohorts']),
    ...mapGetters('curated', ['myCuratedGroups'])
  },
  methods: {
    ...mapActions('user', [
      'setUserPreference',
      'loadCalnetUserByCsid',
      'userAuthenticated'
    ])
  }
};
</script>
