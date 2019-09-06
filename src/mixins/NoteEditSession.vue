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
      'isFocusLockDisabled',
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
      'createAdvisingNote',
      'removeAttachment',
      'removeCohort',
      'removeCuratedGroup',
      'removeStudent',
      'removeTopic',
      'resetModel',
      'setBody',
      'setFocusLockDisabled',
      'setMode',
      'setModel',
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
