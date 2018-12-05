<script>
import store from '@/store';

export default {
  name: 'UserMetadata',
  computed: {
    user: () => store.getters.user
  }
};
</script>
