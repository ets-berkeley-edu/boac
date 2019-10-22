<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'apiBaseUrl',
      'apptDeskRefreshInterval',
      'currentEnrollmentTerm',
      'currentEnrollmentTermId',
      'devAuthEnabled',
      'ebEnvironment',
      'errors',
      'featureFlagAppointments',
      'fixedWarningOnAllPages',
      'hasUserDismissedFooterAlert',
      'isDemoModeAvailable',
      'maxAttachmentsPerNote',
      'pingFrequency',
      'announcement',
      'srAlert',
      'supportEmailAddress',
      'timezone'
    ]),
    ...mapGetters('noteEditSession', ['disableNewNoteButton'])
  },
  methods: {
    ...mapActions('context', [
      'clearAlertsInStore',
      'dismissError',
      'dismissFooterAlert',
      'initUserSession',
      'reportError',
      'alertScreenReader'
    ])
  }
};
</script>
