<template>
  <form class="edit-note-form" @submit.prevent="save()">
    <div>
      <label id="edit-note-subject-label" class="font-weight-bold" for="edit-note-subject">Subject</label>
    </div>
    <div>
      <input
        id="edit-note-subject"
        v-model="subject"
        aria-labelledby="edit-note-subject-label"
        class="cohort-create-input-name"
        type="text"
        maxlength="255"
        @keydown.esc="cancel()">
    </div>
    <div>
      <label class="font-weight-bold mt-2" for="edit-note-details">
        Note Details
      </label>
    </div>
    <div>
      <span id="edit-note-details" class="bg-transparent note-details-editor">
        <ckeditor
          v-model="body"
          :editor="editor"
          :config="editorConfig"></ckeditor>
      </span>
    </div>
    <div class="mt-2 mr-3 mb-2 w-75">
      <div>
        <label for="choose-note-attachment" class="font-weight-bold input-label mb-1"><span class="sr-only">File </span>Attachments</label>
      </div>
      <div v-if="size(note.attachments) <= maxAttachmentsPerNote">
        <b-form-file
          id="choose-note-attachment"
          v-model="attachment"
          :disabled="size(note.attachments) === maxAttachmentsPerNote"
          :state="Boolean(attachment)"
          placeholder="Choose file"
          drop-placeholder="Drop file here..."
        ></b-form-file>
      </div>
      <div v-if="size(note.attachments) === maxAttachmentsPerNote" class="m-2">
        <i class="fa fa-exclamation-triangle text-danger pr-1"></i>
        A note can have no more than {{ maxAttachmentsPerNote }} attachments.
      </div>
      <div>
        <ul class="pill-list pl-0">
          <li
            v-for="(attachment, index) in note.attachments"
            :id="`edit-note-attachment-${index}`"
            :key="attachment.name"
            class="mt-2">
            <span class="pill text-nowrap">
              <i class="fas fa-paperclip pr-1 pl-1"></i> {{ attachment.displayName }}
              <b-btn variant="link" class="pr-0 pt-1 pl-0" @click.prevent="removeAttachment(index)">
                <i class="fas fa-times-circle has-error pl-2"></i>
              </b-btn>
            </span>
          </li>
        </ul>
      </div>
    </div>
    <div class="d-flex mt-2 mb-2">
      <div>
        <b-btn
          id="save-note-button"
          class="btn-primary-color-override"
          variant="primary"
          @click="save()">
          Save
        </b-btn>
      </div>
      <div>
        <b-btn
          id="cancel-edit-note-button"
          variant="link"
          @click.stop="cancel()"
          @keypress.enter.stop="cancel()">
          Cancel
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
      target="edit-note-subject"
      title="">
      <span id="popover-error-message" class="has-error">{{ error }}</span>
    </b-popover>
  </form>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal';
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import { updateNote } from '@/api/notes';

require('@/assets/styles/ckeditor-custom.css');

export default {
  name: 'EditAdvisingNote',
  components: { AreYouSureModal },
  mixins: [Context, Util],
  props: {
    afterCancelled: Function,
    afterSaved: Function,
    note: Object
  },
  data: () => ({
    attachment: undefined,
    body: undefined,
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
    },
    error: undefined,
    showAreYouSureModal: false,
    showErrorPopover: false,
    subject: undefined
  }),
  watch: {
    attachment() {
      if (this.attachment) {
        this.note.attachments.push(this.attachment);
        this.attachment = '';
      }
    }
  },
  created() {
    this.alertScreenReader('The edit note form has loaded.');
    this.reset();
  },
  methods: {
    cancel() {
      if (this.trim(this.subject) === this.note.subject && this.stripHtmlAndTrim(this.body) === this.stripHtmlAndTrim(this.note.body)) {
        this.cancelConfirmed();
      } else {
        this.showAreYouSureModal = true;
      }
    },
    cancelConfirmed() {
      this.alertScreenReader('Edit note form cancelled.');
      this.afterCancelled();
      this.reset();
    },
    cancelTheCancel() {
      this.alertScreenReader('Continue editing note.');
      this.showAreYouSureModal = false;
      this.putFocusNextTick('edit-note-subject');
    },
    clearError() {
      this.error = null;
      this.showErrorPopover = false;
    },
    removeAttachment(index) {
      this.note.attachments.splice(index, 1);
    },
    reset() {
      this.subject = this.note.subject;
      this.body = this.note.body || '';
    },
    save() {
      this.subject = this.trim(this.subject);
      if (this.subject) {
        this.body = this.trim(this.body);
        updateNote(this.note.id, this.subject, this.body).then(updatedNote => {
          this.afterSaved(updatedNote);
        });
      } else {
        this.error = 'Subject is required';
        this.showErrorPopover = true;
        this.alertScreenReader(`Validation failed: ${this.error}`);
        this.putFocusNextTick('edit-note-subject');
      }
    }
  }
}
</script>

<style scoped>
.edit-note-form {
  flex-basis: 100%;
}
</style>
