<template>
  <div v-if="mode" role="dialog">
    <FocusLock
      :disabled="isFocusLockDisabled"
      class="create-note-container"
    >
      <div
        id="new-note-modal-container"
        class="mt-3"
        :class="{
          'd-none': _isNil(mode),
          'modal-content': ['createBatch', 'createNote', 'editDraft', 'editTemplate'].includes(mode),
          'mt-4': ['createBatch', 'editDraft'].includes(mode)
        }"
      >
        <CreateNoteHeader :cancel-primary-modal="cancelRequested" />
        <hr class="m-0" />
        <div class="mt-2 mr-3 mb-1 ml-3">
          <transition v-if="['createBatch', 'editDraft'].includes(mode)" name="batch-transition">
            <div v-show="mode !== 'editTemplate'">
              <BatchNoteFeatures :cancel="cancelRequested" />
              <hr />
            </div>
          </transition>
          <div class="ml-2 mr-3 mt-2 pl-2 pr-2">
            <b-alert
              id="alert-in-note-modal"
              :show="dismissAlertSeconds"
              class="font-weight-bolder w-100"
              dismissible
              fade
              variant="info"
              aria-live="polite"
              role="alert"
              @dismiss-count-down="dismissAlert"
            >
              <div class="d-flex">
                <div v-if="isSaving" class="mr-2">
                  <font-awesome icon="sync" spin />
                </div>
                <div>{{ alert }}</div>
              </div>
            </b-alert>
          </div>
          <div>
            <label
              id="create-note-subject-label"
              for="create-note-subject"
              class="font-size-14 font-weight-bolder mb-1"
            >
              <span class="sr-only">Note </span>Subject
            </label>
          </div>
          <div>
            <input
              id="create-note-subject"
              :value="model.subject"
              :disabled="isSaving || boaSessionExpired"
              :class="{'bg-light': isSaving}"
              aria-labelledby="create-note-subject-label"
              class="cohort-create-input-name"
              maxlength="255"
              type="text"
              @input="setSubjectPerEvent"
              @keydown.esc="cancelRequested"
            >
          </div>
          <div id="note-details">
            <RichTextEditor
              :disabled="isSaving || boaSessionExpired"
              :initial-value="model.body || ''"
              :is-in-modal="true"
              label="Note Details"
              :on-value-update="setBody"
              :show-advising-note-best-practices="true"
            />
          </div>
        </div>
        <div>
          <div class="mt-2 mr-3 mb-1 ml-3">
            <AdvisingNoteTopics
              :key="mode"
              :add-topic="addTopic"
              :disabled="isSaving || boaSessionExpired"
              :remove-topic="removeTopic"
              :topics="model.topics"
            />
          </div>
          <div class="mt-2 mr-3 mb-3 ml-3">
            <PrivacyPermissions
              v-if="currentUser.canAccessPrivateNotes"
              :disabled="isSaving || boaSessionExpired"
            />
          </div>
          <transition-group v-if="mode !== 'editTemplate'" name="batch-transition">
            <div key="0" class="mt-2 mr-3 mb-3 ml-3">
              <ContactMethod :disabled="isSaving || boaSessionExpired" />
            </div>
            <div key="1" class="mt-2 mb-3 ml-3">
              <ManuallySetDate :disabled="isSaving || boaSessionExpired" />
            </div>
          </transition-group>
          <div class="mt-2 mr-3 mb-1 ml-3">
            <AdvisingNoteAttachments
              :add-attachments="addNoteAttachments"
              :disabled="isSaving || boaSessionExpired"
              :existing-attachments="model.attachments"
            />
          </div>
        </div>
        <hr class="my-2" />
        <div>
          <CreateNoteFooter
            :cancel="cancelRequested"
            :save-as-template="saveAsTemplate"
            :update-note="updateNote"
            :update-template="updateTemplate"
          />
        </div>
      </div>
    </FocusLock>
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
  </div>
</template>

<script>
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import BatchNoteFeatures from '@/components/note/BatchNoteFeatures'
import ContactMethod from '@/components/note/ContactMethod'
import Context from '@/mixins/Context'
import CreateNoteFooter from '@/components/note/CreateNoteFooter'
import CreateNoteHeader from '@/components/note/CreateNoteHeader'
import CreateTemplateModal from '@/components/note/CreateTemplateModal'
import FocusLock from 'vue-focus-lock'
import ManuallySetDate from '@/components/note/ManuallySetDate'
import NoteEditSession from '@/mixins/NoteEditSession'
import PrivacyPermissions from '@/components/note/PrivacyPermissions'
import RichTextEditor from '@/components/util/RichTextEditor'
import store from '@/store'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/store/modules/context'
import {addAttachments, createDraftNote, getNote} from '@/api/notes'
import {createNoteTemplate, getMyNoteTemplates, updateNoteTemplate} from '@/api/note-templates'
import {getUserProfile} from '@/api/user'
import {
  exitSession,
  isAutoSaveMode,
  setNoteRecipient,
  setSubjectPerEvent,
  updateAdvisingNote
} from '@/store/modules/note-edit-session/utils'

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
    FocusLock,
    ManuallySetDate,
    PrivacyPermissions,
    RichTextEditor
  },
  mixins: [Context, NoteEditSession, Util],
  props: {
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
    }
  },
  data: () => ({
    alert: undefined,
    dismissAlertSeconds: 0,
    showCreateTemplateModal: false,
    showDiscardNoteModal: false,
    showDiscardTemplateModal: false,
    showErrorPopover: false
  }),
  created() {
    // remove scrollbar for content behind the modal
    document.body.classList.add('modal-open')
    getMyNoteTemplates().then(this.setNoteTemplates)
    this.resetModel()
    this.init().then(note => {
      const onFinish = () => {
        this.setMode(this.initialMode)
        this.alertScreenReader(this.mode === 'createNote' ? 'Create note form is open.' : 'Create batch note form is open.')
        this.setEventHandler('user-session-expired', this.onBoaSessionExpires)
      }
      this.setModel(note)
      if (note.sid) {
        setNoteRecipient(note.sid).then(onFinish)
      } else {
        onFinish()
      }
    })
  },
  beforeDestroy() {
    document.body.classList.remove('modal-open')
    this.removeEventHandler('user-session-expired', this.onBoaSessionExpires)
  },
  methods: {
    addNoteAttachments(attachments) {
      if (isAutoSaveMode(this.mode)) {
        this.setIsSaving(true)
        addAttachments(this.model.id, attachments).then(response => {
          store.commit('note/setAttachments', response.attachments)
          alertScreenReader('Attachment added', 'assertive')
          this.setIsSaving(false)
        })
      } else {
        this.setAttachments(attachments)
      }
    },
    cancelRequested() {
      if (this.mode === 'editTemplate') {
        const indexOf = this.noteTemplates.findIndex(t => t.id === this.model.id)
        const template = this.noteTemplates[indexOf]
        const noDiff = this._trim(this.model.subject) === template.subject
          && this.model.body === template.body
          && !this._size(this._xor(this.model.topics, template.topics))
          && !this._size(this._xorBy(this.model.attachments, template.attachments, 'displayName'))
        if (noDiff) {
          this.discardTemplate()
        } else {
          this.showDiscardTemplateModal = true
          this.disableFocusLock()
        }
      } else {
        const unsavedChanges = this._trim(this.model.subject)
          || this.stripHtmlAndTrim(this.model.body)
          || this._size(this.model.topics)
          || this._size(this.model.attachments)
          || this.completeSidSet.length
        if (unsavedChanges) {
          this.showDiscardNoteModal = true
          this.disableFocusLock()
        } else {
          this.discardNote()
        }
      }
    },
    cancelCreateTemplate() {
      this.setIsSaving(false)
      this.showCreateTemplateModal = false
      this.enableFocusLock()
    },
    cancelDiscardNote() {
      this.showDiscardNoteModal = false
      this.enableFocusLock()
      this.alertScreenReader('Continue editing note.')
      this.putFocusNextTick('create-note-subject')
    },
    cancelDiscardTemplate() {
      this.showDiscardTemplateModal = false
      this.putFocusNextTick('create-note-subject')
      this.enableFocusLock()
    },
    createTemplate(title) {
      this.setIsSaving(true)
      const ifAuthenticated = () => {
        this.showCreateTemplateModal = false
        this.enableFocusLock()
        // File upload might take time; alert will be overwritten when API call is done.
        this.showAlert('Creating template...', 60)
        // Save draft before creating template.
        updateAdvisingNote().then(() => {
          createNoteTemplate(this.model.id, title).then(() => {
            this.showAlert(`Template '${title}' created.`)
            setTimeout(() => {
              // Creating a note-template was the user's purpose so we delete any incidental draft note.
              this.setMode(this.initialMode)
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
      this.enableFocusLock()
      this.alertScreenReader('Canceled create new note')
      this.exit(true)
    },
    discardTemplate() {
      this.showDiscardTemplateModal = false
      this.alertScreenReader('Canceled create template.')
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
          this.broadcast('begin-note-creation', {
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
          this.onBoaSessionExpires()
          onReject()
        }
      })
    },
    saveAsTemplate() {
      this.setIsSaving(true)
      const ifAuthenticated = () => {
        this.showCreateTemplateModal = true
        this.disableFocusLock()
      }
      this.invokeIfAuthenticated(ifAuthenticated)
    },
    setSubjectPerEvent,
    showAlert(alert, seconds=3) {
      this.alert = alert
      this.dismissAlertSeconds = seconds
    },
    toggleShowCreateTemplateModal(show) {
      this.showCreateTemplateModal = show
      const toggle = show ? this.disableFocusLock : this.enableFocusLock
      toggle()
    },
    updateNote() {
      this.setIsSaving(true)
      const ifAuthenticated = () => {
        if (this.model.isDraft || (this.model.subject && this.completeSidSet.length)) {
          // File upload might take time; alert will be overwritten when API call is done.
          this.showAlert('Creating note...', 60)
          updateAdvisingNote().then(() => {
            this.setIsSaving(false)
            this.alertScreenReader(this.mode.includes('create') ? 'Note created' : 'Note saved')
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
      const newAttachments = this._filter(this.model.attachments, a => !a.id)
      if (newAttachments.length) {
        // File upload might take time; alert will be overwritten when API call is done.
        this.showAlert('Updating template...', 60)
      }
      updateNoteTemplate(
        this.model.body,
        this.model.deleteAttachmentIds,
        this.model.isPrivate,
        newAttachments,
        this.model.id,
        this.model.subject,
        this.model.topics,
      ).then(template => {
        this.setIsSaving(false)
        this.alertScreenReader(`Template '${template.title}' updated`)
        this.exit(false)
      })
    }
  }
}
</script>

<!-- The 'batch' classes (below) are used by Vue transition above. -->
<style scoped>
.batch-enter-active {
  -webkit-transition-duration: 0.3s;
  transition-duration: 0.3s;
  -webkit-transition-timing-function: ease-in;
  transition-timing-function: ease-in;
}
.batch-leave-active {
  -webkit-transition-duration: 0.3s;
  transition-duration: 0.5s;
  -webkit-transition-timing-function: cubic-bezier(0, 1, 0.5, 1);
  transition-timing-function: cubic-bezier(0, 1, 0.5, 1);
}
.batch-enter-to, .batch-leave {
  max-height: 280px;
  overflow: hidden;
}
.batch-enter, .batch-leave-to {
  overflow: hidden;
  max-height: 0;
}
.create-note-container {
  background-color: rgb(0,0,0);
  background-color: rgba(0,0,0,0.4);
  display: block;
  height: 100%;
  left: 0;
  overflow: auto;
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 100;
}
.modal-content {
  background-color: #fff;
  margin: 140px auto auto auto;
  padding-bottom: 20px;
  border: 1px solid #888;
  width: 60%;
}
</style>
