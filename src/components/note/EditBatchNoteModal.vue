<template>
  <v-dialog
    v-if="mode"
    v-model="dialogModel"
    aria-labelledby="dialog-header-note"
    min-width="500"
    persistent
    width="60%"
  >
    <v-card id="new-note-modal-container">
      <div
        class="default-margins mb-6 mr-6"
        :class="{'mt-4': ['createBatch', 'editDraft'].includes(mode)}"
      >
        <CreateNoteHeader />
        <div>
          <Transition v-if="['createBatch', 'editDraft'].includes(mode)" name="batch-transition">
            <div v-show="mode !== 'editTemplate'">
              <BatchNoteFeatures :discard="discardRequested" />
            </div>
          </Transition>
        </div>
        <div class="pt-3">
          <label
            id="create-note-subject-label"
            for="create-note-subject"
            class="font-size-16 font-weight-700"
          >
            <span class="sr-only">Note </span>Subject
          </label>
          <v-text-field
            id="create-note-subject"
            :model-value="model.subject"
            aria-labelledby="create-note-subject-label"
            class="mt-2"
            :class="{'bg-light': isSaving}"
            color="primary"
            density="compact"
            :disabled="isSaving || boaSessionExpired"
            maxlength="255"
            type="text"
            variant="outlined"
            @input="setSubjectPerEvent"
          />
          <RichTextEditor
            id="note-details"
            :disabled="isSaving || boaSessionExpired"
            :initial-value="model.body || ''"
            :is-in-modal="true"
            label="Note Details"
            :on-value-update="useNoteStore().setBody"
            :show-advising-note-best-practices="true"
          />
        </div>
        <div class="py-3">
          <AdvisingNoteTopics />
          <PrivacyPermissions v-if="useContextStore().currentUser.canAccessPrivateNotes" />
          <TransitionGroup v-if="mode !== 'editTemplate'" name="batch-transition">
            <div key="0" class="pt-4">
              <ContactMethod />
            </div>
            <div key="1" class="pt-4">
              <ManuallySetDate />
            </div>
          </TransitionGroup>
          <AdvisingNoteAttachments
            :add-attachments="addNoteAttachments"
            class="pt-5"
            :disabled="!!(noteStore.isSaving || noteStore.boaSessionExpired)"
            :remove-attachment="removeAttachmentByIndex"
          />
        </div>
        <v-alert
          v-if="alert"
          id="alert-in-note-modal"
          :model-value="alert && !!dismissAlertSeconds"
          class="font-weight-bold w-100 mb-2"
          closable
          color="info"
          density="comfortable"
          variant="tonal"
          @click:close="dismissAlert"
        >
          <div class="d-flex">
            <div v-if="isSaving" class="mr-2">
              <v-icon :icon="mdiSync" spin />
            </div>
            <div>{{ alert }}</div>
          </div>
        </v-alert>
        <CreateNoteFooter
          :discard="discardRequested"
          :exit="exit"
          :save-as-template="saveAsTemplate"
          :show-alert="showAlert"
          :update-template="updateTemplate"
        />
      </div>
    </v-card>
  </v-dialog>
  <AreYouSureModal
    v-model="showDiscardNoteModal"
    :function-cancel="cancelDiscardNote"
    :function-confirm="discardNote"
    modal-header="Discard unsaved note?"
  />
  <CreateTemplateModal
    v-model="showCreateTemplateModal"
    :cancel="cancelCreateTemplate"
    :create="createTemplate"
    :on-hidden="() => noteStore.setIsSaving(false)"
  />
  <AreYouSureModal
    v-model="showDiscardTemplateModal"
    :function-cancel="cancelDiscardTemplate"
    :function-confirm="discardTemplate"
    modal-header="Discard unsaved template?"
  />
</template>

<script setup>
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import BatchNoteFeatures from '@/components/note/BatchNoteFeatures'
import ContactMethod from '@/components/note/ContactMethod'
import CreateNoteFooter from '@/components/note/CreateNoteFooter'
import CreateNoteHeader from '@/components/note/CreateNoteHeader'
import CreateTemplateModal from '@/components/note/CreateTemplateModal'
import ManuallySetDate from '@/components/note/ManuallySetDate'
import PrivacyPermissions from '@/components/note/PrivacyPermissions'
import RichTextEditor from '@/components/util/RichTextEditor'
import {addAttachments, createDraftNote, getNote, removeAttachment} from '@/api/notes'
import {alertScreenReader, invokeIfAuthenticated, putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {createNoteTemplate, getMyNoteTemplates, updateNoteTemplate} from '@/api/note-templates'
import {concat, filter, size, trim, xor, xorBy} from 'lodash'
import {
  disableFocusLock,
  enableFocusLock,
  exitSession,
  isAutoSaveMode,
  setNoteRecipient,
  setSubjectPerEvent,
  updateAdvisingNote
} from '@/stores/note-edit-session/utils'
import {mdiSync} from '@mdi/js'
import {onBeforeUnmount, ref, watch} from 'vue'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  initialMode: {
    required: true,
    type: String
  },
  noteId: {
    default: undefined,
    required: false,
    type: Number
  },
  onClose: {
    default: () => {},
    required: false,
    type: Function
  },
  sid: {
    default: undefined,
    required: false,
    type: String
  },
  toggleShow: {
    default: () => {},
    required: false,
    type: Function
  }
})

const noteStore = useNoteStore()
const {boaSessionExpired, completeSidSet, isSaving, mode, model, noteTemplates} = storeToRefs(noteStore)
const alert = ref(undefined)
// eslint-disable-next-line vue/require-prop-types
const dialogModel = defineModel()
const dismissAlertSeconds = ref(undefined)
const showCreateTemplateModal = ref(false)
const showDiscardNoteModal = ref(false)
const showDiscardTemplateModal = ref(false)

const selectEscape = (event) => {
  if (event.key === 'Escape') {
    discardRequested()
  }
}

watch(dialogModel, () => {
  if (dialogModel.value) {
    // remove scrollbar for content behind the modal
    document.documentElement.classList.add('modal-open')
    document.removeEventListener('keyup', selectEscape)
    document.addEventListener('keyup', selectEscape)
    getMyNoteTemplates().then(noteStore.setNoteTemplates)
    noteStore.resetModel()
    init().then(note => {
      const onFinish = () => {
        noteStore.setMode(props.initialMode)
        putFocusNextTick(noteStore.mode === 'editTemplate' ? 'create-note-subject' : 'my-templates-button')
        useContextStore().setEventHandler('user-session-expired', noteStore.onBoaSessionExpires)
      }
      noteStore.setModel(note)
      if (note.sid) {
        setNoteRecipient(note.sid).then(onFinish)
      } else {
        onFinish()
      }
    })
  } else {
    noteStore.setMode(null)
    document.documentElement.classList.remove('modal-open')
    document.removeEventListener('keyup', selectEscape)
    useContextStore().removeEventHandler('user-session-expired', noteStore.onBoaSessionExpires)
  }
})

const addNoteAttachments = attachments => {
  return new Promise(resolve => {
    if (isAutoSaveMode(mode.value)) {
      noteStore.setIsSaving(true)
      addAttachments(model.value.id, attachments).then(response => {
        noteStore.setAttachments(response.attachments)
        alertScreenReader('Attachment added', 'assertive')
        noteStore.setIsSaving(false)
        resolve()
      })
    } else {
      noteStore.setAttachments(concat(model.value.attachments, attachments))
      alertScreenReader('Attachment added', 'assertive')
      resolve()
    }
  })
}

const cancelCreateTemplate = () => {
  noteStore.setIsSaving(false)
  showCreateTemplateModal.value = false
  enableFocusLock()
  alertScreenReader('Canceled save note as template.')
  putFocusNextTick('btn-save-as-template')
}

const cancelDiscardNote = () => {
  showDiscardNoteModal.value = false
  enableFocusLock()
  alertScreenReader('Continue editing note.')
  putFocusNextTick('create-note-cancel')
}

const cancelDiscardTemplate = () => {
  showDiscardTemplateModal.value = false
  putFocusNextTick('create-note-subject')
  enableFocusLock()
}

const createTemplate = title => {
  noteStore.setIsSaving(true)
  alertScreenReader('Creating template')
  const ifAuthenticated = () => {
    enableFocusLock()
    // File upload might take time; alert will be overwritten when API call is done.
    showAlert('Creating template...', 60)
    // Save draft before creating template.
    updateAdvisingNote().then(() => {
      createNoteTemplate(model.value.id, title).then(() => {
        showCreateTemplateModal.value = false
        noteStore.setIsSaving(false)
        showAlert(`Template '${title}' created.`)
        alertScreenReader(`Template '${title}' created.`)
        setTimeout(() => {
          // Creating a note-template was the user's purpose so we delete any incidental draft note.
          noteStore.setMode(props.initialMode)
          exit(true)
        }, 2000)
      })
    })
  }
  invokeIfAuthenticated(ifAuthenticated, () => {
    noteStore.onBoaSessionExpires()
    showCreateTemplateModal.value = false
    noteStore.setIsSaving(false)
  })
}

const discardNote = () => {
  enableFocusLock()
  exit(true).then(() => alertScreenReader('Canceled create new note'))
}

const discardRequested = () => {
  if (mode.value === 'editTemplate') {
    const indexOf = noteTemplates.value.findIndex(t => t.id === model.value.id)
    const template = noteTemplates.value[indexOf]
    const noDiff = trim(model.value.subject) === template.subject
      && model.value.body === template.body
      && !size(xor(model.value.topics, template.topics))
      && !size(xorBy(model.value.attachments, template.attachments, 'displayName'))
    if (noDiff) {
      discardTemplate()
    } else {
      showDiscardTemplateModal.value = true
      disableFocusLock()
    }
  } else {
    const unsavedChanges = !!trim(model.value.subject)
      || !!stripHtmlAndTrim(model.value.body)
      || size(model.value.topics)
      || size(model.value.attachments)
      || completeSidSet.value.size
    if (unsavedChanges) {
      showDiscardNoteModal.value = true
      disableFocusLock()
    } else {
      discardNote()
    }
  }
}

const discardTemplate = () => {
  showDiscardTemplateModal.value = false
  exit(true).then(() => alertScreenReader('Canceled edit template.'))
}

const dismissAlert = seconds => {
  dismissAlertSeconds.value = seconds
  if (seconds === 0) {
    alert.value = undefined
  }
}

const exit = revert => {
  alert.value = dismissAlertSeconds.value = undefined
  showCreateTemplateModal.value = showDiscardNoteModal.value = showDiscardTemplateModal.value = false
  dialogModel.value = null
  noteStore.setMode(null)
  return exitSession(revert).then(props.onClose)
}

const init = () => {
  return new Promise(resolve => {
    if (props.noteId) {
      getNote(props.noteId).then(resolve)
    } else {
      useContextStore().broadcast('begin-note-creation', {
        completeSidSet: [props.sid],
        subject: 'note-creation-is-starting'
      })
      createDraftNote(props.sid).then(resolve)
    }
  })
}

const removeAttachmentByIndex = index => {
  const attachment = noteStore.model.attachments[index]
  if (attachment && attachment.id) {
    if (isAutoSaveMode(mode.value)) {
      removeAttachment(model.value.id, attachment.id).then(() => {
        alertScreenReader(`Attachment '${attachment.displayName}' removed`)
      })
    }
    noteStore.removeAttachmentByIndex(index)
  }
}

const saveAsTemplate = () => {
  return new Promise(resolve => {
    noteStore.setIsSaving(true)
    const ifAuthenticated = () => {
      showCreateTemplateModal.value = true
      disableFocusLock()
    }
    alertScreenReader('Opening Name Template form')
    invokeIfAuthenticated(ifAuthenticated).finally(resolve)
  })
}

const showAlert = (value, seconds=3) => {
  alert.value = value
  dismissAlertSeconds.value = seconds
}

const updateTemplate = () => {
  noteStore.setIsSaving(true)
  alertScreenReader('Updating template')
  const newAttachments = filter(model.value.attachments, a => !a.id)
  if (newAttachments.length) {
    // File upload might take time; alert will be overwritten when API call is done.
    showAlert('Updating template...', 60)
  }
  updateNoteTemplate(
    model.value.body,
    model.value.deleteAttachmentIds,
    model.value.isPrivate,
    newAttachments,
    model.value.id,
    model.value.subject,
    model.value.topics,
  ).then(template => {
    noteStore.setIsSaving(false)
    alertScreenReader(`Template '${template.title}' updated`)
    exit(false)
  })
}

onBeforeUnmount(() => {
  noteStore.setIsCreateNoteModalOpen(false)
  noteStore.setMode(null)
  document.documentElement.classList.remove('modal-open')
  useContextStore().removeEventHandler('user-session-expired', noteStore.onBoaSessionExpires)
})

</script>

<!-- The 'batch' classes (below) are used by Vue transition above. -->
<style scoped>
.batch-enter-active { /* eslint-disable-line vue-scoped-css/no-unused-selector */
  -webkit-transition-duration: 0.3s;
  transition-duration: 0.3s;
  -webkit-transition-timing-function: ease-in;
  transition-timing-function: ease-in;
}
.batch-leave-active { /* eslint-disable-line vue-scoped-css/no-unused-selector */
  -webkit-transition-duration: 0.3s;
  transition-duration: 0.5s;
  -webkit-transition-timing-function: cubic-bezier(0, 1, 0.5, 1);
  transition-timing-function: cubic-bezier(0, 1, 0.5, 1);
}
.batch-enter-to, .batch-leave { /* eslint-disable-line vue-scoped-css/no-unused-selector */
  max-height: 280px;
  overflow: hidden;
}
.batch-enter, .batch-leave-to { /* eslint-disable-line vue-scoped-css/no-unused-selector */
  overflow: hidden;
  max-height: 0;
}
</style>
