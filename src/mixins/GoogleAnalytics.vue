<script>
import store from '@/store';
import { event } from 'vue-analytics';

export default {
  name: 'GoogleAnalytics',
  methods: {
    gaEvent(category, action, label, value) {
      const user = store.getters['user/user'];
      event(category, action, label, value, {
        userId: user.uid
      });
    },
    gaCohortEvent(id, name, action) {
      this.gaEvent('Cohort', action, name, id);
    },
    gaCuratedEvent(id, name, action) {
      this.gaEvent('Curated Group', action, name, id);
    }
  }
};
</script>
