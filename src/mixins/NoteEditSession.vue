<script>
import _ from 'lodash'
import store from '@/store'
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'NoteEditSession',
  computed: {
    ...mapGetters('noteEditSession', [
      'addedCohorts',
      'addedCuratedGroups',
      'boaSessionExpired',
      'completeSidSet',
      'isFocusLockDisabled',
      'isSaving',
      'isRecalculating',
      'mode',
      'model',
      'noteTemplates',
      'sids'
    ])
  },
  methods: {
    ...mapActions('noteEditSession', [
      'addAttachment',
      'addCohort',
      'addCuratedGroup',
      'addSid',
      'addTopic',
      'createAdvisingNotes',
      'exitSession',
      'onBoaSessionExpires',
      'removeAttachment',
      'removeCohort',
      'removeCuratedGroup',
      'removeStudent',
      'removeTopic',
      'resetModel',
      'setBody',
      'setContactType',
      'setFocusLockDisabled',
      'setIsPrivate',
      'setIsRecalculating',
      'setIsSaving',
      'setMode',
      'setModel',
      'setSetDate',
      'setSubject'
    ]),
    setSubjectPerEvent(event) {
      store.dispatch('noteEditSession/setSubject', _.isString(event) ? event : event.target.value)
    }
  }
}
</script>
