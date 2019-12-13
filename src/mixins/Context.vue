<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'apiBaseUrl',
      'currentEnrollmentTerm',
      'currentEnrollmentTermId',
      'hasUserDismissedFooterAlert',
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
