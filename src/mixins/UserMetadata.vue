<script>
import { mapGetters } from 'vuex';

export default {
  name: 'UserMetadata',
  computed: {
    ...mapGetters('user', ['isAscUser', 'isCoeUser', 'user']),
    ...mapGetters('cohort', ['myCohorts']),
    ...mapGetters('curated', ['myCuratedGroups'])
  }
};
</script>
