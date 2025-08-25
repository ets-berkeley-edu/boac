<template>
  <v-dialog
    v-model="dialog"
    class="peer-advising-note-modal"
    aria-labelledby="peer-advising-note-modal-header"
    persistent
  >
    <v-card
      class="modal-content overflow-y-hidden pb-2"
      :class="{'modal-fullscreen': mdAndDown}"
      width="720"
    >
      <FocusLock :disabled="noteStore.isFocusLockDisabled" @keydown.esc="closeModal">
        <v-card-title>
          <EditPeerAdvisingNoteHeader
            header-text="New Note"
            :note-templates="noteTemplates"
            :is-note-templates-loading="isNoteTemplatesLoading"
            @template-selected="setTemplate"
          />
        </v-card-title>
        <v-card-text class="peer-advising-note-modal-content pb-6 pt-0 px-6">
          <PeerAdvisingNoteStudentLookup
            :on-clear-selected-student="onClearSelectedStudent"
            :on-select-student="onSelectStudent"
          />
          <v-expand-transition>
            <CompactStudentCourseSchedule v-if="student" class="pb-1 pt-2" :student="student" />
          </v-expand-transition>
          <RichTextEditor
            id="peer-advising-note-body"
            class="mt-3"
            :disabled="isSaving"
            :initial-value="model.body || ''"
            label="Note Details"
            :on-value-update="noteStore.setBody"
            :show-advising-note-best-practices="true"
          />
          <AdvisingNoteTopics
            v-if="topics.length"
            class="mt-3"
            :disabled="isSaving"
            :topics="topics"
          />
          <ContactMethod
            class="mt-3"
            :disabled="isSaving"
            :is-peer-advising="true"
          />
          <AdvisingNoteAttachments
            :add="addNoteAttachments"
            :attachments="noteStore.model.attachments"
            class="pt-5"
            :disabled="!!(noteStore.isSaving || noteStore.boaSessionExpired)"
            :note="noteStore.model"
            :remove="removeAttachmentByIndex"
          />
        </v-card-text>
        <v-card-actions class="justify-end py-0">
          <CreateNoteFooter
            :discard="discardRequested"
            discard-button-label="Cancel"
            :exit="() => closeModal('Closing modal')"
            publish-button-label="Save"
          />
          <AreYouSureModal
            v-if="isAreYouSureModalOpen"
            v-model="isAreYouSureModalOpen"
            :function-cancel="() => isAreYouSureModalOpen = false"
            :function-confirm="() => closeModal('Confirmed')"
            modal-header="Discard unsaved note?"
            text="Are you sure you want to discard unsaved changes?"
          />
        </v-card-actions>
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import {computed, onMounted, ref, watch} from 'vue'
import {concat, get, size} from 'lodash'
import {storeToRefs} from 'pinia'
import {useDisplay} from 'vuetify'
import FocusLock from 'vue-focus-lock'
import type {BasicStudent, BasicStudentLabeled, NoteAttachment, NoteRecipients, NoteTemplate, NoteTopic} from '@/lib/types'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments.vue'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics.vue'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import CompactStudentCourseSchedule from '@/components/peer/note/CompactStudentCourseSchedule.vue'
import ContactMethod from '@/components/note/ContactMethod.vue'
import CreateNoteFooter from '@/components/note/CreateNoteFooter.vue'
import EditPeerAdvisingNoteHeader from '@/components/peer/note/EditPeerAdvisingNoteHeader.vue'
import PeerAdvisingNoteStudentLookup from '@/components/peer/note/PeerAdvisingNoteStudentLookup.vue'
import RichTextEditor from '@/components/util/RichTextEditor.vue'
import {alertScreenReader, pluralize, putFocusNextTick, stripHtmlAndTrim, toggleModalBackgroundDisabled} from '@/lib/utils'
import {clearNoteRecipients, setNoteRecipient} from '@/stores/note-edit-session/note-edit-session-utils'
import {getBasicStudent} from '@/api/peer-advising-users'
import {getPeerAdvisingTopics} from '@/api/peer-advising-notes'
import {getNoteTemplatesForPeerAdvising} from '@/api/note-templates'
import {removeAttachment} from '@/api/notes'
import {useNoteStore} from '@/stores/note-edit-session'

const dialog = defineModel<boolean>({
  required: true,
  type: Boolean
})

const props = defineProps({
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  }
})

const isAreYouSureModalOpen = ref(false)
const noteStore = useNoteStore()
const noteTemplates = ref<NoteTemplate[]>([])
const isNoteTemplatesLoading = ref(false)
const recipients = computed<NoteRecipients>(() => noteStore.recipients)
const student = ref<BasicStudent | undefined>()
const studentName = computed(() => `${get(student.value, 'firstName')} ${get(student.value, 'lastName')}`)
const topics = ref<NoteTopic[]>([])
const {isSaving, model} = storeToRefs(noteStore)
const {mdAndDown} = useDisplay()

onMounted(() => {
  getPeerAdvisingTopics().then(data => {
    topics.value = data
  })
  isNoteTemplatesLoading.value = true
  getNoteTemplatesForPeerAdvising(props.peerAdvisingDepartmentId).then(data => {
    noteTemplates.value = data
    isNoteTemplatesLoading.value = false
  })
})

watch(dialog, isOpen => {
  toggleModalBackgroundDisabled(isOpen)
  putFocusNextTick(isOpen ? 'peer-advising-note-templates-button' : 'peer-advisor-create-note-button')
})

const addNoteAttachments = (attachments: NoteAttachment[]) => {
  return new Promise<void>(resolve => {
    const pluralized = pluralize('attachment', attachments.length)
    noteStore.setAttachments(concat(model.value.attachments, attachments))
    alertScreenReader(`Added ${pluralized}`, false, 'assertive')
    resolve()
  })
}

const closeModal = (srText?: string) => {
  isAreYouSureModalOpen.value = false
  if (srText) {
    alertScreenReader(srText)
  }
  dialog.value = false
  isAreYouSureModalOpen.value = false
  student.value = undefined
  noteStore.setIsCreateNoteModalOpen(false)
  noteStore.exitSession()
}

const discardRequested = () => {
  const body = stripHtmlAndTrim(model.value.body)
  const unsavedChanges = !model.value.id && !!(body || size(model.value.topics) || size(recipients.value.sids))
  if (unsavedChanges) {
    isAreYouSureModalOpen.value = true
  } else {
    closeModal('Canceled')
  }
}

const onClearSelectedStudent = () => {
  if (student.value) {
    alertScreenReader(`Removed ${studentName.value}`)
    student.value = undefined
  }
  clearNoteRecipients()
}

const onSelectStudent = (selectedStudent: BasicStudentLabeled | undefined) => {
  const sid = get(selectedStudent, 'sid')
  if (sid) {
    getBasicStudent(sid).then(data => {
      student.value = data
      setNoteRecipient(sid)
      alertScreenReader(`${studentName.value} selected`)
      putFocusNextTick('show-hide-student-enrollments')
    })
  } else {
    onClearSelectedStudent()
  }
}

const removeAttachmentByIndex = (index: number) => {
  const attachment = noteStore.model.attachments[index]
  if (attachment) {
    if (attachment.id) {
      removeAttachment(model.value, attachment.id).then(() => {
        alertScreenReader(`Removed attachment '${attachment.displayName}'`)
      })
    }
    noteStore.removeAttachmentByIndex(index)
  }
}

const setTemplate = (template: NoteTemplate) => {
  model.value.body = template.body
  model.value.topics = template.topics
  model.value.noteTemplateId = template.id
}
</script>

<style>
#peer-advising-note-body .ck-editor__editable_inline {
  min-height: 100px;
}
.peer-advising-note-modal {
  --v-overlay-opacity: 0.9;
}
.peer-advising-note-modal-content {
  height: calc(100vh - 205px);
  max-height: fit-content;
  overflow-y: auto;
}
</style>
