<template>
  <form class="edit-note-form" @submit.prevent="save">
    <div v-if="model.isDraft" class="font-size-18 has-error p-2">
      <font-awesome icon="exclamation-triangle" class="pr-1" />
      You are editing a draft note.
    </div>
    <div>
      <label id="edit-note-subject-label" class="font-weight-bold" for="edit-note-subject">Subject</label>
    </div>
    <div>
      <input
        id="edit-note-subject"
        :value="model.subject"
        aria-labelledby="edit-note-subject-label"
        class="cohort-create-input-name"
        type="text"
        maxlength="255"
        @input="setSubjectPerEvent"
        @keydown.esc="cancelRequested"
      >
    </div>
    <div>
      <span id="edit-note-details" class="bg-transparent note-details-editor">
        <RichTextEditor
          :disabled="boaSessionExpired"
          :initial-value="model.body || ''"
          label="Note Details"
          :on-value-update="setBody"
        />
      </span>
    </div>
    <div>
      <AdvisingNoteTopics
        :disabled="boaSessionExpired"
        :function-add="addTopic"
        :function-remove="removeTopic"
        :note-id="model.id"
        :topics="model.topics"
      />
    </div>
    <div v-if="$currentUser.canAccessPrivateNotes" class="pb-3">
      <PrivacyPermissions :disabled="isSaving || boaSessionExpired" />
    </div>
    <div class="pb-3">
      <ContactMethod :disabled="isSaving || boaSessionExpired" />
    </div>
    <div class="pb-3">
      <ManuallySetDate :disabled="isSaving || boaSessionExpired" />
    </div>
    <div>
      <div
        v-if="boaSessionExpired"
        id="uh-oh-session-time-out"
        aria-live="polite"
        class="pl-3 pr-3"
        role="alert"
      >
        <SessionExpired />
      </div>
      <div v-if="!boaSessionExpired" class="d-flex mt-2 mb-2">
        <div>
          <b-btn
            id="save-note-button"
            class="btn-primary-color-override"
            :disabled="!sids.length || !_trim(model.subject)"
            variant="primary"
            @click="() => save(false)"
          >
            {{ model.isDraft ? 'Publish' : 'Save' }}
          </b-btn>
        </div>
        <div v-if="model.isDraft">
          <b-btn
            id="update-draft-note-button"
            variant="link"
            @click="() => save(true)"
          >
            Update Draft
          </b-btn>
        </div>
        <div>
          <b-btn
            id="cancel-edit-note-button"
            variant="link"
            @click.stop="cancelRequested"
            @keypress.enter.stop="cancelRequested"
          >
            Cancel
          </b-btn>
        </div>
      </div>
    </div>
    <AreYouSureModal
      v-if="showAreYouSureModal"
      :function-cancel="cancelTheCancel"
      :function-confirm="cancelConfirmed"
      :show-modal="showAreYouSureModal"
      modal-header="Discard unsaved changes?"
    />
    <div v-if="_size(model.attachments)">
      <div class="pill-list-header mt-3 mb-1">{{ _size(model.attachments) === 1 ? 'Attachment' : 'Attachments' }}</div>
      <ul class="pill-list pl-0">
        <li
          v-for="(attachment, index) in model.attachments"
          :id="`note-${model.id}-attachment-${index}`"
          :key="`${attachment.id}-${index}`"
          class="mt-2"
          @click.stop
          @keyup.stop
        >
          <span class="pill pill-attachment text-nowrap">
            <font-awesome icon="paperclip" class="pr-1 pl-1" />
            {{ attachment.displayName }}
          </span>
        </li>
      </ul>
    </div>
    <b-popover
      v-if="showErrorPopover"
      :show.sync="showErrorPopover"
      placement="top"
      target="edit-note-subject"
      aria-live="polite"
      role="alert"
    >
      <span id="popover-error-message" class="has-error">{{ error }}</span>
    </b-popover>
  </form>
</template>

<script>
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import ContactMethod from '@/components/note/ContactMethod'
import Context from '@/mixins/Context'
import ManuallySetDate from '@/components/note/ManuallySetDate'
import NoteEditSession from '@/mixins/NoteEditSession'
import PrivacyPermissions from '@/components/note/PrivacyPermissions'
import RichTextEditor from '@/components/util/RichTextEditor'
import SessionExpired from '@/components/note/SessionExpired'
import Util from '@/mixins/Util'
import {getNote, updateNote} from '@/api/notes'
import {getUserProfile} from '@/api/user'

export default {
  name: 'EditAdvisingNote',
  components: {
    AdvisingNoteTopics,
    AreYouSureModal,
    ContactMethod,
    ManuallySetDate,
    PrivacyPermissions,
    RichTextEditor,
    SessionExpired
  },
  mixins: [Context, NoteEditSession, Util],
  props: {
    afterCancel: {
      required: true,
      type: Function
    },
    afterSaved: {
      required: true,
      type: Function
    },
    noteId: {
      required: true,
      type: Number
    }
  },
  data: () => ({
    error: undefined,
    showAreYouSureModal: false,
    showErrorPopover: false,
    topic: undefined
  }),
  created() {
    getNote(this.noteId).then(note => {
      this.resetModel()
      this.setModel(note)
      // A draft-note may have a null SID value.
      if (note.sid) {
        this.addSid(note.sid)
      }
      this.setMode('editNote')
      this.$putFocusNextTick('edit-note-subject')
      this.$announcer.polite('Edit note form is open.')
    })
    this.setEventHandler('user-session-expired', () => {
      this.onBoaSessionExpires()
    })
  },
  methods: {
    cancelRequested() {
      this.clearErrors()
      getNote(this.noteId).then(note => {
        const isPristine = this._trim(this.model.subject) === note.subject
          && this.stripHtmlAndTrim(this.model.body) === this.stripHtmlAndTrim(note.body)
        if (isPristine) {
          this.cancelConfirmed()
        } else {
          this.showAreYouSureModal = true
        }
      })
    },
    cancelConfirmed() {
      this.afterCancel()
      this.$announcer.polite('Edit note form canceled.')
      this.exit(true)
    },
    cancelTheCancel() {
      this.$announcer.polite('Continue editing note.')
      this.showAreYouSureModal = false
      this.$putFocusNextTick('edit-note-subject')
    },
    clearErrors() {
      this.error = null
      this.showErrorPopover = false
    },
    exit(revert) {
      this.clearErrors()
      this.exitSession(revert)
    },
    save(isDraft) {
      const ifAuthenticated = () => {
        const trimmedSubject = this._trim(this.model.subject)
        const setDate = this.model.setDate ? this.$moment(this.model.setDate).format('YYYY-MM-DD') : null
        if (trimmedSubject || this.model.isDraft) {
          updateNote(
            this.model.id,
            this._trim(this.model.body),
            [],
            this.model.contactType,
            [],
            isDraft,
            this.model.isPrivate,
            setDate,
            this.sids,
            trimmedSubject,
            [],
            this.model.topics
          ).then(updatedNote => {
            this.afterSaved(updatedNote)
            this.$announcer.polite('Changes to note have been saved')
            this.exit(false)
          })
        } else {
          this.error = 'Subject is required'
          this.showErrorPopover = true
          this.$announcer.polite(`Validation failed: ${this.error}`)
          this.$putFocusNextTick('edit-note-subject')
        }
      }
      getUserProfile().then(data => {
        if (data.isAuthenticated) {
          ifAuthenticated()
        } else {
          this.onBoaSessionExpires()
        }
      })
    }
  }
}
</script>

<style scoped>
.edit-note-form {
  flex-basis: 100%;
}
</style>
