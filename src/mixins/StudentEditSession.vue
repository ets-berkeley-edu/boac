<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'StudentEditSession',
  computed: {
    ...mapGetters('studentEditSession', [
      'editingNoteId',
      'newNoteMode',
      'suggestedTopics'
    ])
  },
  methods: {
    ...mapActions('studentEditSession', [
      'editExistingNoteId',
      'endSession',
      'setNewNoteMode',
      'setSid'
    ])
  }
};
</script>
