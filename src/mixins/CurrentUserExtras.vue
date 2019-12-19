<script>
import { mapGetters } from 'vuex';

export default {
  name: 'CurrentUserExtras',
  computed: {
    ...mapGetters('currentUserExtras', [
      'myCohorts',
      'myCuratedGroups',
      'preferences'
    ])
  }
};
</script>
