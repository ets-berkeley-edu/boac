<template>
  <v-overlay
    :model-value="isOpen"
    class="justify-center overflow-auto"
    persistent
    scroll-strategy="reposition"
    width="100%"
  >
    <v-card
      id="new-note-modal-container"
      class="modal-content mt-3"
      :class="{
        'mt-4': ['createBatch', 'editDraft'].includes(useNoteStore().mode)
      }"
      min-width="500"
    >
      <CreateNoteHeader :cancel-primary-modal="cancelRequested" />
      <hr />
      <div class="px-4">
        <Transition v-if="['createBatch', 'editDraft'].includes(useNoteStore().mode)" name="batch-transition">
          <div v-show="useNoteStore().mode !== 'editTemplate'">
            <BatchNoteFeatures :cancel="cancelRequested" />
          </div>
        </Transition>
      </div>
      <hr v-if="useNoteStore().mode !== 'editTemplate'" />
      <div class="px-4">
        <v-alert
          id="alert-in-note-modal"
          :model-value="hasAlert"
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
            <div v-if="useNoteStore().isSaving" class="mr-2">
              <v-icon :icon="mdiSync" spin />
            </div>
            <div>{{ alert }}</div>
          </div>
        </v-alert>
        <label
          id="create-note-subject-label"
          for="create-note-subject"
          class="font-size-14 font-weight-bold"
        >
          <span class="sr-only">Note </span>Subject
        </label>
        <v-text-field
          id="create-note-subject"
          :model-value="useNoteStore().model.subject"
          aria-labelledby="create-note-subject-label"
          class="mt-2"
          :class="{'bg-light': useNoteStore().isSaving}"
          color="primary"
          density="compact"
          :disabled="useNoteStore().isSaving || useNoteStore().boaSessionExpired"
          maxlength="255"
          type="text"
          variant="outlined"
          @input="setSubjectPerEvent"
          @keydown.esc="cancelRequested"
        ></v-text-field>
        <div id="note-details">
          <RichTextEditor
            v-if="isOpen"
            :disabled="useNoteStore().isSaving || useNoteStore().boaSessionExpired"
            :initial-value="useNoteStore().model.body || ''"
            :is-in-modal="true"
            label="Note Details"
            :on-value-update="useNoteStore().setBody"
            :show-advising-note-best-practices="true"
          />
        </div>
      </div>
      <div class="pa-4">
        <AdvisingNoteTopics :key="useNoteStore().mode" />
        <PrivacyPermissions v-if="useContextStore().currentUser.canAccessPrivateNotes" />
        <TransitionGroup v-if="useNoteStore().mode !== 'editTemplate'" name="batch-transition">
          <div key="0" class="pt-4">
            <ContactMethod />
          </div>
          <div key="1" class="pt-4">
            <ManuallySetDate />
          </div>
        </TransitionGroup>
        <div class="pt-5">
          <AdvisingNoteAttachments
            :add-attachments="addNoteAttachments"
          />
        </div>
      </div>
      <hr class="mt-0" />
      <CreateNoteFooter
        :cancel="cancelRequested"
        :save-as-template="saveAsTemplate"
        :update-note="updateNote"
        :update-template="updateTemplate"
      />
    </v-card>
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
      :on-hidden="() => setIsSaving(false)"
      :toggle-show="toggleShowCreateTemplateModal"
    />
    <AreYouSureModal
      v-if="showDiscardTemplateModal"
      :function-cancel="cancelDiscardTemplate"
      :function-confirm="discardTemplate"
      :show-modal="showDiscardTemplateModal"
      modal-header="Discard unsaved template?"
    />
  </v-overlay>
</template>

<script setup>
import {mdiSync} from '@mdi/js'
</script>

<script>
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
import {createNoteTemplate, getMyNoteTemplates, updateNoteTemplate} from '@/api/note-templates'
import {disableFocusLock, enableFocusLock, exitSession, isAutoSaveMode, setSubjectPerEvent, updateAdvisingNote} from '@/stores/note-edit-session/utils'
import {filter, size, trim, xor, xorBy} from 'lodash'
import {getUserProfile} from '@/api/user'
import {putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

export default {
  name: 'EditBatchNoteModal',
  components: {
    AdvisingNoteAttachments,
    AdvisingNoteTopics,
    AreYouSureModal,
    BatchNoteFeatures,
    ContactMethod,
    CreateNoteFooter,
    CreateNoteHeader,
    CreateTemplateModal,
    ManuallySetDate,
    PrivacyPermissions,
    RichTextEditor
  },
  props: {
    initialMode: {
      required: true,
      type: String
    },
    isOpen: {
      required: true,
      type: Boolean
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
  },
  data: () => ({
    alert: undefined,
    dismissAlertSeconds: undefined,
    showCreateTemplateModal: false,
    showDiscardNoteModal: false,
    showDiscardTemplateModal: false,
    showErrorPopover: false
  }),
  computed: {
    hasAlert() {
      return alert && !!this.dismissAlertSeconds
    }
  },
  watch: {
    isOpen(newVal) {
      this.onChangeIsOpen(newVal)
    }
  },
  methods: {
    addNoteAttachments(attachments) {
      return new Promise(resolve => {
        if (isAutoSaveMode(useNoteStore().mode)) {
          this.setIsSaving(true)
          addAttachments(useNoteStore().model.id, attachments).then(response => {
            useNoteStore().setAttachments(response.attachments)
            useContextStore().alertScreenReader('Attachment added', 'assertive')
            this.setIsSaving(false)
            resolve()
          })
        } else {
          useNoteStore().setAttachments(attachments)
          resolve()
        }
      })
    },
    cancelRequested() {
      if (useNoteStore().mode === 'editTemplate') {
        const indexOf = useNoteStore().noteTemplates.findIndex(t => t.id === useNoteStore().model.id)
        const template = useNoteStore().noteTemplates[indexOf]
        const noDiff = trim(useNoteStore().model.subject) === template.subject
          && useNoteStore().model.body === template.body
          && !size(xor(useNoteStore().model.topics, template.topics))
          && !size(xorBy(useNoteStore().model.attachments, template.attachments, 'displayName'))
        if (noDiff) {
          this.discardTemplate()
        } else {
          this.showDiscardTemplateModal = true
          disableFocusLock()
        }
      } else {
        const unsavedChanges = trim(useNoteStore().model.subject)
          || stripHtmlAndTrim(useNoteStore().model.body)
          || size(useNoteStore().model.topics)
          || size(useNoteStore().model.attachments)
          || useNoteStore().completeSidSet.length
        if (unsavedChanges) {
          this.showDiscardNoteModal = true
          disableFocusLock()
        } else {
          this.discardNote()
        }
      }
    },
    cancelCreateTemplate() {
      this.setIsSaving(false)
      this.showCreateTemplateModal = false
      enableFocusLock()
    },
    cancelDiscardNote() {
      this.showDiscardNoteModal = false
      enableFocusLock()
      useContextStore().alertScreenReader('Continue editing note.')
      putFocusNextTick('create-note-subject')
    },
    cancelDiscardTemplate() {
      this.showDiscardTemplateModal = false
      putFocusNextTick('create-note-subject')
      enableFocusLock()
    },
    createTemplate(title) {
      this.setIsSaving(true)
      const ifAuthenticated = () => {
        this.showCreateTemplateModal = false
        enableFocusLock()
        // File upload might take time; alert will be overwritten when API call is done.
        this.showAlert('Creating template...', 60)
        // Save draft before creating template.
        updateAdvisingNote().then(() => {
          createNoteTemplate(useNoteStore().model.id, title).then(() => {
            this.showAlert(`Template '${title}' created.`)
            setTimeout(() => {
              // Creating a note-template was the user's purpose so we delete any incidental draft note.
              useNoteStore().setMode(this.initialMode)
              this.exit(true)
            }, 2000)
          })
        })
      }
      this.invokeIfAuthenticated(ifAuthenticated, () => {
        this.showCreateTemplateModal = false
        this.setIsSaving(false)
      })
    },
    discardNote() {
      enableFocusLock()
      useContextStore().alertScreenReader('Canceled create new note')
      this.exit(true)
    },
    discardTemplate() {
      this.showDiscardTemplateModal = false
      useContextStore().alertScreenReader('Canceled create template.')
      this.exit(true)
    },
    dismissAlert(seconds) {
      this.dismissAlertSeconds = seconds
      if (seconds === 0) {
        this.alert = undefined
      }
    },
    exit(revert) {
      this.alert = this.dismissAlertSeconds = undefined
      this.showCreateTemplateModal = this.showDiscardNoteModal = this.showDiscardTemplateModal = this.showErrorPopover = false
      exitSession(revert).then(this.onClose)
    },
    init() {
      return new Promise(resolve => {
        if (this.noteId) {
          getNote(this.noteId).then(resolve)
        } else {
          useContextStore().broadcast('begin-note-creation', {
            completeSidSet: [this.sid],
            subject: 'note-creation-is-starting'
          })
          createDraftNote(this.sid).then(resolve)
        }
      })
    },
    invokeIfAuthenticated(callback, onReject = () => {}) {
      getUserProfile().then(data => {
        if (data.isAuthenticated) {
          callback()
        } else {
          useNoteStore().onBoaSessionExpires()
          onReject()
        }
      })
    },
    onChangeIsOpen(isOpen) {
      if (isOpen) {
        // remove scrollbar for content behind the modal
        document.documentElement.classList.add('modal-open')
        getMyNoteTemplates().then(useNoteStore().setNoteTemplates)
        useNoteStore().resetModel()
        this.init().then(note => {
          const onFinish = () => {
            useNoteStore().setMode(this.initialMode)
            useContextStore().alertScreenReader(useNoteStore().mode === 'createNote' ? 'Create note form is open.' : 'Create batch note form is open.')
            putFocusNextTick('modal-header-note')
            useContextStore().setEventHandler('user-session-expired', useNoteStore().onBoaSessionExpires)
          }
          useNoteStore().setModel(note)
          if (note.sid) {
            useNoteStore().setNoteRecipient(note.sid).then(onFinish)
          } else {
            onFinish()
          }
        })
      } else {
        useNoteStore().setMode(undefined)
        document.documentElement.classList.remove('modal-open')
        useContextStore().removeEventHandler('user-session-expired', useNoteStore().onBoaSessionExpires)
      }
    },
    saveAsTemplate() {
      this.setIsSaving(true)
      const ifAuthenticated = () => {
        this.showCreateTemplateModal = true
        disableFocusLock()
      }
      this.invokeIfAuthenticated(ifAuthenticated)
    },
    setIsSaving(isSaving) {
      useNoteStore().setIsSaving(isSaving)
    },
    setSubjectPerEvent,
    showAlert(alert, seconds=3) {
      this.alert = alert
      this.dismissAlertSeconds = seconds
    },
    toggleShowCreateTemplateModal(show) {
      this.showCreateTemplateModal = show
      const toggle = show ? disableFocusLock : enableFocusLock
      toggle()
    },
    updateNote() {
      this.setIsSaving(true)
      const ifAuthenticated = () => {
        if (useNoteStore().model.isDraft || (useNoteStore().model.subject && useNoteStore().completeSidSet.length)) {
          // File upload might take time; alert will be overwritten when API call is done.
          this.showAlert('Creating note...', 60)
          updateAdvisingNote().then(() => {
            this.setIsSaving(false)
            useContextStore().alertScreenReader(useNoteStore().mode.includes('create') ? 'Note created' : 'Note saved')
            this.exit(false)
          })
        }
      }
      this.invokeIfAuthenticated(ifAuthenticated, () => {
        this.setIsSaving(false)
      })
    },
    updateTemplate() {
      this.setIsSaving(true)
      const newAttachments = filter(useNoteStore().model.attachments, a => !a.id)
      if (newAttachments.length) {
        // File upload might take time; alert will be overwritten when API call is done.
        this.showAlert('Updating template...', 60)
      }
      updateNoteTemplate(
        useNoteStore().model.body,
        useNoteStore().model.deleteAttachmentIds,
        useNoteStore().model.isPrivate,
        newAttachments,
        useNoteStore().model.id,
        useNoteStore().model.subject,
        useNoteStore().model.topics,
      ).then(template => {
        this.setIsSaving(false)
        useContextStore().alertScreenReader(`Template '${template.title}' updated`)
        this.exit(false)
      })
    },
    useNoteStore
  }
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
