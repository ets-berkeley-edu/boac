<template>
  <v-card-title id="edit-note-header" class="d-flex pb-0">
    <div class="flex-grow-1">
      <div class="align-center d-flex flex-wrap">
        <ModalHeader header-id="dialog-header-note">
          <span :aria-hidden="'createBatch' === noteStore.mode">{{ HEADER_TEXT_LOOKUP[noteStore.mode] }}</span>
          <span v-if="'createBatch' === noteStore.mode" class="sr-only">Create Notes</span>
        </ModalHeader>
        <div aria-live="polite" class="auto-save-alert d-flex mx-auto">
          <v-fade-transition>
            <div
              v-if="noteStore.isAutoSavingDraftNote && !suppressAutoSaveDraftNoteAlert"
              :aria-hidden="isAutoSaveAlertPaused"
              class="d-flex align-center text-success font-size-14 font-weight-bold"
            >
              <v-progress-circular
                class="mr-2"
                indeterminate
                size="16"
                width="2"
              />
              SAVING DRAFT
            </div>
          </v-fade-transition>
          <v-btn
            class="sr-only"
            :text="isAutoSaveAlertPaused ? 'Resume Auto-Save Notifications' : 'Pause Auto-Save Notifications'"
            @click="() => isAutoSaveAlertPaused = !isAutoSaveAlertPaused"
          />
        </div>
      </div>
    </div>
    <SelectNoteTemplateForNote :exit="exit" />
  </v-card-title>
</template>

<script setup lang="ts">
import {ref, watch} from 'vue'
import ModalHeader from '@/components/util/ModalHeader.vue'
import SelectNoteTemplateForNote from '@/components/note/template/SelectNoteTemplateForNote.vue'
import {useNoteStore} from '@/stores/note-edit-session'

defineProps({
  exit: {
    type: Function,
    required: true
  }
})

const HEADER_TEXT_LOOKUP = {
  createBatch: 'Create Note(s)',
  createNote: 'Create Note',
  editDraft: 'Edit Draft Note',
  editNote: 'Edit Note',
  editTemplate: 'Edit Note Template'
}

const isAutoSaveAlertPaused = ref(false)
const noteStore = useNoteStore()
const suppressAutoSaveDraftNoteAlert = ref(false)

watch(() => noteStore.isAutoSavingDraftNote, value => {
  if (value) {
    setTimeout(() => suppressAutoSaveDraftNoteAlert.value = !suppressAutoSaveDraftNoteAlert.value, 5000)
  }
})

</script>

<style scoped>
.auto-save-alert {
  min-height: 36px;
  min-width: 150px;
}
</style>
