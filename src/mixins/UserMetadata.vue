<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'UserMetadata',
  computed: {
    ...mapGetters('user', [
      'preferences',
      'user',
      'userAuthStatus'
    ]),
    ...mapGetters('cohort', ['myCohorts']),
    ...mapGetters('curated', ['myCuratedGroups'])
  },
  methods: {
    ...mapActions('user', [
      'setUserPreference',
      'loadCalnetUserByCsid'
    ])
  }
};
</script>
