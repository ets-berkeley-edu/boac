<script>
import store from '@/store'
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Loading',
  computed: {
    ...mapGetters('context', ['loading'])
  },
  beforeCreate: () => store.dispatch('context/loadingStart'),
  methods: {
    ...mapActions('context', ['loadingStart']),
    loaded(srAlert) {
      if (srAlert) {
        this.$announcer.polite(srAlert)
      }
      store.dispatch('context/loadingComplete')
    }
  }
}
</script>
