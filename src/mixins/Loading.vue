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
      if (this.user) {
        this.finishLoading();
      } else {
        this.$watch('user', this.finishLoading);
      }
    },
    finishLoading() {
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
