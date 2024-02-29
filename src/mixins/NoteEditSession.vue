<script>
import {mapActions, mapState} from 'pinia'
import {nextTick} from 'vue'
import {useNoteStore} from '@/stores/note-edit-session'
import {onVisibilityChange, scheduleAutoSaveJob} from '@/stores/note-edit-session/utils'

const $_disableFocusLock = disable => {
  const onNextTick = () => {
    useNoteStore().setFocusLockDisabled(disable)
  }
  nextTick(onNextTick)
}

export default {
  name: 'NoteEditSession',
  computed: {
    ...mapState(useNoteStore, [
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
  unmounted() {
    useNoteStore().clearAutoSaveJob()
    document.removeEventListener('visibilitychange', onVisibilityChange)
  },
  methods: {
    ...mapActions(useNoteStore, [
      'addTopic',
      'onBoaSessionExpires',
      'removeAllStudents',
      'removeTopic',
      'resetModel',
      'setAttachments',
      'setBody',
      'setContactType',
      'setIsDraft',
      'setIsPrivate',
      'setIsRecalculating',
      'setIsSaving',
      'setMode',
      'setModel',
      'setNoteTemplates',
      'setSetDate',
      'setSubject',
    ]),
    disableFocusLock: () => $_disableFocusLock(true),
    enableFocusLock: () => $_disableFocusLock(false)
  }
}
</script>
