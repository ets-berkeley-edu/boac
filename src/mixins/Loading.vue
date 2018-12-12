<script>
import store from '@/store';
import { mapGetters } from 'vuex';

export default {
  name: 'Loading',
  beforeCreate: () => store.dispatch('context/loadingStart'),
  computed: {
    ...mapGetters('context', ['loading'])
  },
  methods: {
    startLoading: () => store.dispatch('context/loadingStart'),
    loaded: () => store.dispatch('context/loadingComplete')
  }
};
</script>
