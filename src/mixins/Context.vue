<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'announcement',
      'apiBaseUrl',
      'currentEnrollmentTerm',
      'currentEnrollmentTermId',
      'hasUserDismissedFooterAlert',
      'isVueAppDebugMode',
      'maxAttachmentsPerNote',
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
