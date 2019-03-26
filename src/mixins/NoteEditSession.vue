<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'NoteEditSession',
  computed: {
    ...mapGetters('noteEditSession', [
      'editingNoteId',
      'newNoteMode'
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
