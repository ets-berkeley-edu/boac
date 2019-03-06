<template>
  <div>
    <div id="sr-alert-new-note" class="sr-only" aria-live="polite">{{ screenReaderAlert }}</div>
    <div>
      <b-btn
        id="new-note-button"
        class="mt-1 mr-2 btn-primary-color-override"
        variant="primary"
        :disabled="includes(['minimized', 'open'], mode)"
        @click="openNewNoteModal()">
        <span class="m-1">
          <i class="fas fa-file-alt"></i>
          New Note
        </span>
      </b-btn>
    </div>
    <div
      :class="{
        'd-none': mode === 'hidden',
        'modal-open': mode === 'open',
        'modal-open modal-minimized': mode === 'minimized',
        'modal-open modal-saving': mode === 'saving'
      }">
      <form @submit.prevent="create()">
        <div class="d-flex align-items-end pt-2 mb-1">
          <div class="flex-grow-1 new-note-header font-weight-bolder">
            New Note
          </div>
          <div class="pr-0">
            <label id="minimize-button-label" class="sr-only">Minimize the create note dialog box</label>
            <b-btn
              id="minimize-new-note-modal"
              variant="link"
              aria-labelledby="minimize-button-label"
              class="pr-2"
              @click.prevent="minimize()">
              <span class="sr-only">Minimize</span>
              <i class="fas fa-window-minimize minimize-icon text-dark"></i>
            </b-btn>
          </div>
          <div class="pr-2">
            <label id="cancel-button-label" class="sr-only">Cancel the create-note form</label>
            <b-btn
              id="cancel-new-note-modal"
              variant="link"
              aria-labelledby="cancel-button-label"
              class="pl-1 pb-1"
              @click.prevent="cancel()">
              <span class="sr-only">Cancel</span>
              <i class="fas fa-times fa-icon-size text-dark"></i>
            </b-btn>
          </div>
        </div>
        <hr class="m-0" />
        <div class="mt-2 mr-3 mb-1 ml-3">
          <div>
            <label for="create-note-subject" class="input-label mb-1"><span class="sr-only">Note </span>Subject</label>
          </div>
          <div>
            <input
              id="create-note-subject"
              v-model="subject"
              aria-labelledby="create-note-subject-label"
              class="cohort-create-input-name"
              type="text"
              maxlength="255">
          </div>
          <div>
            <label for="create-note-body" class="input-label mt-3 mb-1">Note Details</label>
          </div>
          <div id="note-details">
            <span id="create-note-body">
              <ckeditor v-model="body" :editor="editor" :config="editorConfig"></ckeditor>
            </span>
          </div>
        </div>
        <hr />
        <div class="d-flex justify-content-end mt-1 mr-3 mb-0 ml-3">
          <div>
            <b-btn
              id="create-note"
              class="btn-primary-color-override"
              aria-label="Create new note"
              variant="primary"
              @click.prevent="create()">
              Save
            </b-btn>
          </div>
        </div>
      </form>
    </div>
    <div v-if="!isMinimizing && mode === 'minimized'" class="minimized-placeholder d-flex align-items-end ml-3 mr-3">
      <div class="flex-grow-1 new-note-header">
        New Note
      </div>
      <div class="pr-0">
        <b-btn
          id="maximize-new-note-modal"
          aria-label="Bring create-note form into view"
          variant="link"
          class="pr-2"
          @click.prevent="maximize()">
          <span class="sr-only">Maximize</span>
          <i class="fas fa-window-maximize fa-icon-size text-white"></i>
        </b-btn>
      </div>
      <div class="pr-2 pt-1">
        <b-btn
          id="cancel-minimized-new-note"
          aria-label="Cancel the create-note form"
          variant="link"
          class="pl-1"
          @click.prevent="cancel()">
          <span class="sr-only">Cancel</span>
          <i class="fas fa-times fa-icon-size text-white"></i>
        </b-btn>
      </div>
    </div>
    <b-popover
      v-if="showErrorPopover"
      :show.sync="showErrorPopover"
      placement="top"
      :target="`${subject ? 'create-note-body' : 'create-note-subject'}`"
      title="">
      <span class="has-error">{{ error }}</span>
    </b-popover>
  </div>
</template>

<script>
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import Util from '@/mixins/Util';
import { createNote } from '@/api/notes';

require('@/assets/styles/ckeditor-custom.css');

export default {
  name: 'NewNoteModal',
  mixins: [Util],
  props: {
    onSuccessfulCreate: Function,
    student: Object
  },
  data: () => ({
    body: undefined,
    error: undefined,
    isMinimizing: false,
    mode: undefined,
    showErrorPopover: false,
    screenReaderAlert: undefined,
    subject: undefined,
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
    }
  }),
  watch: {
    body(str) {
      if (str) this.clearError();
    },
    subject(str) {
      if (str) this.clearError();
    }
  },
  created() {
    this.reset();
  },
  methods: {
    cancel() {
      this.reset();
      this.screenReaderAlert = "Cancelled create new note";
    },
    clearError() {
      this.error = null;
      this.showErrorPopover = false;
    },
    create() {
      this.subject = this.trim(this.subject);
      this.body = this.trim(this.body);
      if (this.subject && this.body) {
        this.mode = 'saving';
        createNote(this.student.sid, this.subject, this.body).then(data => {
          this.reset();
          this.onSuccessfulCreate(data);
          this.screenReaderAlert = "New note saved";
        });
      } else {
        if (this.subject) {
          this.error = 'Note details required';
        } else {
          this.error = this.body ? 'Subject is required' : 'Both subject and note details are required.';
        }
        this.showErrorPopover = true;
        this.screenReaderAlert = `Validation failed: ${this.error}`;
      }
    },
    maximize() {
      this.mode = 'open';
      this.screenReaderAlert = "The create-note form is visible";
      this.putFocusNextTick('create-note-subject');
    },
    minimize() {
      this.isMinimizing = true;
      this.mode = 'minimized';
      setTimeout(() => this.isMinimizing = false, 300);
      this.screenReaderAlert = "The create-note form minimized";
    },
    openNewNoteModal() {
       this.mode = 'open';
       this.putFocusNextTick('create-note-subject');
    },
    reset() {
      this.mode = 'hidden';
      this.subject = this.body = undefined;
    }
  }
}
</script>

<style scoped>
.fa-icon-size {
  font-size: 28px;
}
.input-label {
  font-weight: 600;
}
.minimize-icon {
  font-size: 24px;
}
.minimized-placeholder {
  background-color: #125074;
  border: 1px solid #aaa;
  bottom: 0;
  box-shadow: 0 0 10px #ccc;
  color: #fff;
  height: 50px;
  position: fixed;
  right: 10px;
  width: 30%;
  z-index: 2;
}
.modal-minimized {
  height: 1px !important;
  z-index: 1;
}
.modal-open {
  -webkit-transition: height 0.5s;
  background-color: #fff;
  border: 1px solid #aaa;
  bottom: 0;
  box-shadow: 0 0 10px #ccc;
  height: 480px;
  position: fixed;
  right: 30px;
  transition: height 0.5s;
  width: 30%;
}
.modal-saving {
  height: 1px !important;
}
.new-note-header {
  font-size: 24px;
  margin: 0 15px 12px 15px;
}
</style>
