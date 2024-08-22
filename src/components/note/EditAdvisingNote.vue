<template>
  <v-form
    ref="editNoteForm"
    class="edit-note-form"
    @submit.prevent="save"
  >
    <div v-if="noteStore.model.isDraft" class="font-size-18 text-error pa-2">
      <v-icon :icon="mdiAlert" />
      You are editing a draft note.
    </div>
    <label id="edit-note-subject-label" class="font-weight-bold" for="edit-note-subject">Subject</label>
    <v-text-field
      id="edit-note-subject"
      aria-labelledby="edit-note-subject-label"
      bg-color="white"
      class="mt-1"
      density="comfortable"
      :disabled="isSaving || boaSessionExpired"
      hide-details
      maxlength="255"
      :model-value="noteStore.model.subject"
      required
      :rules="[rules.required]"
      size="255"
      validate-on="submit"
      variant="outlined"
      @input="onInput"
      @keydown.esc="cancelRequested"
    />
    <div id="edit-note-details" class="bg-transparent mt-2">
      <RichTextEditor
        :disabled="isSaving || boaSessionExpired"
        :initial-value="noteStore.model.body || ''"
        label="Note Details"
        :on-value-update="noteStore.setBody"
        :show-advising-note-best-practices="true"
      />
    </div>
    <AdvisingNoteTopics class="mt-2" />
    <PrivacyPermissions
      v-if="currentUser.canAccessPrivateNotes"
      class="mt-2"
      :disabled="isSaving || boaSessionExpired"
    />
    <ContactMethod class="mt-3" :disabled="isSaving || boaSessionExpired" />
    <ManuallySetDate class="mt-3" :disabled="isSaving || boaSessionExpired" />
    <AdvisingNoteAttachments
      v-if="size(noteStore.model.attachments)"
      class="mt-3"
      :disabled="isSaving || boaSessionExpired"
      id-prefix="edit-note-"
      read-only
    >
      <template #label>
        <label
          id="edit-note-attachments-list-label"
          class="font-size-16 font-weight-700"
          for="edit-note-attachments-list"
        >Attachments</label>
      </template>
    </AdvisingNoteAttachments>
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
      <div class="d-flex py-4">
        <ProgressButton
          id="save-note-button"
          :action="() => save(false)"
          :disabled="!noteStore.recipients.sids.length || !trim(noteStore.model.subject) || isSaving || boaSessionExpired"
          :in-progress="isPublishingNote"
          :text="noteStore.model.isDraft ? 'Publish Note' : 'Save'"
        />
        <ProgressButton
          v-if="noteStore.model.isDraft"
          id="update-draft-note-button"
          :action="() => save(true)"
          :disabled="isSaving || boaSessionExpired"
          :in-progress="isSavingDraft"
          text="Update Draft"
          variant="text"
        />
        <v-btn
          id="cancel-edit-note-button"
          color="primary"
          :disabled="isSaving || boaSessionExpired"
          slim
          text="Cancel"
          variant="text"
          @click="cancelRequested"
        />
      </div>
    </div>
    <AreYouSureModal
      v-model="showAreYouSureModal"
      :function-cancel="cancelTheCancel"
      :function-confirm="cancelConfirmed"
      modal-header="Discard unsaved changes?"
    />
  </v-form>
</template>

<script setup>
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics'
import {alertScreenReader, putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import ContactMethod from '@/components/note/ContactMethod'
import {exitSession, setNoteRecipient, setSubjectPerEvent} from '@/stores/note-edit-session/utils'
import {getNote, updateNote} from '@/api/notes'
import {getUserProfile} from '@/api/user'
import ManuallySetDate from '@/components/note/ManuallySetDate'
import {mdiAlert} from '@mdi/js'
import {onBeforeMount, ref} from 'vue'
import PrivacyPermissions from '@/components/note/PrivacyPermissions'
import ProgressButton from '@/components/util/ProgressButton'
import RichTextEditor from '@/components/util/RichTextEditor'
import SessionExpired from '@/components/note/SessionExpired'
import {size, trim} from 'lodash'
import {storeToRefs} from 'pinia'
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
const isPublishingNote = ref(false)
const isSavingDraft = ref(false)
const noteStore = useNoteStore()
const {boaSessionExpired, isSaving} = storeToRefs(noteStore)
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
        updateNote(
          noteStore.model.id,
          trim(noteStore.model.body),
          [],
          noteStore.model.contactType,
          [],
          isDraft,
          noteStore.model.isPrivate,
          noteStore.model.setDate,
          noteStore.model.sids,
          trimmedSubject,
          [],
          noteStore.model.topics
        ).then(updatedNote => {
          props.afterSaved(updatedNote)
          isSavingDraft.value = false
          isPublishingNote.value = false
          noteStore.setIsSaving(false)
          alertScreenReader(isDraft ? 'Draft note updated' : 'Note updated')
          exit(false)
        })
      } else {
        isSavingDraft.value = false
        isPublishingNote.value = false
        noteStore.setIsSaving(false)
        putFocusNextTick('edit-note-subject')
      }
    })
  }
  isSavingDraft.value = isDraft
  isPublishingNote.value = !isDraft
  noteStore.setIsSaving(true)
  alertScreenReader(isDraft ? 'Saving draft note' : 'Publishing note')
  getUserProfile().then(data => {
    if (data.isAuthenticated) {
      ifAuthenticated()
    } else {
      noteStore.onBoaSessionExpires()
    }
  })
}

onBeforeMount(() => {
  useContextStore().removeEventHandler('user-session-expired', noteStore.onBoaSessionExpires)
})

init()

</script>

<style scoped>
.edit-note-form {
  cursor: auto !important;
  flex-basis: 100%;
}
</style>
