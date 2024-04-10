<template>
  <form class="edit-note-form" @submit.prevent="save">
    <div v-if="useNoteStore().model.isDraft" class="font-size-18 text-error p-2">
      <v-icon :icon="mdiAlertRhombus" class="pr-1" />
      You are editing a draft note.
    </div>
    <label id="edit-note-subject-label" class="font-weight-bold" for="edit-note-subject">Subject</label>
    <v-text-field
      id="edit-note-subject"
      :model-value="useNoteStore().model.subject"
      aria-labelledby="edit-note-subject-label"
      class="cohort-create-input-name"
      type="text"
      maxlength="255"
      @input="setSubjectPerEvent"
      @keydown.esc="cancelRequested"
    ></v-text-field>
    <div>
      <span id="edit-note-details" class="bg-transparent note-details-editor">
        <RichTextEditor
          :disabled="useNoteStore().boaSessionExpired"
          :initial-value="useNoteStore().model.body || ''"
          label="Note Details"
          :on-value-update="setBody"
          :show-advising-note-best-practices="true"
        />
      </span>
    </div>
    <div>
      <AdvisingNoteTopics
        :disabled="useNoteStore().boaSessionExpired"
        :add-topic="addTopic"
        :note-id="useNoteStore().model.id"
        :remove-topic="removeTopic"
        :topics="useNoteStore().model.topics"
      />
    </div>
    <div v-if="currentUser.canAccessPrivateNotes" class="pb-3">
      <PrivacyPermissions :disabled="useNoteStore().isSaving || useNoteStore().boaSessionExpired" />
    </div>
    <div class="pb-3">
      <ContactMethod :disabled="useNoteStore().isSaving || useNoteStore().boaSessionExpired" />
    </div>
    <div class="pb-3">
      <ManuallySetDate :disabled="useNoteStore().isSaving || useNoteStore().boaSessionExpired" />
    </div>
    <div>
      <div
        v-if="useNoteStore().boaSessionExpired"
        id="uh-oh-session-time-out"
        aria-live="polite"
        class="pl-3 pr-3"
        role="alert"
      >
        <SessionExpired />
      </div>
      <div v-if="!useNoteStore().boaSessionExpired" class="d-flex mt-2 mb-2">
        <div>
          <v-btn
            id="save-note-button"
            class="btn-primary-color-override"
            :disabled="!recipients.sids.length || !trim(useNoteStore().model.subject)"
            variant="primary"
            @click="() => save(false)"
          >
            {{ useNoteStore().model.isDraft ? 'Publish' : 'Save' }}
          </v-btn>
        </div>
        <div v-if="useNoteStore().model.isDraft">
          <v-btn
            id="update-draft-note-button"
            variant="link"
            @click="() => save(true)"
          >
            Update Draft
          </v-btn>
        </div>
        <div>
          <v-btn
            id="cancel-edit-note-button"
            variant="link"
            @click.stop="cancelRequested"
            @keypress.enter.stop="cancelRequested"
          >
            Cancel
          </v-btn>
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
    <div v-if="size(useNoteStore().model.attachments)">
      <div class="pill-list-header mt-3 mb-1">{{ size(useNoteStore().model.attachments) === 1 ? 'Attachment' : 'Attachments' }}</div>
      <ul class="pill-list pl-0">
        <li
          v-for="(attachment, index) in useNoteStore().model.attachments"
          :id="`note-${useNoteStore().model.id}-attachment-${index}`"
          :key="`${attachment.id}-${index}`"
          class="mt-2"
          @click.stop
          @keyup.stop
        >
          <span class="pill pill-attachment text-no-wrap">
            <v-icon :icon="mdiPaperclip" class="pr-1 pl-1" />
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
      <span id="popover-error-message" class="text-error">{{ error }}</span>
    </b-popover>
  </form>
</template>

<script setup>
import {mdiAlertRhombus, mdiPaperclip} from '@mdi/js'
</script>

<script>
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import ContactMethod from '@/components/note/ContactMethod'
import ManuallySetDate from '@/components/note/ManuallySetDate'
import PrivacyPermissions from '@/components/note/PrivacyPermissions'
import RichTextEditor from '@/components/util/RichTextEditor'
import SessionExpired from '@/components/note/SessionExpired'
import {exitSession, setNoteRecipient, setSubjectPerEvent} from '@/stores/note-edit-session/utils'
import {getNote, updateNote} from '@/api/notes'
import {getUserProfile} from '@/api/user'
import {DateTime} from 'luxon'
import {putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {size, trim} from 'lodash'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

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
      const onFinish = () => {
        useNoteStore().setMode('editNote')
        putFocusNextTick('edit-note-subject')
        useContextStore().alertScreenReader('Edit note form is open.')
      }
      useNoteStore().resetModel()
      useNoteStore().setModel(note)
      if (note.sid) {
        setNoteRecipient(note.sid).then(onFinish())
      } else {
        // A draft-note may have a null SID value.
        onFinish()
      }
    })
    useContextStore().setEventHandler('user-session-expired', useNoteStore().onBoaSessionExpires)
  },
  beforeUnmount() {
    useContextStore().removeEventHandler('user-session-expired', useNoteStore().onBoaSessionExpires)
  },
  methods: {
    cancelRequested() {
      this.clearErrors()
      getNote(this.noteId).then(note => {
        const isPristine = trim(this.model.subject) === note.subject
          && stripHtmlAndTrim(this.model.body) === stripHtmlAndTrim(note.body)
        if (isPristine) {
          this.cancelConfirmed()
        } else {
          this.showAreYouSureModal = true
        }
      })
    },
    cancelConfirmed() {
      this.afterCancel()
      useContextStore().alertScreenReader('Edit note form canceled.')
      this.exit(true)
    },
    cancelTheCancel() {
      useContextStore().alertScreenReader('Continue editing note.')
      this.showAreYouSureModal = false
      putFocusNextTick('edit-note-subject')
    },
    clearErrors() {
      this.error = null
      this.showErrorPopover = false
    },
    exit(revert) {
      this.clearErrors()
      exitSession(revert)
    },
    save(isDraft) {
      const ifAuthenticated = () => {
        const trimmedSubject = trim(this.model.subject)
        const setDate = this.model.setDate ? DateTime.fromJSDate(this.model.setDate).toFormat('YYYY-MM-DD') : null
        if (trimmedSubject || this.model.isDraft) {
          updateNote(
            this.model.id,
            trim(this.model.body),
            [],
            this.model.contactType,
            [],
            isDraft,
            this.model.isPrivate,
            setDate,
            this.recipients.sids,
            trimmedSubject,
            [],
            this.model.topics
          ).then(updatedNote => {
            this.afterSaved(updatedNote)
            useContextStore().alertScreenReader('Changes to note have been saved')
            this.exit(false)
          })
        } else {
          this.error = 'Subject is required'
          this.showErrorPopover = true
          useContextStore().alertScreenReader(`Validation failed: ${this.error}`)
          putFocusNextTick('edit-note-subject')
        }
      }
      getUserProfile().then(data => {
        if (data.isAuthenticated) {
          ifAuthenticated()
        } else {
          useNoteStore().onBoaSessionExpires()
        }
      })
    },
    setSubjectPerEvent,
    size,
    trim
  }
}
</script>

<style scoped>
.edit-note-form {
  flex-basis: 100%;
}
</style>
