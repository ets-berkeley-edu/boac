<script>
import store from '@/store'
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'announcement',
      'config',
      'currentUser',
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
    broadcast: (eventType, data) => store.commit('context/broadcast', {eventType, data}),
    removeEventHandler: (type, handler) => store.commit('context/removeEventHandler', {type, handler}),
    setEventHandler: (type, handler) => store.commit('context/setEventHandler', {type, handler})
  }
}
</script>
