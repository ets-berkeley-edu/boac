<template>
  <v-dialog
    v-model="createNoteDialog"
    persistent
    scrollable
  >
    <v-card
      class="modal-content"
      :class="{'modal-fullscreen': display.mdAndDown}"
      max-width="50%"
    >
      <v-card-title id="edit-note-header">
        <EditPeerAdvisingNoteHeader />
      </v-card-title>
      <v-card-text class="pt-0">
        <PeerAdvisingNoteStudentLookup />
        <RichTextEditor
          id="peer-advising-note-details"
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
      <v-card-actions>
        <CreateNoteFooter
          :discard="discardRequested"
          discard-button-label="Cancel"
          :exit="discardRequested"
          publish-button-label="Save"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import {computed, onMounted, ref} from 'vue'
import {size, trim} from 'lodash'
import {storeToRefs} from 'pinia'
import {useDisplay} from 'vuetify'
import type {NoteRecipients, NoteTopic} from '@/lib/types'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics.vue'
import ContactMethod from '@/components/note/ContactMethod.vue'
import CreateNoteFooter from '@/components/note/CreateNoteFooter.vue'
import EditPeerAdvisingNoteHeader from '@/components/peer/note/EditPeerAdvisingNoteHeader.vue'
import PeerAdvisingNoteStudentLookup from '@/components/peer/note/PeerAdvisingNoteStudentLookup.vue'
import RichTextEditor from '@/components/util/RichTextEditor.vue'
import {alertScreenReader, stripHtmlAndTrim} from '@/lib/utils'
import {getDefaultModel} from '@/stores/note-edit-session/note-edit-session-utils'
import {getPeerAdvisingTopics} from '@/api/peer-advising-notes'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  }
})

const display = useDisplay()
const noteStore = useNoteStore()
const showDiscardNoteModal = ref(false)
const recipients = computed<NoteRecipients>(() => noteStore.recipients)
const topics = ref<NoteTopic[]>([])
const {isSaving, model} = storeToRefs(noteStore)

const createNoteDialog = computed({
  get: () => noteStore.isCreateNoteModalOpen,
  set: noteStore.setIsCreateNoteModalOpen
})

onMounted(() => {
  getPeerAdvisingTopics().then(data => {
    topics.value = data
    const note = getDefaultModel()
    // Peer Advisors do not provide note.subject thus subject is set to empty string to satisfy not-null db constraints.
    note.subject = ''
    note.peerAdvisingDepartmentId = props.peerAdvisingDepartmentId
    noteStore.setModel(note)
  })
})

const discardRequested = () => {
  const unsavedChanges = !!trim(model.value.subject)
    || !!stripHtmlAndTrim(model.value.body)
    || size(model.value.topics)
    || size(model.value.attachments)
    || size(recipients.value.sids)
  if (unsavedChanges) {
    showDiscardNoteModal.value = true
  } else {
    // Discard
    alertScreenReader('Canceled edit note')
    noteStore.exitSession()
  }
}
</script>
