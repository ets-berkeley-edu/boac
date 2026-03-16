<template>
  <v-form
    :id="`note-${noteId}-edit-form`"
    ref="editNoteForm"
    :class="wrapperClass"
    @submit.prevent="save"
  >
    <div v-if="model.isDraft" class="font-size-18 text-error pa-2">
      <v-icon :icon="mdiAlert" aria-hidden="true" />

      <span class="edit-draft-text">
        You are editing a draft note.
      </span>

      <div class="d-inline-flex align-center ml-2" :class="{'sr-only': !isPauseButtonFocused}">
        <v-btn
          :id="`pause-auto-save-notifications-btn-${noteId}`"
          type="button"
          :aria-pressed="isAutoSaveAlertPaused"
          :aria-label="isAutoSaveAlertPaused ? 'Resume Auto-Save Notifications' : 'Pause Auto-Save Notifications'"
          height="16"
          size="small"
          slim
          :text="isAutoSaveAlertPaused ? 'Resume Notifications' : 'Pause Notifications'"
          variant="flat"
          @blur="() => isPauseButtonFocused = false"
          @focus="() => isPauseButtonFocused = true"
          @click.prevent="() => isAutoSaveAlertPaused = !isAutoSaveAlertPaused"
        />
      </div>

      <transition name="bounce">
        <span
          v-if="showDraftSavedBadge"
          :aria-hidden="isAutoSaveAlertPaused"
          class="text-success font-size-12 font-weight-bold mb-1 ml-2"
        >
          DRAFT SAVED
        </span>
      </transition>
    </div>
    <div v-if="!isPeerAdvisor(currentUser) && !model.peerAdvisingDepartmentId" class="mt-1">
      <label id="edit-note-subject-label" class="font-weight-bold" for="edit-note-subject">Subject</label>
      <v-text-field
        id="edit-note-subject"
        aria-label="Note Subject"
        autocomplete="on"
        bg-color="white"
        class="mt-1"
        density="comfortable"
        :disabled="isSaving || boaSessionExpired || (model.peerAdvisingDepartmentId && !model.subject)"
        hide-details
        maxlength="255"
        :model-value="model.subject"
        required
        :rules="[value => (!!trim(value) || model.isDraft) || !!model.peerAdvisingDepartmentId || 'Subject is required']"
        size="255"
        validate-on="submit"
        @input="onInput"
        @keydown.esc="cancelRequested"
      />
    </div>
    <div id="edit-note-details" class="bg-transparent mt-3">
      <RichTextEditor
        id="edit-note-body"
        :disabled="isSaving || boaSessionExpired"
        :initial-value="model.body || ''"
        label="Note Details"
        :on-value-update="noteStore.setBody"
        :show-advising-note-best-practices="true"
      />
    </div>
    <AdvisingNoteTopics
      class="pt-5"
      :topics="topics"
    />
    <PrivacyPermissions
      v-if="currentUser.canAccessPrivateNotes && !model.peerAdvisingDepartmentId"
      class="pt-2"
      :disabled="isSaving || boaSessionExpired"
    />
    <ContactMethod
      class="mt-4"
      :disabled="isSaving || boaSessionExpired"
      :is-peer-advising="!!model.peerAdvisingDepartmentId"
    />
    <ManuallySetDate
      v-if="!model.peerAdvisingDepartmentId"
      class="pt-4"
      :container-id="`note-${noteId}-edit-form`"
    />
    <AdvisingNoteAttachments
      v-if="size(model.attachments)"
      :attachments="model.attachments"
      class="pt-4"
      :disabled="isSaving || boaSessionExpired"
      id-prefix="edit-note"
      :is-read-only="true"
      :note="model"
    />
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
          :aria-label="model.isDraft ? 'Publish Note' : 'Save Note'"
          :disabled="!noteStore.recipients.sids.length || isSaving || boaSessionExpired || (model.peerAdvisingDepartmentId ? (!stripHtmlAndTrim(model.body) && !model.topics.length) : !trim(model.subject))"
          :in-progress="isPublishingNote"
          :text="model.isDraft ? 'Publish Note' : 'Save'"
        />
        <ProgressButton
          v-if="model.isDraft"
          id="update-draft-note-button"
          :action="() => save(true)"
          class="ml-2"
          :disabled="isSaving || boaSessionExpired"
          :in-progress="isSavingDraft"
          text="Update Draft"
          variant="text"
        />
        <v-btn
          id="cancel-edit-note-button"
          :aria-label="`Cancel Edit ${model.isDraft ? 'Draft' : ' Note'}`"
          class="ml-2"
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
import {mdiAlert} from '@mdi/js'
import {onBeforeMount, onMounted, ref, watch} from 'vue'
import {size, trim} from 'lodash'
import {storeToRefs} from 'pinia'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import ContactMethod from '@/components/note/ContactMethod'
import ManuallySetDate from '@/components/note/ManuallySetDate'
import PrivacyPermissions from '@/components/note/PrivacyPermissions'
import ProgressButton from '@/components/util/ProgressButton'
import RichTextEditor from '@/components/util/RichTextEditor'
import SessionExpired from '@/components/note/SessionExpired'
import {alertScreenReader, putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {
  exitSession,
  isAutoSaveMode,
  scheduleAutoSaveJob,
  setNoteRecipient,
  setSubjectPerEvent
} from '@/stores/note-edit-session/note-edit-session-utils'
import {getNote, updateNote} from '@/api/notes'
import {getPeerAdvisingTopics} from '@/api/peer-advising-notes.js'
import {getTopicsForNotes} from '@/api/topics.js'
import {getUserProfile} from '@/api/user'
import {isPeerAdvisor} from '@/lib/boa-user.js'
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
  initialMode: {
    required: true,
    type: String
  },
  noteId: {
    required: true,
    type: Number
  },
  wrapperClass: {
    default: 'edit-note-form pl-2',
    required: false,
    type: String
  }
})

const contextStore = useContextStore()
const noteStore = useNoteStore()

const currentUser = contextStore.currentUser
const editNoteForm = ref()
const isPublishingNote = ref(false)
const isSavingDraft = ref(false)
const showAreYouSureModal = ref(false)
const isAutoSaveAlertPaused = ref(false)
const isPauseButtonFocused = ref(false)
const showDraftSavedBadge = ref(false)
const topics = ref([])
const {boaSessionExpired, isSaving, mode, model} = storeToRefs(noteStore)

const focusNoteField = () => {
  if (model.value.peerAdvisingDepartmentId) {
    // Peer advising notes have no subject field so this will focus the CKEditor's textarea.
    putFocusNextTick('edit-note-body', {cssSelector: '.ck-editor__editable_inline'})
  } else {
    putFocusNextTick('edit-note-subject')
  }
}

watch(isAutoSaveAlertPaused, paused => {
  alertScreenReader(paused ? 'Auto-save notifications paused.' : 'Auto-save notifications resumed.')
})

watch(
  () => noteStore.isAutoSavingDraftNote,
  (isSaving, wasSaving) => {
    // Announce AFTER autosave completes
    if (wasSaving && !isSaving && model.value.isDraft) {
      showDraftSavedBadge.value = true
      window.setTimeout(() => (showDraftSavedBadge.value = false), 5000)

      if (!isAutoSaveAlertPaused.value) {
        alertScreenReader('Draft saved.')
      }
    }
  }
)

onMounted(() => {
  const resolve = note => {
    const fetchTopics = note.peerAdvisingDepartmentId ? getPeerAdvisingTopics() : getTopicsForNotes(false)
    fetchTopics.then(data => {
      topics.value = data
      noteStore.setMode('editNote')
      focusNoteField()
      if (note.isDraft) {
        setTimeout(() => {
          alertScreenReader('You are editing a draft note.')
        }, 250)
      }
      contextStore.setEventHandler('user-session-expired', noteStore.onBoaSessionExpires)
    })
  }
  getNote(props.noteId).then(note => {
    noteStore.resetModel()
    noteStore.setModel(note)
    noteStore.setMode(props.initialMode)
    if (note.sid) {
      setNoteRecipient(note.sid).then(() => resolve(note))
    } else {
      // A draft-note may have a null SID value.
      resolve(note)
    }
    if (isAutoSaveMode(mode.value)) {
      scheduleAutoSaveJob()
    }
  })
})

onBeforeMount(() => {
  contextStore.removeEventHandler('user-session-expired')
})

const cancelRequested = () => {
  getNote(props.noteId).then(note => {
    const isPristine = trim(model.value.subject) === note.subject
      && stripHtmlAndTrim(model.value.body) === stripHtmlAndTrim(note.body)
    if (isPristine) {
      cancelConfirmed()
    } else {
      showAreYouSureModal.value = true
    }
  })
}

const cancelConfirmed = () => {
  props.afterCancel()
  alertScreenReader('Note discarded.')
  exit(true)
}

const cancelTheCancel = () => {
  alertScreenReader('Canceled. Continue editing note.')
  showAreYouSureModal.value = false
  focusNoteField()
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
        const trimmedSubject = trim(model.value.subject)
        updateNote(
          model.value.id,
          trim(model.value.body),
          [],
          model.value.contactType,
          [],
          isDraft,
          model.value.isPrivate,
          model.value.setDate,
          noteStore.recipients.sids,
          trimmedSubject,
          [],
          model.value.topics
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
        focusNoteField()
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
</script>

<style>
#edit-note-details .ck-editor__editable {
  height: 180px;
  width: 100%;
}
</style>

<style scoped>
.edit-note-form {
  cursor: auto !important;
  flex-basis: 100%;
  width: 140%;
}
.edit-draft-text {
  position: relative;
  top: 2px;
}
</style>
