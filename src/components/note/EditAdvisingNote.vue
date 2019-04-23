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
      <div v-if="attachmentError" class="mt-3 mb-3 w-100">
        <i class="fa fa-exclamation-triangle text-danger pr-1"></i>
        <span aria-live="polite" role="alert">{{ attachmentError }}</span>
      </div>
      <div v-if="size(attachments) < maxAttachmentsPerNote" class="w-100">
        <label for="choose-file-for-note-attachment" class="sr-only"><span class="sr-only">Note </span>Attachments</label>
        <div class="choose-attachment-file-wrapper no-wrap pl-3 pr-3 w-100">
          Drop file to upload attachment or
          <b-btn
            id="choose-file-for-note-attachment"
            type="file"
            variant="outline-primary"
            class="btn-file-upload mt-2 mb-2"
            size="sm">
            Browse<span class="sr-only"> for file to upload</span>
          </b-btn>
          <b-form-file
            v-model="attachment"
            :disabled="size(attachments) === maxAttachmentsPerNote"
            :state="Boolean(attachment)"
            :plain="true"
          ></b-form-file>
        </div>
      </div>
      <div v-if="size(attachments) === maxAttachmentsPerNote" class="w-100">
        A note can have no more than {{ maxAttachmentsPerNote }} attachments.
      </div>
      <div>
        <ul class="pill-list pl-0">
          <li
            v-for="(attachment, index) in attachments"
            :id="`edit-note-attachment-${index}`"
            :key="attachment.name"
            :class="{'mt-2': index === 0}">
            <span class="pill text-nowrap">
              <i class="fas fa-paperclip pr-1 pl-1"></i> {{ attachment.displayName }}
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
      v-if="showConfirmDeleteAttachment"
      button-label-confirm="Delete"
      :function-cancel="cancelRemoveAttachment"
      :function-confirm="confirmedRemoveAttachment"
      :modal-body="`Are you sure you want to delete the <b>'${displayName(attachments, deleteAttachmentIndex)}'</b> attachment?`"
      modal-header="Delete Attachment"
      :show-modal="showConfirmDeleteAttachment" />
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
import NoteUtil from '@/components/note/NoteUtil';
import Util from '@/mixins/Util';
import { updateNote } from '@/api/notes';

require('@/assets/styles/ckeditor-custom.css');

export default {
  name: 'EditAdvisingNote',
  components: { AreYouSureModal },
  mixins: [Context, NoteUtil, Util],
  props: {
    afterCancelled: Function,
    afterSaved: Function,
    note: Object
  },
  data: () => ({
    attachment: undefined,
    attachmentError: undefined,
    attachments: undefined,
    body: undefined,
    deleteAttachmentIndex: undefined,
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
  watch: {
    attachment() {
      if (this.attachment) {
        const name = this.attachment.name;
        const matching = this.filterList(this.attachments, a => name === a.displayName);
        if (this.size(matching)) {
          this.attachmentError = `Another attachment has the name '${name}'. Please rename your file.`;
        } else {
          this.attachment.displayName = name;
          this.clearErrors();
          this.attachments.push(this.attachment);
          this.alertScreenReader(`Attachment '${name}' added`);
        }
      }
    }
  },
  created() {
    this.alertScreenReader('The edit note form has loaded.');
    this.initFileDropPrevention();
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
      this.attachmentError = null;
      this.error = null;
      this.showErrorPopover = false;
    },
    displayName(attachments, index) {
      return this.size(attachments) <= index ? '' : attachments[index].displayName;
    },
    removeAttachment(index) {
      this.clearErrors();
      const removeMe = this.attachments[index];
      if (removeMe.id) {
        this.deleteAttachmentIndex = index;
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
      this.deleteAttachmentIds.push(attachment.id);
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
.btn-file-upload {
  border-color: grey;
  color: grey;
}
.btn-file-upload:hover,
.btn-file-upload:focus,
.btn-file-upload:active
{
  color: #333;
  background-color: #aaa;
}
.choose-attachment-file-wrapper {
  position: relative;
  align-items: center;
  overflow: hidden;
  display: inline-block;
  background-color: #f7f7f7;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  text-align: center;
}
.choose-attachment-file-wrapper input[type=file] {
  font-size: 100px;
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0;
}
.choose-attachment-file-wrapper:hover,
.choose-attachment-file-wrapper:focus,
.choose-attachment-file-wrapper:active
{
  color: #333;
  background-color: #eee;
}
.edit-note-form {
  flex-basis: 100%;
}
.form-control-file {
  height: 100%;
}
</style>
