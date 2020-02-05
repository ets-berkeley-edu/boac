<script>
import { mapGetters } from 'vuex';

export default {
  name: 'CurrentUserExtras',
  computed: {
    ...mapGetters('currentUserExtras', [
      'myAdmitCohorts',
      'myCohorts',
      'myCuratedGroups',
      'preferences'
    ])
  }
};
</script>
