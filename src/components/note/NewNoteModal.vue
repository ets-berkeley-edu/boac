<template>
  <div>
    <div>
      <b-btn
        id="new-note-button"
        class="mt-1 mr-2 btn-primary-color-override"
        variant="primary"
        :disabled="disable || includes(['minimized', 'open'], newNoteMode)"
        @click="openNewNoteModal()">
        <span class="m-1">
          <i class="fas fa-file-alt"></i>
          New Note
        </span>
      </b-btn>
    </div>
    <FocusLock
      :disabled="newNoteMode !== 'fullScreen' || showAreYouSureModal"
      :class="{'modal-full-screen': newNoteMode === 'fullScreen'}">
      <div
        id="new-note-modal-container"
        :class="{
          'd-none': isNil(newNoteMode),
          'modal-open': newNoteMode === 'open',
          'modal-open modal-minimized': newNoteMode === 'minimized',
          'modal-open modal-saving': newNoteMode === 'saving',
          'modal-full-screen-content': newNoteMode === 'fullScreen'
        }">
        <form @submit.prevent="create()">
          <div class="d-flex align-items-end pt-2 mb-1" :class="{'mt-2': newNoteMode === 'fullScreen'}">
            <div class="flex-grow-1 new-note-header font-weight-bolder">
              New Note
            </div>
            <div v-if="newNoteMode !== 'fullScreen'" class="pr-0">
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
            <div v-if="newNoteMode !== 'fullScreen'" class="pr-2">
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
                maxlength="255"
                @keydown.esc="cancel()">
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
          <div v-if="newNoteMode === 'fullScreen'" class="mt-2 mr-3 mb-1 ml-3 w-75">
            <div>
              <label for="choose-file-for-note-attachment" class="input-label mb-1"><span class="sr-only">Note </span>Attachments</label>
            </div>
            <div v-if="size(attachments) <= maxAttachmentsPerNote">
              <b-form-file
                id="choose-file-for-note-attachment"
                v-model="attachment"
                :disabled="size(attachments) === maxAttachmentsPerNote"
                :state="Boolean(attachment)"
                placeholder="Choose file"
                drop-placeholder="Drop file here..."
              ></b-form-file>
            </div>
            <div v-if="size(attachments) === maxAttachmentsPerNote" class="m-2">
              <i class="fa fa-exclamation-triangle text-danger pr-1"></i>
              <span aria-live="polite" role="alert">A note can have no more than {{ maxAttachmentsPerNote }} attachments.</span>
            </div>
            <div>
              <ul class="pill-list pl-0">
                <li
                  v-for="(attachment, index) in attachments"
                  :id="`new-note-attachment-${index}`"
                  :key="attachment.name"
                  :class="{'mt-2': index === 0}">
                  <span class="pill text-nowrap">
                    <i class="fas fa-paperclip pr-1 pl-1"></i> {{ attachment.name }}
                    <b-btn
                      :id="`remove-note-attachment-${index}`"
                      variant="link"
                      class="pr-0 pt-1 pl-0"
                      @click.prevent="removeAttachment(index)">
                      <i class="fas fa-times-circle has-error pl-2"></i>
                    </b-btn>
                  </span>
                </li>
              </ul>
            </div>
          </div>
          <hr />
          <div class="d-flex mt-1 mr-3 mb-0 ml-3">
            <div class="flex-grow-1">
              <b-btn
                v-if="newNoteMode !== 'fullScreen'"
                id="btn-to-advanced-note-options"
                variant="link"
                @click.prevent="setNewNoteMode('fullScreen')">
                Advanced note options
              </b-btn>
            </div>
            <div>
              <b-btn
                id="create-note-button"
                class="btn-primary-color-override"
                aria-label="Create new note"
                variant="primary"
                @click.prevent="create()">
                Save
              </b-btn>
            </div>
            <div>
              <b-btn
                id="create-note-cancel"
                variant="link"
                :class="{'sr-only': newNoteMode !== 'fullScreen'}"
                @click.prevent="cancel()">
                Cancel
              </b-btn>
            </div>
          </div>
        </form>
      </div>
    </FocusLock>
    <div v-if="!isMinimizing && newNoteMode === 'minimized'" class="minimized-placeholder d-flex align-items-end ml-3 mr-3">
      <div class="flex-grow-1 new-note-header">
        New Note
      </div>
      <div class="pr-0">
        <b-btn
          id="maximize-new-note-modal"
          aria-label="Bring create-note form into view"
          variant="link"
          class="pr-2"
          @click.stop="maximize()">
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
    <AreYouSureModal
      v-if="showAreYouSureModal"
      :function-cancel="cancelTheCancel"
      :function-confirm="cancelConfirmed"
      modal-header="Discard unsaved note?"
      :show-modal="showAreYouSureModal" />
    <b-popover
      v-if="showErrorPopover"
      :show.sync="showErrorPopover"
      placement="top"
      target="create-note-subject"
      title="">
      <span class="has-error">{{ error }}</span>
    </b-popover>
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal';
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import Context from '@/mixins/Context';
import FocusLock from 'vue-focus-lock';
import NoteEditSession from "@/mixins/NoteEditSession";
import Util from '@/mixins/Util';
import { createNote } from '@/api/notes';

require('@/assets/styles/ckeditor-custom.css');

export default {
  name: 'NewNoteModal',
  components: { AreYouSureModal, FocusLock },
  mixins: [Context, NoteEditSession, Util],
  props: {
    disable: Boolean,
    onSuccessfulCreate: Function,
    student: Object
  },
  data: () => ({
    attachment: undefined,
    attachments: [],
    body: undefined,
    error: undefined,
    isMinimizing: false,
    showErrorPopover: false,
    subject: undefined,
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
    },
    showAreYouSureModal: false
  }),
  watch: {
    attachment() {
      if (this.attachment) {
        this.attachments.push(this.attachment);
        this.alertScreenReader(`Attachment '${this.attachment.name}' added`);
        this.attachment = '';
      }
    },
    body(b) {
      if (b) this.clearError();
    },
    subject(s) {
      if (s) this.clearError();
    }
  },
  created() {
    this.reset();
  },
  methods: {
    cancel() {
      if (this.trim(this.subject) || this.stripHtmlAndTrim(this.body) || this.size(this.attachments)) {
        this.showAreYouSureModal = true;
      } else {
        this.cancelConfirmed();
      }
    },
    cancelConfirmed() {
      this.showAreYouSureModal = false;
      this.reset();
      this.alertScreenReader("Cancelled create new note");
    },
    cancelTheCancel() {
      this.showAreYouSureModal = false;
      this.putFocusNextTick('create-note-subject');
    },
    clearError() {
      this.error = null;
      this.showErrorPopover = false;
    },
    create() {
      this.subject = this.trim(this.subject);
      if (this.subject) {
        this.body = this.trim(this.body);
        this.setNewNoteMode('saving');
        createNote(this.student.sid, this.subject, this.body, this.attachments).then(data => {
          this.reset();
          this.onSuccessfulCreate(data);
          this.alertScreenReader("New note saved.");
        });
      } else {
        this.error = 'Subject is required';
        this.showErrorPopover = true;
        this.alertScreenReader(`Validation failed: ${this.error}`);
        this.putFocusNextTick('create-note-subject');
      }
    },
    maximize() {
      this.setNewNoteMode('open');
      this.alertScreenReader("Create note form is visible.");
      this.putFocusNextTick('create-note-subject');
    },
    minimize() {
      this.isMinimizing = true;
      this.setNewNoteMode('minimized');
      setTimeout(() => this.isMinimizing = false, 300);
      this.alertScreenReader("Create note form minimized.");
    },
    openNewNoteModal() {
       this.setNewNoteMode('open');
       this.putFocusNextTick('create-note-subject');
    },
    removeAttachment(index) {
      this.alertScreenReader(`Attachment '${this.attachments[index].name}' removed`);
      this.attachments.splice(index, 1);
    },
    reset() {
      this.setNewNoteMode(null);
      this.subject = this.body = undefined;
      this.attachments = [];
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
.modal-full-screen {
  display: block;
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgb(0,0,0);
  background-color: rgba(0,0,0,0.4);
}
.modal-full-screen-content {
  background-color: #fff;
  margin: 140px auto auto auto;
  padding-bottom: 20px;
  border: 1px solid #888;
  width: 60%;
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
  z-index: 1;
}
.modal-saving {
  height: 1px !important;
}
.new-note-header {
  font-size: 24px;
  margin: 0 15px 12px 15px;
}
</style>
