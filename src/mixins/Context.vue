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
      'featureFlagAppointments',
      'featureFlagPassengerEdit',
      'fixedWarningOnAllPages',
      'hasUserDismissedFooterAlert',
      'isDemoModeAvailable',
      'isVueAppDebugMode',
      'maxAttachmentsPerNote',
      'pingFrequency',
      'announcement',
      'screenReaderAlert',
      'supportEmailAddress',
      'timezone'
    ]),
    ...mapGetters('noteEditSession', ['disableNewNoteButton'])
  },
  methods: {
    ...mapActions('context', [
      'alertScreenReader',
      'dismissFooterAlert',
      'initUserSession'
    ])
  }
};
</script>
