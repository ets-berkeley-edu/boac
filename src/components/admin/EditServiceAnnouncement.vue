<template>
  <div v-if="announcement !== undefined" class="mt-3">
    <h2 id="edit-service-announcement" class="page-section-header-sub">Service Alert</h2>
    <div class="p-2">
      <div v-if="isTogglingPublish">
        <span class="fa fa-spinner fa-spin"></span>
        {{ isPublished ? 'Unposting...' : 'Posting...' }}
      </div>
      <div v-if="!isTogglingPublish">
        <b-form-checkbox
          id="checkbox-publish-service-announcement"
          v-model="isPublished"
          :disabled="isSaving || !originalText || !originalText.length || text !== originalText"
          @change="togglePublish">
          <span id="checkbox-service-announcement-label">{{ isPublished ? 'Posted' : 'Post' }}</span>
        </b-form-checkbox>
      </div>
      <div class="mt-3">
        <div v-if="error" class="mt-2 has-error w-100">
          <span aria-live="polite" role="alert">{{ error }}</span>
        </div>
        <ckeditor
          id="textarea-update-service-announcement"
          v-model="text"
          aria-label="Service announcement input"
          :config="editorConfig"
          :disabled="isSaving"
          :editor="editor"></ckeditor>
        <div>
          <b-btn
            id="button-update-service-announcement"
            variant="primary"
            class="btn-primary-color-override mt-2"
            :disabled="text === originalText"
            @click="updateText">
            <span v-if="isSaving"><i class="fa fa-spinner fa-spin"></i> Update...</span>
            <span v-if="!isSaving">Update</span>
          </b-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ClassicEditor from '@ckeditor/ckeditor5-build-classic';
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import { getServiceAnnouncement, publishAnnouncement, updateAnnouncement } from '@/api/config';

require('@/assets/styles/ckeditor-custom.css');

export default {
  name: 'EditServiceAnnouncement',
  mixins: [Context, Util],
  data: () => ({
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link']
    },
    error: undefined,
    isPublished: undefined,
    isTogglingPublish: false,
    isSaving: false,
    originalText: undefined,
    text: undefined
  }),
  created() {
    getServiceAnnouncement().then(data => {
      this.originalText = this.text = data.text;
      this.isPublished = data.isPublished;
    })
  },
  methods: {
    togglePublish() {
      const publish = !this.isPublished;
      this.error = null;
      this.isTogglingPublish = true;
      if (!this.originalText.length && publish) {
        this.error = 'You are not allowed to publish empty text.';
        this.isTogglingPublish = false;
      } else {
        publishAnnouncement(publish).then(data => {
          this.isPublished = data.isPublished;
          this.isTogglingPublish = false;
          this.alertScreenReader(`Service announcement has been ${this.isPublished ? 'published' : 'unpublished'}.`);
        });
      }
    },
    updateText() {
      this.error = null;
      this.isSaving = true;
      if (!this.trim(this.text).length && this.isPublished) {
        this.error = 'You are not allowed to publish empty text.';
        this.isSaving = false;
      } else {
        updateAnnouncement(this.text).then(data => {
          this.originalText = this.text = data.text;
          this.isPublished = data.isPublished;
          this.isSaving = false;
          this.alertScreenReader('The service announcement has been updated.');
        });
      }
    }
  }
}
</script>
