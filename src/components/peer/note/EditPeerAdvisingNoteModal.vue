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
        Mode: {{ mode }}
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
import {computed} from 'vue'
import {storeToRefs} from 'pinia'
import {useDisplay} from 'vuetify'
import {useNoteStore} from '@/stores/note-edit-session'
import EditPeerAdvisingNoteHeader from '@/components/peer/note/EditPeerAdvisingNoteHeader.vue'

const display = useDisplay()
const noteStore = useNoteStore()
const {mode} = storeToRefs(noteStore)

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

const cancel = () => {
  noteStore.setIsCreateNoteModalOpen(false)
}
</script>

<style scoped>

</style>
