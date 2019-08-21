<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Notes',
  computed: {
    ...mapGetters('notes', [
      'editingNoteId',
      'noteMode',
      'noteTemplates',
      'suggestedTopics'
    ])
  },
  methods: {
    ...mapActions('notes', [
      'editExistingNoteId',
      'endSession',
      'setNoteMode',
      'setSid'
    ])
  }
};
</script>
