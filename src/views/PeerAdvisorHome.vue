<template>
  <div class="default-margins">
    <v-container fluid>
      <v-row>
        <v-col>
          Peer Advising Notes
        </v-col>
        <v-col>
          <v-btn
            id="batch-note-button"
            class="w-100"
            color="primary"
            :disabled="!!noteStore.mode"
            variant="flat"
            @click="() => noteStore.setIsCreateNoteModalOpen(true)"
          >
            <v-icon class="mr-1" :icon="mdiFileDocument" />
            New Note
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
    <EditBatchNoteModal
      v-model="noteStore.isCreateNoteModalOpen"
      initial-mode="createBatch"
      :on-close="() => {
        noteStore.setMode(null)
        noteStore.setIsCreateNoteModalOpen(false)
        putFocusNextTick('batch-note-button')
      }"
      :toggle-show="show => noteStore.setIsCreateNoteModalOpen(show)"
    />
  </div>
</template>

<script setup lang="ts">
import {mdiFileDocument} from '@mdi/js'
import {onMounted} from 'vue'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'
import {putFocusNextTick} from '@/lib/utils'
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal.vue'

const contextStore = useContextStore()
const noteStore = useNoteStore()

contextStore.loadingStart()

onMounted(() => {

  contextStore.loadingComplete()
})
</script>
