<script>
import {mapActions, mapState} from 'pinia'
import {useContextStore} from '@/stores/context'

export default {
  name: 'Context',
  computed: {
    ...mapState(useContextStore, [
      'announcement',
      'config',
      'currentUser',
      'dismissedFooterAlert',
      'dismissedServiceAnnouncement',
      'loading',
      'screenReaderAlert'
    ]),
  },
  methods: {
    ...mapActions(useContextStore, [
      'alertScreenReader',
      'broadcast',
      'dismissFooterAlert',
      'dismissServiceAnnouncement',
      'loadingComplete',
      'loadingStart',
      'removeEventHandler',
      'restoreServiceAnnouncement',
      'setEventHandler'
    ])
  }
}
</script>
