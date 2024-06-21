<template>
  <div>
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
          class="pl-0"
          color="primary"
          :disabled="isSaving || !trim(model.subject) || !!model.setDate || !!model.contactType"
          text="Save as template"
          variant="text"
          @click="saveAsTemplate"
        />
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
        <ProgressButton
          v-if="model.isDraft"
          id="save-as-draft-button"
          :action="updateDraft"
          :disabled="isSaving || isUpdatingDraft || (!trim(model.subject) && !trim(model.body))"
          :in-progress="isUpdatingDraft"
          text="Save and Close Draft"
          variant="text"
        />
        <ProgressButton
          v-if="!['editTemplate'].includes(mode)"
          id="create-note-button"
          :action="publish"
          :disabled="isSaving || isEmpty(completeSidSet) || !trim(model.subject)"
          :in-progress="isPublishing"
          text="Publish Note"
        />
        <v-btn
          v-if="mode !== 'editDraft'"
          id="create-note-cancel"
          class="ml-2"
          color="error"
          :disabled="isSaving || isUpdatingDraft"
          text="Discard"
          variant="outlined"
          @click="discard"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton.vue'
import SessionExpired from '@/components/note/SessionExpired'
import {alertScreenReader, invokeIfAuthenticated} from '@/lib/utils'
import {isEmpty, size, trim} from 'lodash'
import {ref} from 'vue'
import {storeToRefs} from 'pinia'
import {updateAdvisingNote} from '@/stores/note-edit-session/utils'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  discard: {
    required: true,
    type: Function
  },
  exit: {
    required: true,
    type: Function
  },
  saveAsTemplate: {
    required: true,
    type: Function
  },
  showAlert: {
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
const isPublishing = ref(false)
const isUpdatingDraft = ref(false)

const publish = () => {
  noteStore.setIsDraft(false)
  isPublishing.value = true
  updateNote().then(() => isPublishing.value = false)
}

const updateDraft = () => {
  isUpdatingDraft.value = true
  updateNote().then(() => isUpdatingDraft.value = false)
}

const updateNote = () => {
  return new Promise(resolve => {
    noteStore.setIsSaving(true)
    const ifAuthenticated = () => {
      if (model.value.isDraft || (model.value.subject && size(completeSidSet.value))) {
        // File upload might take time; alert will be overwritten when API call is done.
        props.showAlert('Creating note...', 60)
        updateAdvisingNote().then(() => {
          noteStore.setIsSaving(false)
          alertScreenReader(mode.value.includes('create') ? 'Note created' : 'Note saved')
          props.exit(false)
          resolve()
        })
      } else {
        resolve()
      }
    }
    invokeIfAuthenticated(ifAuthenticated, () => {
      noteStore.onBoaSessionExpires()
      noteStore.setIsSaving(false)
      props.exit(true)
      resolve()
    })
  })
}
</script>
