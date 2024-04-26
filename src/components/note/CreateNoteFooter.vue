<template>
  <div class="pt-1 px-3 pb-0">
    <div
      v-if="useNoteStore().boaSessionExpired"
      id="uh-oh-session-time-out"
      aria-live="polite"
      class="pl-3 pr-3"
      role="alert"
    >
      <SessionExpired />
    </div>
    <div v-if="!useNoteStore().boaSessionExpired" class="d-flex flex-wrap">
      <div class="flex-grow-1">
        <v-btn
          v-if="!['editTemplate'].includes(useNoteStore().mode)"
          id="btn-save-as-template"
          color="primary"
          :disabled="useNoteStore().isSaving || !trim(useNoteStore().model.subject) || !!useNoteStore().model.setDate || !!useNoteStore().model.contactType"
          variant="text"
          @click="saveAsTemplate"
        >
          Save as template
        </v-btn>
      </div>
      <div class="d-flex justify-end">
        <ProgressButton
          v-if="useNoteStore().mode === 'editTemplate'"
          id="btn-update-template"
          :action="updateTemplate"
          :disabled="useNoteStore().isSaving || !useNoteStore().model.subject"
          :in-progress="useNoteStore().isSaving"
          text="Update Template"
        />
        <v-btn
          v-if="useNoteStore().model.isDraft"
          id="save-as-draft-button"
          class="mx-1"
          color="primary"
          :disabled="useNoteStore().isSaving || (!trim(useNoteStore().model.subject) && !trim(useNoteStore().model.body))"
          text="Save and Close Draft"
          variant="text"
          @click.prevent="updateNote"
        />
        <ProgressButton
          v-if="!['editTemplate'].includes(useNoteStore().mode)"
          id="create-note-button"
          :action="publish"
          :disabled="useNoteStore().isSaving || isEmpty(useNoteStore().completeSidSet) || !trim(useNoteStore().model.subject)"
          :in-progress="useNoteStore().isSaving"
          text="Publish Note"
        />
        <v-btn
          v-if="useNoteStore().mode !== 'editDraft'"
          id="create-note-cancel"
          class="ml-1"
          color="error"
          :disabled="useNoteStore().isSaving"
          text="Discard"
          variant="outlined"
          @click.prevent="cancel"
        />
      </div>
    </div>
  </div>
</template>

<script>
import ProgressButton from '@/components/util/ProgressButton.vue'
import SessionExpired from '@/components/note/SessionExpired'
import {isEmpty, trim} from 'lodash'
import {useNoteStore} from '@/stores/note-edit-session'

export default {
  name: 'CreateNoteFooter',
  components: {ProgressButton, SessionExpired},
  props: {
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
  },
  methods: {
    publish() {
      useNoteStore().setIsDraft(false)
      this.updateNote()
    },
    isEmpty,
    trim,
    useNoteStore
  }
}
</script>
