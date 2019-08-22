<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Notes',
  computed: {
    ...mapGetters('notes', [
      'editModeObject',
      'noteMode',
      'noteTemplates',
      'suggestedTopics'
    ])
  },
  methods: {
    ...mapActions('notes', [
      'endSession',
      'setNoteMode',
      'setEditModeObject',
      'setSid'
    ])
  }
};
</script>
