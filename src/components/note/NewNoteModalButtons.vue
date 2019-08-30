<template>
  <div class="d-flex flex-wrap-reverse mt-1 mr-3 mb-0 ml-3">
    <div class="flex-grow-1">
      <b-btn
        v-if="!undocked"
        id="btn-to-advanced-note-options"
        variant="link"
        @click.prevent="setMode('advanced')">
        Advanced note options
      </b-btn>
    </div>
    <div v-if="mode === 'createTemplate'">
      <b-btn
        id="create-template-button"
        class="btn-primary-color-override"
        :disabled="!model.subject"
        aria-label="Create note template"
        variant="primary"
        @click.prevent="createTemplate()">
        Create Template
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
    <div v-if="!includes(['createTemplate', 'editTemplate'], mode)">
      <b-btn
        id="create-note-button"
        class="btn-primary-color-override"
        :disabled="!targetStudentCount || !trim(model.subject)"
        aria-label="Create note"
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
    createTemplate: {
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
