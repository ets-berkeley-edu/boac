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
    loaded() {
      store.commit('loadingComplete');
    }
  }
};
</script>
