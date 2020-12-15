<script>
import store from '@/store'
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Loading',
  computed: {
    ...mapGetters('context', ['loading'])
  },
  beforeCreate: () => store.commit('context/loadingStart'),
  methods: {
    ...mapActions('context', ['loadingStart']),
    loaded(srAlert, focusTarget) {
      if (srAlert) {
        this.$announcer.polite(srAlert)
      }
      store.commit('context/loadingComplete', focusTarget)
    }
  }
}
</script>
