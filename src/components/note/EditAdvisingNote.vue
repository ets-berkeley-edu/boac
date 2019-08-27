<template>
  <form class="edit-note-form" @submit.prevent="save()">
    <div>
      <label id="edit-note-subject-label" class="font-weight-bold" for="edit-note-subject">Subject</label>
    </div>
    <div>
      <input
        id="edit-note-subject"
        v-model="noteSubject"
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
          v-model="noteBody"
          :editor="editor"
          :config="editorConfig"></ckeditor>
      </span>
    </div>
    <div v-if="suggestedTopics">
      <AdvisingNoteTopics
        :function-add="addTopic"
        :function-remove="removeTopic"
        :note-id="String(objectId)"
        :suggested-topics="suggestedTopics"
        :topics="topics" />
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
      modal-header="Discard unsaved changes?"
      :show-modal="showAreYouSureModal" />
    <div v-if="size(attachments)">
      <div class="pill-list-header mt-3 mb-1">{{ size(attachments) === 1 ? 'Attachment' : 'Attachments' }}</div>
      <ul class="pill-list pl-0">
        <li
          v-for="(attachment, index) in attachments"
          :id="`note-${objectId}-attachment-${index}`"
          :key="attachment.id"
          class="mt-2"
          @click.stop>
          <span class="pill pill-attachment text-nowrap">
            <font-awesome icon="paperclip" class="pr-1 pl-1" />
            {{ attachment.displayName }}
          </span>
        </li>
      </ul>
    </div>
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
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics';
import AreYouSureModal from '@/components/util/AreYouSureModal';
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import Context from '@/mixins/Context';
import NoteEditSession from '@/mixins/NoteEditSession';
import Util from '@/mixins/Util';
import { updateNote } from '@/api/notes';

require('@/assets/styles/ckeditor-custom.css');

export default {
  name: 'EditAdvisingNote',
  components: { AdvisingNoteTopics, AreYouSureModal },
  mixins: [Context, NoteEditSession, Util],
  props: {
    afterCancel: Function,
    afterSaved: Function,
    note: Object
  },
  data: () => ({
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
    },
    error: undefined,
    noteBody: undefined,
    noteSubject: undefined,
    showAreYouSureModal: false,
    showErrorPopover: false,
    topic: undefined
  }),
  watch: {
    // Vuex-managed 'body' and 'subject' cannot be bound to ckeditor v-model. Thus, we have the following aliases.
    noteBody(value) {
      this.setBody(value);
    },
    noteSubject(value) {
      this.setSubject(value);
    }
  },
  created() {
    this.reset();
    this.init({
      note: this.cloneDeep(this.note),
      noteMode: 'edit'
    });
    this.noteSubject = this.note.subject;
    this.noteBody = this.note.body;
    this.addSid(this.note.sid);
    this.putFocusNextTick('edit-note-subject');
    this.alertScreenReader('Edit note form is open.');
  },
  methods: {
    cancel() {
      this.clearErrors();
      const isPristine = this.trim(this.subject) === this.note.subject
        && this.stripHtmlAndTrim(this.body) === this.stripHtmlAndTrim(this.note.body);
      if (isPristine) {
        this.cancelConfirmed();
      } else {
        this.showAreYouSureModal = true;
      }
    },
    cancelConfirmed() {
      this.afterCancel();
      this.reset();
      this.alertScreenReader('Edit note form cancelled.');
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
    reset() {
      this.resetSession();
      this.clearErrors();
      this.noteBody = null;
      this.noteSubject = null;
    },
    save() {
      const trimmedSubject = this.trim(this.subject);
      if (trimmedSubject) {
        updateNote(this.objectId, trimmedSubject, this.trim(this.noteBody), this.topics).then(updatedNote => {
          this.afterSaved(updatedNote);
          this.reset();
          this.alertScreenReader('Changes to note have been saved');
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
