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
      'featureFlagEditNotes',
      'isDemoModeAvailable',
      'maxAttachmentsPerNote',
      'serviceAnnouncement',
      'srAlert',
      'supportEmailAddress'
    ])
  },
  methods: {
    ...mapActions('context', [
      'clearAlertsInStore',
      'dismissError',
      'reportError',
      'alertScreenReader'
    ])
  }
};
</script>
