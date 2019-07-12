<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'apiBaseUrl',
      'currentEnrollmentTermId',
      'devAuthEnabled',
      'errors',
      'isDemoModeAvailable',
      'maxAttachmentsPerNote',
      'announcement',
      'srAlert',
      'supportEmailAddress',
      'timezone'
    ])
  },
  methods: {
    ...mapActions('context', [
      'clearAlertsInStore',
      'dismissError',
      'initUserSession',
      'reportError',
      'alertScreenReader'
    ])
  }
};
</script>
