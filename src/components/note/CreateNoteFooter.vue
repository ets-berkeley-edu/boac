<template>
  <div class="pt-1 px-3 pb-0">
    <div
      v-if="boaSessionExpired"
      id="uh-oh-session-time-out"
      aria-live="polite"
      class="pl-3 pr-3"
      role="alert"
    >
      <SessionExpired />
    </div>
    <div v-if="!boaSessionExpired" class="d-flex flex-wrap">
      <div class="flex-grow-1">
        <v-btn
          v-if="!['editTemplate'].includes(mode)"
          id="btn-save-as-template"
          color="primary"
          :disabled="isSaving || !trim(model.subject) || !!model.setDate || !!model.contactType"
          variant="text"
          @click="saveAsTemplate"
        >
          Save as template
        </v-btn>
      </div>
      <div class="d-flex justify-end">
        <ProgressButton
          v-if="mode === 'editTemplate'"
          id="btn-update-template"
          :action="updateTemplate"
          :disabled="isSaving || !model.subject"
          :in-progress="isSaving"
          text="Update Template"
        />
        <v-btn
          v-if="model.isDraft"
          id="save-as-draft-button"
          class="mx-1"
          color="primary"
          :disabled="isSaving || (!trim(model.subject) && !trim(model.body))"
          text="Save and Close Draft"
          variant="text"
          @click.prevent="updateNote"
        />
        <ProgressButton
          v-if="!['editTemplate'].includes(mode)"
          id="create-note-button"
          :action="publish"
          :disabled="isSaving || isEmpty(completeSidSet) || !trim(model.subject)"
          :in-progress="isSaving"
          text="Publish Note"
        />
        <v-btn
          v-if="mode !== 'editDraft'"
          id="create-note-cancel"
          class="ml-1"
          color="error"
          :disabled="isSaving"
          text="Discard"
          variant="outlined"
          @click="cancel"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton.vue'
import SessionExpired from '@/components/note/SessionExpired'
import {isEmpty, trim} from 'lodash'
import {storeToRefs} from 'pinia'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  cancel: {
    required: true,
    type: Function
  },
  saveAsTemplate: {
    required: true,
    type: Function
  },
  updateNote: {
    required: true,
    type: Function
  },
  updateTemplate: {
    required: true,
    type: Function
  }
})

const noteStore = useNoteStore()
const {boaSessionExpired, completeSidSet, isSaving, mode, model} = storeToRefs(noteStore)

const publish = () => {
  noteStore.setIsDraft(false)
  props.updateNote()
}
</script>
