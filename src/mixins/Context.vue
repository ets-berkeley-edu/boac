<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'apiBaseUrl',
      'currentEnrollmentTermId',
      'devAuthEnabled',
      'errors',
      'supportEmailAddress'
    ])
  },
  methods: {
    ...mapActions('context', [
      'clearErrorsInStore',
      'dismissError',
      'reportError'
    ])
  }
};
</script>
