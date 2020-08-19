<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'announcement',
      'hasUserDismissedFooterAlert',
      'screenReaderAlert'
    ]),
    ...mapGetters('noteEditSession', [
      'disableNewNoteButton',
      'mode'
    ])
  },
  methods: {
    ...mapActions('context', [
      'alertScreenReader',
      'dismissFooterAlert'
    ])
  }
};
</script>
