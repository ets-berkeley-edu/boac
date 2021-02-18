<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'announcement',
      'dismissedFooterAlert',
      'dismissedServiceAnnouncement'
    ]),
    ...mapGetters('noteEditSession', [
      'disableNewNoteButton',
      'mode'
    ])
  },
  methods: {
    ...mapActions('context', [
      'dismissFooterAlert',
      'dismissServiceAnnouncement',
      'restoreServiceAnnouncement'
    ]),
    alertScreenReader(message, politeness='polite') {
      this.$announcer.set(message, politeness)
    }
  }
}
</script>
