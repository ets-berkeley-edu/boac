<script>
import store from '@/store';

export default {
  name: 'AppConfig',
  computed: {
    devAuthEnabled() {
      return store.getters.config.devAuthEnabled;
    }
  }
};
</script>
