<script>
import _ from 'lodash';
import store from '@/store';
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'NoteEditSession',
  computed: {
    ...mapGetters('noteEditSession', [
      'addedCohorts',
      'addedCuratedGroups',
      'mode',
      'model',
      'sids',
      'targetStudentCount'
    ])
  },
  methods: {
    ...mapActions('noteEditSession', [
      'addAttachment',
      'addCohort',
      'addCuratedGroup',
      'addSid',
      'addTopic',
      'beginEditSession',
      'createAdvisingNote',
      'removeAttachment',
      'removeCohort',
      'removeCuratedGroup',
      'removeStudent',
      'removeTopic',
      'setBody',
      'setMode',
      'setSubject',
      'terminate'
    ]),
    setSubjectPerEvent(event) {
      store.dispatch('noteEditSession/setSubject', _.isString(event) ? event : event.target.value);
    },
    setBodyPerEvent(event) {
      store.dispatch('noteEditSession/setBody', _.isString(event) ? event : event.target.value);
    }
  }
};
</script>
