<template>
  <form @submit.prevent="save()">
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
    <div class="d-flex mt-2">
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
