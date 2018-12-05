<script>
import store from '@/store';

export default {
  name: 'Loading',
  beforeCreate() {
    store.commit('loadingStart');
  },
  computed: {
    loading() {
      return store.getters.loading;
    }
  },
  methods: {
    startLoading() {
      store.commit('loadingStart');
    },
    loaded() {
      store.commit('loadingComplete');
    }
  }
};
</script>
