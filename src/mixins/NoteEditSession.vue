<script>
import _ from 'lodash'
import store from '@/store'
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'NoteEditSession',
  created() {
    this.scheduleAutoSaveJob()
    document.addEventListener('visibilitychange', this.onVisibilityChange)
  },
  destroyed() {
    this.clearAutoSaveJob()
    document.removeEventListener('visibilitychange', this.onVisibilityChange)
  },
  computed: {
    ...mapGetters('noteEditSession', [
      'addedCohorts',
      'addedCuratedGroups',
      'autoSaveJob',
      'boaSessionExpired',
      'completeSidSet',
      'isAutoSavingDraftNote',
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
      'addAttachments',
      'addCohort',
      'addCuratedGroup',
      'addSid',
      'addSidList',
      'addTopic',
      'applyTemplate',
      'clearAutoSaveJob',
      'exitSession',
      'onBoaSessionExpires',
      'removeAllStudents',
      'removeAttachment',
      'removeCohort',
      'removeCuratedGroup',
      'removeStudent',
      'removeTopic',
      'resetModel',
      'setAutoSaveJob',
      'setBody',
      'setContactType',
      'setFocusLockDisabled',
      'setIsDraft',
      'setIsPrivate',
      'setIsRecalculating',
      'setIsSaving',
      'setMode',
      'setModel',
      'setSetDate',
      'setSubject',
      'updateAdvisingNote'
    ]),
    autoSaveDraftNote() {
      this.clearAutoSaveJob()
      if (this.model.isDraft) {
        store.commit('noteEditSession/isAutoSavingDraftNote', true)
        this.updateAdvisingNote().then(note => {
          store.commit('noteEditSession/setModelId', note.id)
          setTimeout(() => store.commit('noteEditSession/isAutoSavingDraftNote', false), 2000)
          this.scheduleAutoSaveJob()
        })
      }
    },
    onVisibilityChange() {
      const visibility = document.visibilityState
      if (visibility) {
        this.clearAutoSaveJob()
        if (visibility === 'visible') {
          this.scheduleAutoSaveJob()
        }
      }
    },
    scheduleAutoSaveJob() {
      const jobId = setTimeout(this.autoSaveDraftNote, this.$config.notesDraftAutoSaveInterval)
      this.setAutoSaveJob(jobId)
    },
    setSubjectPerEvent(event) {
      store.dispatch('noteEditSession/setSubject', _.isString(event) ? event : event.target.value)
    }
  }
}
</script>
