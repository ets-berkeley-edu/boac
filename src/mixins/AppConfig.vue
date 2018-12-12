<script>
import { mapGetters } from 'vuex';

export default {
  name: 'AppConfig',
  computed: {
    ...mapGetters('context', [
      'apiBaseUrl',
      'currentEnrollmentTermId',
      'devAuthEnabled',
      'supportEmailAddress'
    ])
  }
};
</script>
