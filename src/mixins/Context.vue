<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'announcement',
      'hasUserDismissedFooterAlert'
    ]),
    ...mapGetters('noteEditSession', [
      'disableNewNoteButton',
      'mode'
    ])
  },
  methods: {
    ...mapActions('context', [
      'dismissFooterAlert'
    ]),
    alertScreenReader(message, politeness='polite') {
      this.$announcer.set(message, politeness)
    }
  }
}
</script>
