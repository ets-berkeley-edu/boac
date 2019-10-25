<template>
  <div class="d-flex flex-wrap-reverse mt-1 mr-3 mb-0 ml-3">
    <div>
      <b-btn
        id="btn-save-as-template"
        v-if="undocked && mode !== 'editTemplate'"
        :disabled="isSaving || !trim(model.subject)"
        @click="saveAsTemplate()"
        variant="link">
        Save as template
      </b-btn>
    </div>
    <div class="flex-grow-1">
      <b-btn
        id="btn-to-advanced-note-options"
        v-if="!undocked"
        @click.prevent="enterAdvancedMode()"
        variant="link">
        Advanced note options
      </b-btn>
    </div>
    <div v-if="mode === 'editTemplate'">
      <b-btn
        id="btn-update-template"
        :disabled="isSaving || !model.subject"
        @click.prevent="updateTemplate()"
        class="btn-primary-color-override"
        aria-label="Update note template"
        variant="primary">
        Update Template
      </b-btn>
    </div>
    <div v-if="mode !== 'editTemplate'">
      <b-btn
        id="create-note-button"
        :disabled="isSaving || !targetStudentCount || !trim(model.subject)"
        @click.prevent="createNote()"
        class="btn-primary-color-override"
        aria-label="Create note"
        variant="primary">
        Save
      </b-btn>
    </div>
    <div>
      <b-btn
        id="create-note-cancel"
        :disabled="isSaving"
        :class="{'sr-only': !undocked}"
        @click.prevent="cancel()"
        variant="link">
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
