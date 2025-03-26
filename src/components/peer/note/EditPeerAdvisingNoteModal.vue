<template>
  <v-dialog
    v-model="dialog"
    persistent
    scrollable
  >
    <v-card
      class="modal-content pb-2"
      :class="{'modal-fullscreen': mdAndDown}"
      width="720"
    >
      <v-card-title id="edit-note-header">
        <EditPeerAdvisingNoteHeader
          header-text="New Note"
          :note-templates="noteTemplates"
          :is-note-templates-loading="isNoteTemplatesLoading"
          @template-selected="setTemplate"
        />
      </v-card-title>
      <v-card-text class="pt-0">
        <v-expand-transition>
          <PeerAdvisingNoteStudentLookup
            v-if="!student"
            :on-clear-selected-student="onClearSelectedStudent"
            :on-select-student="onSelectStudent"
          />
        </v-expand-transition>
        <v-expand-transition>
          <div v-if="student" class="pb-1">
            <div class="align-start d-flex">
              <div class="d-flex flex-column pt-2">
                <h4 aria-live="polite" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="font-size-18 text-medium-emphasis">
                  {{ student.firstName }} {{ student.lastName }} <span class="sr-only">has been selected</span>
                </h4>
                <div :class="{'demo-mode-blur': currentUser.inDemoMode}" class="font-size-16 text-medium-emphasis">
                  SID: {{ student.sid }}
                </div>
              </div>
              <div>
                <v-btn
                  id="clear-student-selection"
                  aria-label="Clear the student selection"
                  color="error"
                  :icon="mdiCloseCircle"
                  title="Remove"
                  variant="text"
                  @click="() => onSelectStudent(undefined)"
                />
              </div>
            </div>
            <div class="compact-student-course-schedule">
              <CompactStudentCourseSchedule :student="student" />
            </div>
          </div>
        </v-expand-transition>
        <RichTextEditor
          id="peer-advising-note-body"
          class="mt-3"
          :disabled="isSaving"
          :initial-value="model.body || ''"
          :is-in-modal="true"
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
      <v-card-actions class="py-0">
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
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import {computed, onMounted, ref} from 'vue'
import {concat, get, size} from 'lodash'
import {mdiCloseCircle} from '@mdi/js'
import {storeToRefs} from 'pinia'
import {useDisplay} from 'vuetify'
import type {BasicStudent, NoteAttachment, NoteRecipients, NoteTemplate, NoteTopic} from '@/lib/types'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments.vue'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics.vue'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import CompactStudentCourseSchedule from '@/components/peer/note/CompactStudentCourseSchedule.vue'
import ContactMethod from '@/components/note/ContactMethod.vue'
import CreateNoteFooter from '@/components/note/CreateNoteFooter.vue'
import EditPeerAdvisingNoteHeader from '@/components/peer/note/EditPeerAdvisingNoteHeader.vue'
import PeerAdvisingNoteStudentLookup from '@/components/peer/note/PeerAdvisingNoteStudentLookup.vue'
import RichTextEditor from '@/components/util/RichTextEditor.vue'
import {alertScreenReader, pluralize, stripHtmlAndTrim} from '@/lib/utils'
import {clearNoteRecipients, setNoteRecipient} from '@/stores/note-edit-session/note-edit-session-utils'
import {getPeerAdvisingTopics} from '@/api/peer-advising-notes'
import {getNoteTemplatesForPeerAdvising} from '@/api/note-templates'
import {removeAttachment} from '@/api/notes'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const dialog = defineModel<boolean>({
  required: true,
  type: Boolean
})

const props = defineProps({
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  },
})

const currentUser = useContextStore().currentUser
const isAreYouSureModalOpen = ref(false)
const noteStore = useNoteStore()
const noteTemplates = ref([])
const isNoteTemplatesLoading = ref(false)
const recipients = computed<NoteRecipients>(() => noteStore.recipients)
const student = ref<BasicStudent | undefined>()
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

const addNoteAttachments = (attachments: NoteAttachment[]) => {
  return new Promise<void>(resolve => {
    const pluralized = pluralize('attachment', attachments.length)
    noteStore.setAttachments(concat(model.value.attachments, attachments))
    alertScreenReader(`${pluralized} added`, false, 'assertive')
    resolve()
  })
}

const closeModal = (srText?: string) => {
  if (srText) {
    alertScreenReader(srText)
  }
  dialog.value = false
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
  student.value = undefined
  clearNoteRecipients()
  alertScreenReader('Student selection removed')
}

const onSelectStudent = (selectedStudent: BasicStudent | undefined) => {
  const sid = get(selectedStudent, 'sid')
  if (sid) {
    student.value = selectedStudent
    setNoteRecipient(sid)
    alertScreenReader(`${get(student.value, 'firstName')} ${get(student.value, 'lastName')} selected`)
  } else {
    onClearSelectedStudent()
  }
}

const removeAttachmentByIndex = (index: number) => {
  const attachment = noteStore.model.attachments[index]
  if (attachment) {
    if (attachment.id) {
      removeAttachment(model.value.id, attachment.id).then(() => {
        alertScreenReader(`Attachment '${attachment.displayName}' removed`)
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
.compact-student-course-schedule {
  margin: 8px 0 0 -8px;
}
</style>
