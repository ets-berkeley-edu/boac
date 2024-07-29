<template>
  <v-form
    ref="editNoteForm"
    class="edit-note-form"
    @submit.prevent="save"
  >
    <div v-if="noteStore.model.isDraft" class="font-size-18 text-error p-2">
      <v-icon :icon="mdiAlertRhombus" class="pr-1" />
      You are editing a draft note.
    </div>
    <label id="edit-note-subject-label" class="font-weight-bold" for="edit-note-subject">Subject</label>
    <v-text-field
      id="edit-note-subject"
      :model-value="noteStore.model.subject"
      aria-labelledby="edit-note-subject-label"
      bg-color="white"
      density="comfortable"
      maxlength="255"
      required
      :rules="[rules.required]"
      size="255"
      validate-on="submit"
      variant="outlined"
      @input="onInput"
      @keydown.esc="cancelRequested"
    ></v-text-field>
    <div>
      <span id="edit-note-details" class="bg-transparent note-details-editor">
        <RichTextEditor
          :disabled="noteStore.boaSessionExpired"
          :initial-value="noteStore.model.body || ''"
          label="Note Details"
          :on-value-update="noteStore.setBody"
          :show-advising-note-best-practices="true"
        />
      </span>
    </div>
    <div>
      <AdvisingNoteTopics />
    </div>
    <div v-if="currentUser.canAccessPrivateNotes" class="pb-3">
      <PrivacyPermissions :disabled="noteStore.isSaving || noteStore.boaSessionExpired" />
    </div>
    <div class="pb-3">
      <ContactMethod :disabled="noteStore.isSaving || noteStore.boaSessionExpired" />
    </div>
    <div class="pb-3">
      <ManuallySetDate :disabled="noteStore.isSaving || noteStore.boaSessionExpired" />
    </div>
    <div>
      <div
        v-if="noteStore.boaSessionExpired"
        id="uh-oh-session-time-out"
        aria-live="polite"
        class="pl-3 pr-3"
        role="alert"
      >
        <SessionExpired />
      </div>
      <div v-if="!noteStore.boaSessionExpired" class="d-flex mt-2 mb-2">
        <div>
          <v-btn
            id="save-note-button"
            class="mr-2"
            color="primary"
            :disabled="!noteStore.recipients.sids.length || !trim(noteStore.model.subject)"
            @click="() => save(false)"
          >
            {{ noteStore.model.isDraft ? 'Publish' : 'Save' }}
          </v-btn>
        </div>
        <div v-if="noteStore.model.isDraft">
          <v-btn
            id="update-draft-note-button"
            class="mr-2"
            color="primary"
            variant="text"
            @click="() => save(true)"
          >
            Update Draft
          </v-btn>
        </div>
        <div>
          <v-btn
            id="cancel-edit-note-button"
            color="primary"
            variant="text"
            @click.stop="cancelRequested"
            @keypress.enter.stop="cancelRequested"
          >
            Cancel
          </v-btn>
        </div>
      </div>
    </div>
    <AreYouSureModal
      v-model="showAreYouSureModal"
      :function-cancel="cancelTheCancel"
      :function-confirm="cancelConfirmed"
      modal-header="Discard unsaved changes?"
    />
    <div v-if="size(noteStore.model.attachments)">
      <div class="pill-list-header mt-3 mb-1">{{ size(noteStore.model.attachments) === 1 ? 'Attachment' : 'Attachments' }}</div>
      <ul class="pill-list pl-0">
        <li
          v-for="(attachment, index) in noteStore.model.attachments"
          :id="`note-${noteStore.model.id}-attachment-${index}`"
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
  </v-form>
</template>

<script setup>
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import {onBeforeMount, ref} from 'vue'
import ContactMethod from '@/components/note/ContactMethod'
import ManuallySetDate from '@/components/note/ManuallySetDate'
import {mdiAlertRhombus, mdiPaperclip} from '@mdi/js'
import PrivacyPermissions from '@/components/note/PrivacyPermissions'
import RichTextEditor from '@/components/util/RichTextEditor'
import SessionExpired from '@/components/note/SessionExpired'
import {alertScreenReader, putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {exitSession, setNoteRecipient, setSubjectPerEvent} from '@/stores/note-edit-session/utils'
import {getNote, updateNote} from '@/api/notes'
import {getUserProfile} from '@/api/user'
import {DateTime} from 'luxon'
import {size, trim} from 'lodash'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
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
})

const currentUser = useContextStore().currentUser
const editNoteForm = ref()
const noteStore = useNoteStore()
const rules = {
  required: value => (!!trim(value) || noteStore.model.isDraft) || 'Subject is required',
}
const showAreYouSureModal = ref(false)

const init = () => {
  getNote(props.noteId).then(note => {
    const onFinish = () => {
      noteStore.setMode('editNote')
      putFocusNextTick('edit-note-subject')
      alertScreenReader('Edit note form is open.')
    }
    noteStore.resetModel()
    noteStore.setModel(note)
    if (note.sid) {
      setNoteRecipient(note.sid).then(onFinish())
    } else {
      // A draft-note may have a null SID value.
      onFinish()
    }
  })
  useContextStore().setEventHandler('user-session-expired', noteStore.onBoaSessionExpires)
}
onBeforeMount(() => {
  useContextStore().removeEventHandler('user-session-expired', noteStore.onBoaSessionExpires)
})

const cancelRequested = () => {
  getNote(props.noteId).then(note => {
    const isPristine = trim(noteStore.model.subject) === note.subject
      && stripHtmlAndTrim(noteStore.model.body) === stripHtmlAndTrim(note.body)
    if (isPristine) {
      cancelConfirmed()
    } else {
      showAreYouSureModal.value = true
    }
  })
}

const cancelConfirmed = () => {
  props.afterCancel()
  alertScreenReader('Edit note form canceled.')
  exit(true)
}

const cancelTheCancel = () => {
  alertScreenReader('Continue editing note.')
  showAreYouSureModal.value = false
  putFocusNextTick('edit-note-subject')
}

const exit = revert => {
  exitSession(revert)
}

const onInput = event => {
  editNoteForm.value.resetValidation()
  setSubjectPerEvent(event)
}

const save = isDraft => {
  const ifAuthenticated = () => {
    async function validate() {
      const valid = await editNoteForm.value.validate()
      return valid
    }
    validate().then(({valid}) => {
      if (valid) {
        const trimmedSubject = trim(noteStore.model.subject)
        const setDate = noteStore.model.setDate ? DateTime.fromJSDate(noteStore.model.setDate).toFormat('yyyy-MM-dd') : null
        updateNote(
          noteStore.model.id,
          trim(noteStore.model.body),
          [],
          noteStore.model.contactType,
          [],
          isDraft,
          noteStore.model.isPrivate,
          setDate,
          noteStore.model.sids,
          trimmedSubject,
          [],
          noteStore.model.topics
        ).then(updatedNote => {
          props.afterSaved(updatedNote)
          alertScreenReader('Changes to note have been saved')
          exit(false)
        })
      } else {
        putFocusNextTick('edit-note-subject')
      }
    })
  }
  getUserProfile().then(data => {
    if (data.isAuthenticated) {
      ifAuthenticated()
    } else {
      noteStore.onBoaSessionExpires()
    }
  })
}

init()

</script>

<style scoped>
.edit-note-form {
  flex-basis: 100%;
}
</style>
