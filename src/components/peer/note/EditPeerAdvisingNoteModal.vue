<template>
  <v-dialog
    v-model="dialog"
    persistent
    scrollable
  >
    <v-card
      class="modal-content pb-2"
      :class="{'modal-fullscreen': display.mdAndDown}"
      max-width="50%"
    >
      <v-card-title id="edit-note-header">
        <EditPeerAdvisingNoteHeader
          :header-text="student ? `${student.firstName} ${student.lastName}` : 'New Note'"
          :note-templates="noteTemplates"
          @template-selected="setTemplate"
        />
      </v-card-title>
      <v-card-text class="pt-0">
        <div v-if="!student">
          <PeerAdvisingNoteStudentLookup />
        </div>
        <div class="compact-student-course-schedule">
          <CompactStudentCourseSchedule
            v-if="get(student, 'sid')"
            :sid="student.sid"
            :student="student"
          />
        </div>
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
import type {PropType} from 'vue'
import {computed, onMounted, ref} from 'vue'
import {get, size} from 'lodash'
import {storeToRefs} from 'pinia'
import {useDisplay} from 'vuetify'
import type {BasicStudent, NoteRecipients, NoteTopic} from '@/lib/types'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics.vue'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import CompactStudentCourseSchedule from '@/components/peer/note/CompactStudentCourseSchedule.vue'
import ContactMethod from '@/components/note/ContactMethod.vue'
import CreateNoteFooter from '@/components/note/CreateNoteFooter.vue'
import EditPeerAdvisingNoteHeader from '@/components/peer/note/EditPeerAdvisingNoteHeader.vue'
import PeerAdvisingNoteStudentLookup from '@/components/peer/note/PeerAdvisingNoteStudentLookup.vue'
import RichTextEditor from '@/components/util/RichTextEditor.vue'
import {alertScreenReader, stripHtmlAndTrim} from '@/lib/utils'
import {getPeerAdvisingTopics} from '@/api/peer-advising-notes'
import {useNoteStore} from '@/stores/note-edit-session'
import {getNoteTemplatesForPeerAdvising} from '@/api/note-templates'

const dialog = defineModel<boolean>({
  required: true,
  type: Boolean
})

const props = defineProps({
  student: {
    default: undefined,
    required: false,
    type: Object as PropType<BasicStudent>
  },
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  },
})

const display = useDisplay()
const isAreYouSureModalOpen = ref(false)
const noteStore = useNoteStore()
const recipients = computed<NoteRecipients>(() => noteStore.recipients)
const topics = ref<NoteTopic[]>([])
const noteTemplates = ref([])
const {isSaving, model} = storeToRefs(noteStore)

onMounted(() => {
  getPeerAdvisingTopics().then(data => {
    topics.value = data
  })
  getNoteTemplatesForPeerAdvising(props.peerAdvisingDepartmentId).then(data => {
    noteTemplates.value = data
  })
})

const setTemplate = (template) => {
  model.value.body = template.body
  model.value.topics = template.topics
  model.value.noteTemplateId = template.id
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
</script>

<style>
#peer-advising-note-body .ck-editor__editable_inline {
  min-height: 100px;
}
.compact-student-course-schedule {
  margin-left: -8px !important;
}
</style>
