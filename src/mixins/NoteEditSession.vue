<script>
import {clearAutoSaveJob, onVisibilityChange, scheduleAutoSaveJob} from '@/store/modules/note-edit-session/utils'
import {mapGetters, mapMutations} from 'vuex'

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
    scheduleAutoSaveJob()
    document.addEventListener('visibilitychange', onVisibilityChange)
  },
  destroyed() {
    clearAutoSaveJob()
    document.removeEventListener('visibilitychange', onVisibilityChange)
  },
  methods: {
    ...mapMutations('note', [
      'addTopic',
      'onBoaSessionExpires',
      'removeAllStudents',
      'removeTopic',
      'resetModel',
      'setAttachments',
      'setBody',
      'setContactType',
      'setFocusLockDisabled',
      'setIsDraft',
      'setIsPrivate',
      'setIsRecalculating',
      'setIsSaving',
      'setMode',
      'setModel',
      'setNoteTemplates',
      'setSetDate',
      'setSubject',
    ])
  }
}
</script>
