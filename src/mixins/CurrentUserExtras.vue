<script>
import { mapGetters } from 'vuex'

export default {
  name: 'CurrentUserExtras',
  computed: {
    ...mapGetters('currentUserExtras', [
      'includeAdmits',
      'myAdmitCohorts',
      'myCohorts',
      'myCuratedGroups',
      'preferences'
    ])
  }
}
</script>
