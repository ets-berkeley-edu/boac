<script>
import _ from 'lodash'
import store from '@/store'
import {mapActions, mapGetters, mapMutations} from 'vuex'
import {addAttachments} from '@/api/notes'
import {alertScreenReader} from '@/store/modules/context'
import {isAutoSaveMode} from '@/store/utils/note'

export default {
  name: 'note',
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
      'addCohort',
      'addCuratedGroup',
      'addSid',
      'addSidList',
      'applyTemplate',
      'clearAutoSaveJob',
      'exitSession',
      'removeAttachment',
      'removeCohort',
      'removeCuratedGroup',
      'removeStudent',
      'resetModel',
      'setAutoSaveJob',
      'setModel',
      'updateAdvisingNote'
    ]),
    ...mapMutations('note', [
      'addAttachments',
      'addTopic',
      'onBoaSessionExpires',
      'removeAllStudents',
      'removeTopic',
      'setBody',
      'setContactType',
      'setFocusLockDisabled',
      'setIsDraft',
      'setIsPrivate',
      'setIsRecalculating',
      'setIsSaving',
      'setMode',
      'setSetDate',
      'setSubject',
    ]),
    addAttachments(attachments) {
      if (isAutoSaveMode(this.mode)) {
        this.setIsSaving(true)
        addAttachments(this.model.id, attachments).then(response => {
          store.commit('note/addAttachments', response.attachments)
          alertScreenReader('Attachment added', 'assertive')
          this.setIsSaving(false)
        })
      } else {
        this.addAttachments(attachments)
      }
    },
    autoSaveDraftNote() {
      this.clearAutoSaveJob()
      if (this.model.isDraft) {
        store.commit('note/isAutoSavingDraftNote', true)
        this.updateAdvisingNote().then(note => {
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
      store.commit('note/setSubject', _.isString(event) ? event : event.target.value)
    }
  }
}
</script>
