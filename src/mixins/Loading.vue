<script>
import store from '@/store';
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Loading',
  beforeCreate: () => store.dispatch('context/loadingStart'),
  computed: {
    ...mapGetters('context', ['loading'])
  },
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
