<template>
  <v-card-title id="edit-note-header" class="d-flex pb-0">
    <div class="w-100">
      <div class="align-start d-flex flex-column flex-sm-row">
        <ModalHeader header-id="dialog-header-note">
          <span :aria-hidden="'createBatch' === noteStore.mode">{{ HEADER_TEXT_LOOKUP[noteStore.mode] }}</span>
          <span v-if="'createBatch' === noteStore.mode" class="sr-only">Create Notes</span>
        </ModalHeader>
        <div aria-live="polite" class="auto-save d-flex flex-wrap w-100 pb-2">
          <div class="auto-save-alert">
            <v-fade-transition>
              <div
                :aria-hidden="isAutoSaveAlertPaused"
                class="d-none align-center text-success font-size-14 font-weight-bold mx-4 my-2"
                :class="{'d-flex': noteStore.isAutoSavingDraftNote && !suppressAutoSaveDraftNoteAlert}"
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
          </div>
          <div class="d-flex align-center mx-4" :class="{'sr-only': !isPauseButtonFocused}">
            <v-btn
              id="pause-auto-save-notifications-btn"
              :aria-label="isAutoSaveAlertPaused ? 'Resume Auto-Save Notifications' : 'Pause Auto-Save Notifications'"
              height="16"
              size="small"
              slim
              :text="isAutoSaveAlertPaused ? 'Resume Notifications' : 'Pause Notifications'"
              variant="flat"
              @blur="() => isPauseButtonFocused = false"
              @click="() => isAutoSaveAlertPaused = !isAutoSaveAlertPaused"
              @focus="() => isPauseButtonFocused = true"
            />
          </div>
        </div>
      </div>
    </div>
    <SelectNoteTemplateForNote :exit="exit" />
    <v-btn
      v-if="noteStore.mode === 'editDraft'"
      id="close-btn-in-modal-header"
      aria-label="Close dialog"
      class="font-size-14 font-weight-bold ml-4 mr-1"
      color="primary"
      density="comfortable"
      elevation="0"
      icon
      title="Close"
      variant="text"
      @click="exit"
    >
      <v-icon
        color="primary"
        :icon="mdiCloseThick"
        size="16"
      />
    </v-btn>
  </v-card-title>
</template>

<script setup lang="ts">
import {ref, watch} from 'vue'
import {mdiCloseThick} from '@mdi/js'
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
const isPauseButtonFocused = ref(false)
const noteStore = useNoteStore()
const suppressAutoSaveDraftNoteAlert = ref(false)

watch(() => noteStore.isAutoSavingDraftNote, value => {
  if (value) {
    setTimeout(() => suppressAutoSaveDraftNoteAlert.value = !suppressAutoSaveDraftNoteAlert.value, 5000)
  }
})

</script>

<style scoped>
.auto-save {
  min-height: 3rem;
}
.auto-save-alert {
  min-height: 2.5rem;
  min-width: 12rem;
}
</style>
