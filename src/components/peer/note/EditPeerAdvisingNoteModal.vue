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
      <v-card-text>
        <PeerAdvisingAddStudent
          :exclude-these-students="[]"
          :peer-advising-department-id="1"
          :refresh="noop"
        />
        <RichTextEditor
          id="note-details"
          :initial-value="model.body || ''"
          :is-in-modal="true"
          label="Note Details"
          :on-value-update="noteStore.setBody"
          :show-advising-note-best-practices="true"
        />
        <pre>
          {{ topics }}
        </pre>
        <AdvisingNoteTopics :topics="topics" />
      </v-card-text>
      <v-card-actions class="px-6">
        <v-btn
          id="peer-advisor-note-cancel"
          aria-label="Discard note"
          text="Cancel"
          variant="outlined"
          @click="cancel"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import {computed, onMounted, ref} from 'vue'
import {noop} from 'lodash'
import {storeToRefs} from 'pinia'
import {useDisplay} from 'vuetify'
import type {NoteTopic} from '@/lib/types'
import EditPeerAdvisingNoteHeader from '@/components/peer/note/EditPeerAdvisingNoteHeader.vue'
import PeerAdvisingAddStudent from '@/components/peer/PeerAdvisingAddStudent.vue'
import RichTextEditor from '@/components/util/RichTextEditor.vue'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics.vue'
import {useNoteStore} from '@/stores/note-edit-session'
import {getPeerAdvisingDepartmentTopics} from '@/api/peer-advising-notes'

const props = defineProps({
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  }
})

const display = useDisplay()
const noteStore = useNoteStore()
const topics = ref<NoteTopic[]>([])
const {model} = storeToRefs(noteStore)

const createNoteDialog = computed({
  get: () => noteStore.isCreateNoteModalOpen,
  set: (value: boolean) => {
    noteStore.exitSession()
    if (value) {
      noteStore.setMode('peerAdvisor')
      noteStore.setIsEditedNoteModalOpen(value)
    }
  }
})

onMounted(() => {
  getPeerAdvisingDepartmentTopics(props.peerAdvisingDepartmentId).then(data => {
    topics.value = data
  })
})

const cancel = () => {
  noteStore.setIsCreateNoteModalOpen(false)
}
</script>
