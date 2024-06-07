<template>
  <v-dialog
    v-model="dialogModel"
    persistent
    width="800"
  >
    <v-card id="new-note-modal-container">
      <div
        class="default-margins mb-6 mr-6"
        :class="{'mt-4': ['createBatch', 'editDraft'].includes(mode)}"
      >
        <CreateNoteHeader :cancel-primary-modal="cancelRequested" />
        <hr />
        <div>
          <Transition v-if="['createBatch', 'editDraft'].includes(mode)" name="batch-transition">
            <div v-show="mode !== 'editTemplate'">
              <BatchNoteFeatures :cancel="cancelRequested" />
            </div>
          </Transition>
        </div>
        <hr v-if="mode !== 'editTemplate'" />
        <div>
          <v-alert
            v-if="alert"
            id="alert-in-note-modal"
            :model-value="alert && !!dismissAlertSeconds"
            aria-live="polite"
            class="font-weight-bold w-100 mb-2"
            closable
            color="info"
            density="comfortable"
            role="alert"
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
            @keydown.esc="cancelRequested"
          />
          <div id="note-details">
            <RichTextEditor
              :disabled="isSaving || boaSessionExpired"
              :initial-value="model.body || ''"
              :is-in-modal="true"
              label="Note Details"
              :on-value-update="useNoteStore().setBody"
              :show-advising-note-best-practices="true"
            />
          </div>
        </div>
        <div class="py-4">
          <AdvisingNoteTopics :key="mode" />
          <PrivacyPermissions v-if="useContextStore().currentUser.canAccessPrivateNotes" />
          <TransitionGroup v-if="mode !== 'editTemplate'" name="batch-transition">
            <div key="0" class="pt-4">
              <ContactMethod />
            </div>
            <div key="1" class="pt-4">
              <ManuallySetDate />
            </div>
          </TransitionGroup>
          <div class="pt-5">
            <AdvisingNoteAttachments :add-attachments="addNoteAttachments" />
          </div>
        </div>
        <hr class="mt-0" />
        <CreateNoteFooter
          :cancel="cancelRequested"
          :save-as-template="saveAsTemplate"
          :update-note="updateNote"
          :update-template="updateTemplate"
        />
      </div>
    </v-card>
  </v-dialog>
  <AreYouSureModal
    v-if="showDiscardNoteModal"
    :function-cancel="cancelDiscardNote"
    :function-confirm="discardNote"
    :show-modal="showDiscardNoteModal"
    modal-header="Discard unsaved note?"
  />
  <CreateTemplateModal
    :show-modal="showCreateTemplateModal"
    :cancel="cancelCreateTemplate"
    :create="createTemplate"
    :on-hidden="() => noteStore.setIsSaving(false)"
    :toggle-show="toggleShowCreateTemplateModal"
  />
  <AreYouSureModal
    v-if="showDiscardTemplateModal"
    :function-cancel="cancelDiscardTemplate"
    :function-confirm="discardTemplate"
    :show-modal="showDiscardTemplateModal"
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
import {addAttachments, createDraftNote, getNote} from '@/api/notes'
import {alertScreenReader, putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {createNoteTemplate, getMyNoteTemplates, updateNoteTemplate} from '@/api/note-templates'
import {disableFocusLock, enableFocusLock, exitSession, isAutoSaveMode, setSubjectPerEvent, updateAdvisingNote} from '@/stores/note-edit-session/utils'
import {filter, size, trim, xor, xorBy} from 'lodash'
import {getUserProfile} from '@/api/user'
import {mdiSync} from '@mdi/js'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'
import {watch} from 'vue'

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

let alert = undefined
let dismissAlertSeconds = undefined
let showCreateTemplateModal = false
let showDiscardNoteModal = false
let showDiscardTemplateModal = false

// eslint-disable-next-line vue/require-prop-types
const dialogModel = defineModel()
const noteStore = useNoteStore()
const {boaSessionExpired, completeSidSet, isSaving, mode, model, noteTemplates} = storeToRefs(noteStore)

watch(dialogModel, () => {
  if (dialogModel.value) {
    // remove scrollbar for content behind the modal
    document.documentElement.classList.add('modal-open')
    getMyNoteTemplates().then(noteStore.setNoteTemplates)
    noteStore.resetModel()
    init().then(note => {
      const onFinish = () => {
        noteStore.setMode(props.initialMode)
        alertScreenReader(mode === 'createNote' ? 'Create note form is open.' : 'Create batch note form is open.')
        putFocusNextTick(props.sid ? 'create-note-subject' : 'modal-header-note')
        useContextStore().setEventHandler('user-session-expired', noteStore.onBoaSessionExpires)
      }
      noteStore.setModel(note)
      if (note.sid) {
        noteStore.setNoteRecipient(note.sid).then(onFinish)
      } else {
        onFinish()
      }
    })
  } else {
    noteStore.setMode(undefined)
    document.documentElement.classList.remove('modal-open')
    useContextStore().removeEventHandler('user-session-expired', noteStore.onBoaSessionExpires)
  }
})

const addNoteAttachments = attachments => {
  return new Promise(resolve => {
    if (isAutoSaveMode(mode)) {
      noteStore.setIsSaving(true)
      addAttachments(model.id, attachments).then(response => {
        noteStore.setAttachments(response.attachments)
        alertScreenReader('Attachment added', 'assertive')
        noteStore.setIsSaving(false)
        resolve()
      })
    } else {
      noteStore.setAttachments(attachments)
      resolve()
    }
  })
}

const cancelRequested = () => {
  if (mode === 'editTemplate') {
    const indexOf = noteTemplates.findIndex(t => t.id === model.id)
    const template = noteTemplates[indexOf]
    const noDiff = trim(model.subject) === template.subject
      && model.body === template.body
      && !size(xor(model.topics, template.topics))
      && !size(xorBy(model.attachments, template.attachments, 'displayName'))
    if (noDiff) {
      discardTemplate()
    } else {
      showDiscardTemplateModal = true
      disableFocusLock()
    }
  } else {
    const unsavedChanges = trim(model.subject)
      || stripHtmlAndTrim(model.body)
      || size(model.topics)
      || size(model.attachments)
      || completeSidSet.length
    if (unsavedChanges) {
      showDiscardNoteModal = true
      disableFocusLock()
    } else {
      discardNote()
    }
  }
}

const cancelCreateTemplate = () => {
  noteStore.setIsSaving(false)
  showCreateTemplateModal = false
  enableFocusLock()
}

const cancelDiscardNote = () => {
  showDiscardNoteModal = false
  enableFocusLock()
  alertScreenReader('Continue editing note.')
  putFocusNextTick('create-note-subject')
}

const cancelDiscardTemplate = () => {
  showDiscardTemplateModal = false
  putFocusNextTick('create-note-subject')
  enableFocusLock()
}

const createTemplate = title => {
  noteStore.setIsSaving(true)
  const ifAuthenticated = () => {
    showCreateTemplateModal = false
    enableFocusLock()
    // File upload might take time; alert will be overwritten when API call is done.
    showAlert('Creating template...', 60)
    // Save draft before creating template.
    updateAdvisingNote().then(() => {
      createNoteTemplate(model.id, title).then(() => {
        showAlert(`Template '${title}' created.`)
        setTimeout(() => {
          // Creating a note-template was the user's purpose so we delete any incidental draft note.
          noteStore.setMode(props.initialMode)
          exit(true)
        }, 2000)
      })
    })
  }
  invokeIfAuthenticated(ifAuthenticated, () => {
    showCreateTemplateModal = false
    noteStore.setIsSaving(false)
  })
}

const discardNote = () => {
  enableFocusLock()
  alertScreenReader('Canceled create new note')
  exit(true)
}

const discardTemplate = () => {
  showDiscardTemplateModal = false
  alertScreenReader('Canceled create template.')
  exit(true)
}

const dismissAlert = seconds => {
  dismissAlertSeconds = seconds
  if (seconds === 0) {
    alert = undefined
  }
}

const exit = revert => {
  alert = dismissAlertSeconds = undefined
  showCreateTemplateModal = showDiscardNoteModal = showDiscardTemplateModal = false
  exitSession(revert).then(props.onClose)
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

const invokeIfAuthenticated = (callback, onReject = () => {}) => {
  getUserProfile().then(data => {
    if (data.isAuthenticated) {
      callback()
    } else {
      noteStore.onBoaSessionExpires()
      onReject()
    }
  })
}

const saveAsTemplate = () => {
  noteStore.setIsSaving(true)
  const ifAuthenticated = () => {
    showCreateTemplateModal = true
    disableFocusLock()
  }
  invokeIfAuthenticated(ifAuthenticated)
}

const showAlert = (value, seconds=3) => {
  alert = value
  dismissAlertSeconds = seconds
}

const toggleShowCreateTemplateModal = show => {
  showCreateTemplateModal = show
  const toggle = show ? disableFocusLock : enableFocusLock
  toggle()
}

const updateNote = () => {
  noteStore.setIsSaving(true)
  const ifAuthenticated = () => {
    if (model.isDraft || (model.subject && size(completeSidSet))) {
      // File upload might take time; alert will be overwritten when API call is done.
      showAlert('Creating note...', 60)
      updateAdvisingNote().then(() => {
        noteStore.setIsSaving(false)
        alertScreenReader(mode.includes('create') ? 'Note created' : 'Note saved')
        exit(false)
      })
    }
  }
  invokeIfAuthenticated(ifAuthenticated, () => {
    noteStore.setIsSaving(false)
  })
}

const updateTemplate = () => {
  noteStore.setIsSaving(true)
  const newAttachments = filter(model.attachments, a => !a.id)
  if (newAttachments.length) {
    // File upload might take time; alert will be overwritten when API call is done.
    showAlert('Updating template...', 60)
  }
  updateNoteTemplate(
    model.body,
    model.deleteAttachmentIds,
    model.isPrivate,
    newAttachments,
    model.id,
    model.subject,
    model.topics,
  ).then(template => {
    noteStore.setIsSaving(false)
    alertScreenReader(`Template '${template.title}' updated`)
    exit(false)
  })
}
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
