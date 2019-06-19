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
      'featureFlagBatchNotes',
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
      'initGoogleAnalytics',
      'initUserSession',
      'reportError',
      'alertScreenReader'
    ])
  }
};
</script>
