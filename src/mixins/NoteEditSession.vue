<script>
import { mapActions, mapGetters, mapMutations } from 'vuex';

export default {
  name: 'NoteEditSession',
  computed: {
    ...mapGetters('noteEditSession', [
      'addedCohorts',
      'addedCuratedGroups',
      'attachments',
      'body',
      'noteMode',
      'noteTemplates',
      'objectId',
      'sids',
      'subject',
      'suggestedTopics',
      'targetStudentCount',
      'topics',
      'undocked'
    ])
  },
  methods: {
    ...mapActions('noteEditSession', [
      'addAttachment',
      'addCohort',
      'addCuratedGroup',
      'addSid',
      'addTopic',
      'createAdvisingNote',
      'init',
      'recalculateStudentCount',
      'removeCohort',
      'removeCuratedGroup',
      'removeStudent',
      'setBody',
      'setNoteMode',
      'setSubject',
      'updateAdvisingNote'
    ]),
    ...mapMutations('noteEditSession', [
      'endSession',
      'removeAttachment',
      'removeTopic',
      'resetSession',
      'setObjectId'
    ])
  }
};
</script>
