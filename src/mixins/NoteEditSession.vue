<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'NoteEditSession',
  computed: {
    ...mapGetters('noteEditSession', [
      'addedCohorts',
      'addedCuratedGroups',
      'attachments',
      'body',
      'noteMode',
      'objectId',
      'sids',
      'subject',
      'targetStudentCount',
      'topics'
    ])
  },
  methods: {
    ...mapActions('noteEditSession', [
      'addAttachment',
      'addCohort',
      'addCuratedGroup',
      'addSid',
      'addTopic',
      'clearAllFields',
      'createAdvisingNote',
      'endSession',
      'init',
      'recalculateStudentCount',
      'removeAttachment',
      'removeCohort',
      'removeCuratedGroup',
      'removeStudent',
      'removeTopic',
      'setBody',
      'setNoteMode',
      'setSubject',
      'updateAdvisingNote'
    ])
  }
};
</script>
