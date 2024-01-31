<script>
import store from '@/store'
import {mapGetters, mapMutations} from 'vuex'

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'announcement',
      'config',
      'currentUser',
      'dismissedFooterAlert',
      'dismissedServiceAnnouncement',
      'loading'
    ]),
    ...mapGetters('noteEditSession', [
      'disableNewNoteButton',
      'mode'
    ])
  },
  methods: {
    ...mapMutations('context', [
      'dismissFooterAlert',
      'dismissServiceAnnouncement',
      'loadingComplete',
      'loadingStart',
      'restoreServiceAnnouncement'
    ]),
    broadcast: (eventType, data) => store.commit('context/broadcast', {eventType, data}),
    removeEventHandler: (type, handler) => store.commit('context/removeEventHandler', {type, handler}),
    setEventHandler: (type, handler) => store.commit('context/setEventHandler', {type, handler})
  }
}
</script>
