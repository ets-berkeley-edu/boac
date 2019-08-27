<template>
  <div class="d-flex mt-1 mr-3 mb-0 ml-3">
    <div v-if="undocked && mode !== 'editTemplate'" class="flex-grow-1">
      <b-btn
        id="btn-to-save-note-as-template"
        variant="link"
        :disabled="!trim(model.subject)"
        @click.prevent="saveAsTemplate()">
        Save note as template
      </b-btn>
    </div>
    <div class="flex-grow-1">
      <b-btn
        v-if="!undocked"
        id="btn-to-advanced-note-options"
        variant="link"
        @click.prevent="setMode('advanced')">
        Advanced note options
      </b-btn>
    </div>
    <div v-if="mode === 'editTemplate'">
      <b-btn
        id="update-template-button"
        class="btn-primary-color-override"
        :disabled="!model.subject"
        aria-label="Update note template"
        variant="primary"
        @click.prevent="updateTemplate()">
        Update Template
      </b-btn>
    </div>
    <div v-if="mode !== 'editTemplate'">
      <b-btn
        id="create-note-button"
        class="btn-primary-color-override"
        :disabled="!targetStudentCount || !trim(model.subject)"
        aria-label="Create new note"
        variant="primary"
        @click.prevent="createNote()">
        Save
      </b-btn>
    </div>
    <div>
      <b-btn
        id="create-note-cancel"
        variant="link"
        :class="{'sr-only': !undocked}"
        @click.prevent="cancel()">
        Cancel
      </b-btn>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import NoteEditSession from '@/mixins/NoteEditSession';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'NewNoteModalButtons',
  mixins: [Context, NoteEditSession, UserMetadata, Util],
  props: {
    cancel: {
      required: true,
      type: Function
    },
    createNote: {
      required: true,
      type: Function
    },
    deleteTemplate: {
      required: true,
      type: Function
    },
    minimize: {
      required: true,
      type: Function
    },
    saveAsTemplate: {
      required: true,
      type: Function
    },
    updateTemplate: {
      required: true,
      type: Function
    },
    undocked: {
      required: true,
      type: Boolean
    }
  }
}
</script>
