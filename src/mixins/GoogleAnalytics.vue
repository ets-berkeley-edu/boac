<script>
import { event } from 'vue-analytics';
import { mapGetters } from 'vuex';

export default {
  name: 'GoogleAnalytics',
  computed: {
    ...mapGetters('user', ['user'])
  },
  methods: {
    gaEvent(category, action, label, value) {
      if (this.user) {
        event(category, action, label, value, {
          userId: this.user.uid
        });
      } else {
        this.$watch('user', () => {
          event(category, action, label, value, {
            userId: this.user.uid
          });
        }); 
      }
    },
    gaCohortEvent(id, name, action) {
      this.gaEvent('Cohort', action, name, id);
    },
    gaCuratedEvent(id, name, action) {
      this.gaEvent('Curated Group', action, name, id);
    },
    gaStudentAlert(id, name, action) {
      this.gaEvent('Advising Note', action, name, id);
    },
    gaNoteEvent(id, name, action) {
      this.gaEvent('Advising Note', action, name, id);
    },
    gaSearchEvent(id, name, action) {
      this.gaEvent('Search', action, name, id);
    }
  }
};
</script>
