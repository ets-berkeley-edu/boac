<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'apiBaseUrl',
      'currentEnrollmentTerm',
      'currentEnrollmentTermId',
      'devAuthEnabled',
      'errors',
      'featureFlagAppointments',
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
      'initUserSession',
      'reportError',
      'alertScreenReader'
    ])
  }
};
</script>
