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
          :exit="close"
          publish-button-label="Save"
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
import CompactStudentCourseSchedule from '@/components/peer/note/CompactStudentCourseSchedule.vue'
import ContactMethod from '@/components/note/ContactMethod.vue'
import CreateNoteFooter from '@/components/note/CreateNoteFooter.vue'
import EditPeerAdvisingNoteHeader from '@/components/peer/note/EditPeerAdvisingNoteHeader.vue'
import PeerAdvisingNoteStudentLookup from '@/components/peer/note/PeerAdvisingNoteStudentLookup.vue'
import RichTextEditor from '@/components/util/RichTextEditor.vue'
import {alertScreenReader, stripHtmlAndTrim} from '@/lib/utils'
import {getPeerAdvisingTopics} from '@/api/peer-advising-notes'
import {useNoteStore} from '@/stores/note-edit-session'

const dialog = defineModel<boolean>({
  required: true,
  type: Boolean
})

defineProps({
  student: {
    default: undefined,
    required: false,
    type: Object as PropType<BasicStudent>
  }
})

const display = useDisplay()
const noteStore = useNoteStore()
const recipients = computed<NoteRecipients>(() => noteStore.recipients)
const topics = ref<NoteTopic[]>([])
const {isSaving, model} = storeToRefs(noteStore)

onMounted(() => {
  getPeerAdvisingTopics().then(data => {
    topics.value = data
  })
})

const close = () => {
  dialog.value = false
  noteStore.exitSession()
}

const discardRequested = () => {
  const body = stripHtmlAndTrim(model.value.body)
  const unsavedChanges = !model.value.id && !!(body || size(model.value.topics) || size(recipients.value.sids))
  if (unsavedChanges) {
    dialog.value = true
  } else {
    // Discard
    alertScreenReader('Canceled edit note')
    dialog.value = false
    noteStore.exitSession()
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
