<template>
  <form class="edit-note-form" @submit.prevent="save">
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
            variant="primary"
            @click="save"
          >
            Save
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
    <div v-if="$_.size(model.attachments)">
      <div class="pill-list-header mt-3 mb-1">{{ $_.size(model.attachments) === 1 ? 'Attachment' : 'Attachments' }}</div>
      <ul class="pill-list pl-0">
        <li
          v-for="(attachment, index) in model.attachments"
          :id="`note-${model.id}-attachment-${index}`"
          :key="attachment.id"
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
import Context from '@/mixins/Context'
import NoteEditSession from '@/mixins/NoteEditSession'
import RichTextEditor from '@/components/util/RichTextEditor'
import SessionExpired from '@/components/note/SessionExpired'
import Util from '@/mixins/Util'
import {getNote, updateNote} from '@/api/notes'
import {getUserProfile} from '@/api/user'

export default {
  name: 'EditAdvisingNote',
  components: {AdvisingNoteTopics, AreYouSureModal, RichTextEditor, SessionExpired},
  mixins: [Context, NoteEditSession, Util],
  props: {
    afterCancel: Function,
    afterSaved: Function,
    noteId: Number
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
      this.setModel(this.$_.cloneDeep(note))
      this.addSid(note.sid)
      this.setMode('edit')
      this.$putFocusNextTick('edit-note-subject')
      this.alertScreenReader('Edit note form is open.')
    })
    this.$eventHub.on('user-session-expired', () => {
      this.onBoaSessionExpires()
    })
  },
  methods: {
    cancelRequested() {
      this.clearErrors()
      getNote(this.noteId).then(note => {
        const isPristine = this.$_.trim(this.model.subject) === note.subject
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
      this.alertScreenReader('Edit note form cancelled.')
      this.exit()
    },
    cancelTheCancel() {
      this.alertScreenReader('Continue editing note.')
      this.showAreYouSureModal = false
      this.$putFocusNextTick('edit-note-subject')
    },
    clearErrors() {
      this.error = null
      this.showErrorPopover = false
    },
    exit() {
      this.clearErrors()
      this.exitSession()
    },
    save() {
      const ifAuthenticated = () => {
        const trimmedSubject = this.$_.trim(this.model.subject)
        if (trimmedSubject) {
          updateNote(this.model.id, trimmedSubject, this.$_.trim(this.model.body), this.model.topics).then(updatedNote => {
            this.afterSaved(updatedNote)
            this.alertScreenReader('Changes to note have been saved')
            this.exit()
          })
        } else {
          this.error = 'Subject is required'
          this.showErrorPopover = true
          this.alertScreenReader(`Validation failed: ${this.error}`)
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
