<template>
  <div class="d-flex flex-wrap-reverse mt-1 mr-3 mb-0 ml-3">
    <div>
      <b-btn
        v-if="undocked && mode !== 'editTemplate'"
        id="btn-save-as-template"
        variant="link"
        :disabled="!trim(model.subject)"
        @click="saveAsTemplate()">
        Save as template
      </b-btn>
    </div>
    <div class="flex-grow-1">
      <b-btn
        v-if="!undocked"
        id="btn-to-advanced-note-options"
        variant="link"
        @click.prevent="enterAdvancedMode()">
        Advanced note options
      </b-btn>
    </div>
    <div v-if="mode === 'editTemplate'">
      <b-btn
        id="btn-update-template"
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
  name: 'CreateNoteFooter',
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
    saveAsTemplate: {
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
  },
  methods: {
    enterAdvancedMode() {
      this.setMode('advanced');
      this.putFocusNextTick('create-note-subject');
    }
  }
}
</script>
