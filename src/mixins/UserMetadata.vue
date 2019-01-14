<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'UserMetadata',
  methods: {
    ...mapActions('user', ['setUserPreference'])
  },
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
  }
};
</script>
