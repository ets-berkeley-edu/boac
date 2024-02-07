<script>
import _ from 'lodash'
import store from '@/store'
import {getDistinctSids} from '@/api/student'
import {mapActions, mapGetters, mapMutations} from 'vuex'
import {addAttachments} from '@/api/notes'
import {alertScreenReader} from '@/store/modules/context'
import {isAutoSaveMode} from '@/store/modules/note-edit-session/utils'

export default {
  name: 'NoteEditSession',
  computed: {
    ...mapGetters('note', [
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
      'recipients'
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
      'applyTemplate',
      'clearAutoSaveJob',
      'exitSession',
      'removeAttachment',
      'setAutoSaveJob',
      'updateAdvisingNote'
    ]),
    ...mapMutations('note', [
      'addAttachments',
      'addTopic',
      'onBoaSessionExpires',
      'removeAllStudents',
      'removeTopic',
      'resetModel',
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
    setRecipient(sid) {
      return this.setRecipients(
        this.recipients.cohorts,
        this.recipients.curatedGroups,
        this.recipients.sids.concat(sid)
      )
    },
    setRecipients(cohorts, curatedGroups, sids) {
      return new Promise(resolve => {
        store.commit('note/setIsRecalculating', true)
        store.commit('note/setRecipients', {cohorts, curatedGroups, sids})
        const cohortIds = _.map(cohorts, 'id')
        const curatedGroupIds = _.map(curatedGroups, 'id')
        const onFinish = sids => {
          store.commit('note/setCompleteSidSet', sids)
          store.commit('note/setIsRecalculating', false)
          resolve()
        }
        if (cohortIds.length || curatedGroupIds.length) {
          getDistinctSids(this.recipients.sids, cohortIds, curatedGroupIds).then(data => onFinish(data.sids))
        } else {
          onFinish(this.recipients.sids)
        }
      })
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
