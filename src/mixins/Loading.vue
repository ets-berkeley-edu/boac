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
    loaded(pageTitle) {
      if (!!pageTitle && store.getters['context/loading']) {
        store.dispatch('context/alertScreenReader', `${pageTitle} page is ready`)
      }
      store.dispatch('context/loadingComplete')
    }
  }
}
</script>
