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
    <div class="mt-2 mb-2">
      <ManageNoteAttachments
        :attachments="attachments"
        :clear-errors="clearErrors"
        :put-delete-attachment-id="removeAttachment" />
      <AreYouSureModal
        v-if="showConfirmDeleteAttachment"
        button-label-confirm="Delete"
        :function-cancel="cancelRemoveAttachment"
        :function-confirm="confirmedRemoveAttachment"
        :modal-body="`Are you sure you want to delete the <b>'${displayName(attachments, deleteAttachmentIndex)}'</b> attachment?`"
        modal-header="Delete Attachment"
        :show-modal="showConfirmDeleteAttachment" />
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
import ManageNoteAttachments from '@/components/note/ManageNoteAttachments';
import Util from '@/mixins/Util';
import { updateNote } from '@/api/notes';

require('@/assets/styles/ckeditor-custom.css');

export default {
  name: 'EditAdvisingNote',
  components: { AreYouSureModal, ManageNoteAttachments },
  mixins: [Context, Util],
  props: {
    afterCancelled: Function,
    afterSaved: Function,
    note: Object
  },
  data: () => ({
    attachments: undefined,
    body: undefined,
    deleteAttachmentIds: [],
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
    },
    error: undefined,
    showAreYouSureModal: false,
    showConfirmDeleteAttachment: false,
    showErrorPopover: false,
    subject: undefined
  }),
  created() {
    this.alertScreenReader('The edit note form has loaded.');
    this.reset();
  },
  methods: {
    cancel() {
      this.clearErrors();
      const newAttachments = this.filterList(this.attachments, a => !a.id);
      const isPristine = this.trim(this.subject) === this.note.subject
        && this.stripHtmlAndTrim(this.body) === this.stripHtmlAndTrim(this.note.body)
        && this.size(newAttachments) === 0;
      if (isPristine) {
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
    clearErrors() {
      this.error = null;
      this.showErrorPopover = false;
    },
    displayName(attachments, index) {
      return this.size(attachments) <= index ? '' : attachments[index].displayName;
    },
    removeAttachment(attachment) {
      this.clearErrors();
      const index = this.findIndex(this.attachments, {name: attachment.name});
      const removeMe = this.attachments[index];
      if (removeMe.id) {
        this.deleteAttachmentIds.push(attachment.id);
        this.showConfirmDeleteAttachment = true;
      } else {
        this.attachments.splice(index, 1);
      }
    },
    cancelRemoveAttachment() {
      this.showConfirmDeleteAttachment = false;
      this.deleteAttachmentIndex = null;
    },
    confirmedRemoveAttachment() {
      this.showConfirmDeleteAttachment = false;
      const attachment = this.attachments[this.deleteAttachmentIndex];
      this.attachments.splice(this.deleteAttachmentIndex, 1);
      this.alertScreenReader(`Attachment '${attachment.displayName}' removed`);
      this.deleteAttachmentIndex = null;
    },
    reset() {
      this.clearErrors();
      this.subject = this.note.subject;
      this.body = this.note.body || '';
      this.attachments = this.cloneDeep(this.note.attachments);
    },
    save() {
      this.subject = this.trim(this.subject);
      if (this.subject) {
        this.body = this.trim(this.body);
        // Add new attachments only
        const newAttachments = this.filterList(this.attachments, a => !a.id);
        updateNote(this.note.id, this.subject, this.body, newAttachments, this.deleteAttachmentIds).then(updatedNote => {
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
