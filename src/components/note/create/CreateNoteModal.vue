<template>
  <div role="dialog">
    <FocusLock
      :disabled="isFocusLockDisabled"
      class="create-note-container"
    >
      <div
        id="new-note-modal-container"
        :class="{
          'd-none': $_.isNil(mode),
          'modal-content': $_.includes(['batch', 'create', 'editTemplate'], mode),
          'mt-4': isBatchFeature
        }"
      >
        <form @submit.prevent="submitForm">
          <CreateNoteHeader :cancel-primary-modal="cancelRequested" />
          <hr class="m-0" />
          <div class="mt-2 mr-3 mb-1 ml-3">
            <transition v-if="isBatchFeature" name="batch">
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
              <label id="create-note-subject-label" for="create-note-subject" class="font-size-14 font-weight-bolder mb-1"><span class="sr-only">Note </span>Subject</label>
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
                :initial-value="model.body || ''"
                :disabled="isSaving || boaSessionExpired"
                :is-in-modal="true"
                label="Note Details"
                :on-value-update="setBody"
              />
            </div>
          </div>
          <div>
            <div class="mt-2 mr-3 mb-1 ml-3">
              <AdvisingNoteTopics
                :key="mode"
                :disabled="isSaving || boaSessionExpired"
                :function-add="addTopic"
                :function-remove="removeTopic"
                :topics="model.topics"
              />
            </div>
            <div class="mt-2 mr-3 mb-3 ml-3">
              <PrivacyPermissions
                v-if="$currentUser.canAccessPrivateNotes"
                :disabled="isSaving || boaSessionExpired"
              />
            </div>
            <div class="mt-2 mr-3 mb-1 ml-3">
              <AdvisingNoteAttachments
                :add-attachment="addAttachment"
                :disabled="isSaving || boaSessionExpired"
                :existing-attachments="model.attachments"
                :remove-attachment="removeAttachment"
              />
            </div>
          </div>
          <hr />
          <div>
            <CreateNoteFooter
              :cancel="cancelRequested"
              :create-note="createNote"
              :save-as-template="saveAsTemplate"
              :update-template="updateTemplate"
            />
          </div>
        </form>
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
import BatchNoteFeatures from '@/components/note/create/BatchNoteFeatures'
import Context from '@/mixins/Context'
import CreateNoteFooter from '@/components/note/create/CreateNoteFooter'
import CreateNoteHeader from '@/components/note/create/CreateNoteHeader'
import CreateTemplateModal from '@/components/note/create/CreateTemplateModal'
import FocusLock from 'vue-focus-lock'
import NoteEditSession from '@/mixins/NoteEditSession'
import PrivacyPermissions from '@/components/note/create/PrivacyPermissions'
import RichTextEditor from '@/components/util/RichTextEditor'
import store from '@/store'
import Util from '@/mixins/Util'
import {createNoteTemplate, updateNoteTemplate} from '@/api/note-templates'
import {getUserProfile} from '@/api/user'

export default {
  name: 'CreateNoteModal',
  components: {
    AdvisingNoteAttachments,
    AdvisingNoteTopics,
    AreYouSureModal,
    BatchNoteFeatures,
    CreateNoteFooter,
    CreateNoteHeader,
    CreateTemplateModal,
    FocusLock,
    PrivacyPermissions,
    RichTextEditor
  },
  mixins: [Context, NoteEditSession, Util],
  props: {
    isBatchFeature: {
      required: true,
      type: Boolean
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
  mounted() {
    store.dispatch('noteEditSession/loadNoteTemplates')
    this.resetModel()
    this.setIsPrivate(false)
    if (this.sid) {
      this.addSid(this.sid)
    }
    this.setMode(this.isBatchFeature ? 'batch' : 'create')
    this.$announcer.polite(this.isBatchFeature ? 'Create batch note form is open.' : 'Create note form is open')
    this.$putFocusNextTick('modal-header-note')
    this.$eventHub.on('user-session-expired', () => {
      this.onBoaSessionExpires()
    })
  },
  methods: {
    cancelRequested() {
      if (this.mode === 'editTemplate') {
        const indexOf = this.noteTemplates.findIndex(t => t.id === this.model.id)
        const template = this.noteTemplates[indexOf]
        const noDiff = this.$_.trim(this.model.subject) === template.subject
          && this.model.body === template.body
          && !this.$_.size(this.$_.xor(this.model.topics, template.topics))
          && !this.$_.size(this.$_.xorBy(this.model.attachments, template.attachments, 'displayName'))
        if (noDiff) {
          this.discardTemplate()
        } else {
          this.showDiscardTemplateModal = true
          this.setFocusLockDisabled(true)
        }
      } else {
        const unsavedChanges = this.$_.trim(this.model.subject)
          || this.stripHtmlAndTrim(this.model.body)
          || this.$_.size(this.model.topics)
          || this.$_.size(this.model.attachments)
          || this.addedCohorts.length
          || this.addedCuratedGroups.length
        if (unsavedChanges) {
          this.showDiscardNoteModal = true
          this.setFocusLockDisabled(true)
        } else {
          this.discardNote()
        }
      }
    },
    cancelCreateTemplate() {
      this.showCreateTemplateModal = false
      this.$nextTick(() => {
        this.setFocusLockDisabled(false)
      })
    },
    cancelDiscardNote() {
      this.showDiscardNoteModal = false
      this.setFocusLockDisabled(false)
      this.$announcer.polite('Continue editing note.')
      this.$putFocusNextTick('create-note-subject')
    },
    cancelDiscardTemplate() {
      this.showDiscardTemplateModal = false
      this.$putFocusNextTick('create-note-subject')
      this.$nextTick(() => {
        this.setFocusLockDisabled(false)
      })
    },
    createNote() {
      const ifAuthenticated = () => {
        if (this.model.subject && this.completeSidSet.length) {
          this.setIsSaving(true)
          // File upload might take time; alert will be overwritten when API call is done.
          this.showAlert('Creating note...', 60)
          this.createAdvisingNotes().then(note => {
            this.setIsSaving(false)
            this.$announcer.polite(this.isBatchFeature ? `Note created for ${this.completeSidSet.length} students.` : 'New note saved.')
            this.exit(note)
          })
        }
      }
      this.invokeIfAuthenticated(ifAuthenticated, () => {
        this.setIsSaving(false)
      })
    },
    createTemplate(title) {
      const ifAuthenticated = () => {
        this.showCreateTemplateModal = false
        this.setIsSaving(true)
        this.setFocusLockDisabled(false)
        // File upload might take time; alert will be overwritten when API call is done.
        this.showAlert('Creating template...', 60)
        createNoteTemplate(
          this.model.attachments,
          this.model.body,
          this.model.isPrivate,
          this.model.subject,
          title,
          this.model.topics,
        ).then(template => {
          this.showAlert(`Template '${title}' created.`)
          this.setIsSaving(false)
          this.setModel({
            attachments: template.attachments,
            body: template.body,
            deleteAttachmentIds: [],
            id: undefined,
            isPrivate: this.model.isPrivate,
            subject: template.subject,
            topics: template.topics
          })
          this.setMode(this.isBatchFeature ? 'batch' : 'create')
          this.$putFocusNextTick('create-note-subject')
        })
      }
      this.invokeIfAuthenticated(ifAuthenticated, () => {
        this.showCreateTemplateModal = false
        this.setIsSaving(false)
      })
    },
    discardNote() {
      this.showDiscardNoteModal = false
      this.setFocusLockDisabled(false)
      this.dismissAlertSeconds = 0
      this.$announcer.polite('Canceled create new note')
      this.exit()
    },
    discardTemplate() {
      this.showDiscardTemplateModal = false
      this.resetModel(false)
      this.setMode(this.isBatchFeature ? 'batch' : 'create')
      this.$announcer.polite('Canceled create template.')
      this.$putFocusNextTick('create-note-subject')
      this.$nextTick(() => {
        this.setFocusLockDisabled(false)
      })
    },
    dismissAlert(seconds) {
      this.dismissAlertSeconds = seconds
      if (seconds === 0) {
        this.alert = undefined
      }
    },
    exit(note=undefined) {
      this.alert = this.dismissAlertSeconds = undefined
      this.showCreateTemplateModal = this.showDiscardNoteModal = this.showDiscardTemplateModal = this.showErrorPopover = false
      this.exitSession()
      this.onClose(note)
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
      const ifAuthenticated = () => {
        this.showCreateTemplateModal = true
        this.setFocusLockDisabled(true)
      }
      this.invokeIfAuthenticated(ifAuthenticated)
    },
    showAlert(alert, seconds=3) {
      this.alert = alert
      this.dismissAlertSeconds = seconds
    },
    submitForm() {
      if (this.mode === 'editTemplate') {
        this.updateTemplate()
      } else {
        this.createNote()
      }
    },
    toggleShowCreateTemplateModal(show) {
      this.showCreateTemplateModal = show
      this.setFocusLockDisabled(show)
    },
    updateTemplate() {
      this.setIsSaving(true)
      const newAttachments = this.$_.filter(this.model.attachments, a => !a.id)
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
        this.setModel({
          attachments: template.attachments,
          body: template.body,
          deleteAttachmentIds: [],
          id: undefined,
          isPrivate: this.model.isPrivate,
          subject: template.subject,
          topics: template.topics
        })
        this.setMode(this.isBatchFeature ? 'batch' : 'create')
        this.showAlert(`Template '${template.title}' updated`)
      })
    }
  }
}
</script>

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
  display: block;
  position: fixed;
  z-index: 3;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgb(0,0,0);
  background-color: rgba(0,0,0,0.4);
}
.modal-content {
  background-color: #fff;
  margin: 140px auto auto auto;
  padding-bottom: 20px;
  border: 1px solid #888;
  width: 60%;
}
</style>
