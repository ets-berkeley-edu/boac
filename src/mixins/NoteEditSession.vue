<script>
import {mapActions, mapState} from 'pinia'
import {nextTick} from 'vue'
import {useNoteStore} from '@/stores/note-edit-session'

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
    useNoteStore().scheduleAutoSaveJob()
    document.addEventListener('visibilitychange', useNoteStore().onVisibilityChange)
  },
  unmounted() {
    useNoteStore().clearAutoSaveJob()
    document.removeEventListener('visibilitychange', useNoteStore().onVisibilityChange)
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
