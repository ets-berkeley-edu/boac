<script>
import _ from 'lodash'
import store from '@/store'
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'NoteEditSession',
  created() {
    this.scheduleAutoSaveJob()
  },
  destroyed() {
    this.clearAutoSaveJob()
  },
  computed: {
    ...mapGetters('noteEditSession', [
      'addedCohorts',
      'addedCuratedGroups',
      'autoSaveJob',
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
      'addSidList',
      'addTopic',
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
        // We auto-save draft notes.
        this.updateAdvisingNote().then(() => {
          if (this.$config.isVueAppDebugMode) {
            const now = this.$moment(new Date()).format('h:mm:ss')
            console.log(`[DEBUG] Auto-save draft note ${this.model.id} at ${now}`)
          }
          this.scheduleAutoSaveJob()
        })
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
