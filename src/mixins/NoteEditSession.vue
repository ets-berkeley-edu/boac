<script>
import _ from 'lodash'
import store from '@/store'
import {mapActions, mapGetters, mapMutations} from 'vuex'
import {updateAdvisingNote} from '@/store/utils/note'

export default {
  name: 'NoteEditSession',
  computed: {
    ...mapGetters('note', [
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
  created() {
    this.scheduleAutoSaveJob()
    document.addEventListener('visibilitychange', this.onVisibilityChange)
  },
  destroyed() {
    this.clearAutoSaveJob()
    document.removeEventListener('visibilitychange', this.onVisibilityChange)
  },
  methods: {
    ...mapActions('note', [
      'addAttachments',
      'addCohort',
      'addCuratedGroup',
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
      'setContactType',
      'setFocusLockDisabled',
      'setIsDraft',
      'setIsPrivate',
      'setIsRecalculating',
      'setIsSaving',
      'setMode',
      'setModel',
      'setSetDate',
      'setSubject'
    ]),
    ...mapMutations('note', [
      'addSid',
      'setBody',
    ]),
    autoSaveDraftNote() {
      this.clearAutoSaveJob()
      if (this.model.isDraft) {
        store.commit('note/isAutoSavingDraftNote', true)
        updateAdvisingNote().then(note => {
          store.commit('note/setModelId', note.id)
          setTimeout(() => store.commit('note/isAutoSavingDraftNote', false), 2000)
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
      const jobId = setTimeout(this.autoSaveDraftNote, store.getters['context/config'].notesDraftAutoSaveInterval)
      this.setAutoSaveJob(jobId)
    },
    setSubjectPerEvent(event) {
      store.dispatch('note/setSubject', _.isString(event) ? event : event.target.value)
    }
  }
}
</script>
