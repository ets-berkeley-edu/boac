<template>
  <div>
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
        maxlength="255">
    </div>
    <div>
      <label class="font-weight-bold mt-2" for="edit-note-details">
        Note Details
      </label>
    </div>
    <div id="edit-note-details">
      <span class="bg-transparent note-details-editor">
        <ckeditor
          v-model="body"
          :editor="editor"
          :config="editorConfig"></ckeditor>
      </span>
    </div>
    <div class="d-flex mt-2">
      <div>
        <b-btn class="btn-primary-color-override" variant="primary" @click="save()">Save</b-btn>
      </div>
      <div>
        <b-btn variant="link" @click="cancel()">Cancel</b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import Util from '@/mixins/Util';
import { updateNote } from '@/api/notes';

require('@/assets/styles/ckeditor-custom.css');

export default {
  name: 'EditAdvisingNote',
  mixins: [Util],
  props: {
    afterCancelled: Function,
    afterSaved: Function,
    note: Object
  },
  data: () => ({
    body: undefined,
    error: undefined,
    showErrorPopover: false,
    screenReaderAlert: undefined,
    subject: undefined,
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
    }
  }),
  created() {
    this.reset();
  },
  methods: {
    cancel() {
      this.afterCancelled();
      this.reset();
    },
    reset() {
      this.subject = this.note.subject;
      this.body = this.note.body;
    },
    save() {
      updateNote(this.note.id, this.subject, this.body).then(updatedNote => {
        this.afterSaved(updatedNote.id, updatedNote.subject, updatedNote.body);
      });
    }
  }
}
</script>
