<script>
import store from '@/store';
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Loading',
  computed: {
    ...mapGetters('context', ['loading']),
    ...mapGetters('user', ['user'])
  },
  beforeCreate: () => store.dispatch('context/loadingStart'),
  methods: {
    ...mapActions('context', ['loadingStart']),
    loaded() {
      store.dispatch('context/loadingComplete');
      this.$nextTick(() => {
        if (this.$refs.pageHeader) {
          this.$refs.pageHeader.focus();
        }
      });
    }
  }
};
</script>
