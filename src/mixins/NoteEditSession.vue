<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'NoteEditSession',
  computed: {
    ...mapGetters('noteEditSession', [
      'editingNoteId',
      'newNoteMode',
      'suggestedTopics'
    ])
  },
  methods: {
    ...mapActions('noteEditSession', [
      'editExistingNoteId',
      'setNewNoteMode'
    ])
  }
};
</script>
