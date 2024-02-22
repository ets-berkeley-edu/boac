<script>
import store from '@/store'
import Vue from 'vue'
import {clearAutoSaveJob, onVisibilityChange, scheduleAutoSaveJob} from '@/store/modules/note-edit-session/utils'
import {mapGetters, mapMutations} from 'vuex'

const $_disableFocusLock = disable => {
  const onNextTick = () => {
    store.commit('note/setFocusLockDisabled', disable)
  }
  Vue.nextTick(onNextTick)
}

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
