<template>
  <div v-if="announcement !== undefined" class="mt-3">
    <h2 class="page-section-header-sub">Service Alert</h2>
    <div v-if="error" class="has-error ml-2 p-1 w-100">
      <span aria-live="polite" role="alert">{{ error }}</span>
    </div>
    <div class="p-2">
      <b-form-textarea
        id="service-announcement-textarea"
        v-model="text"
        aria-label="Enter service announcement for users to read"
        rows="3"
        max-rows="5"
        :disabled="isSaving"
      ></b-form-textarea>
      <span
        v-if="isSaving"
        role="alert"
        aria-live="passive"
        class="sr-only">{{ isPublished ? 'Publishing' : 'Unpublishing' }} the service announcement</span>
      <b-form-checkbox
        id="publish-service-announcement"
        v-model="isPublished"
        class="mt-2 ml-2"
        :disabled="isSaving">
        Publish
      </b-form-checkbox>
      <div>
        <b-btn variant="primary" class="btn-primary-color-override m-2" @click="save">
          <span v-if="isSaving"><i class="fa fa-spinner fa-spin"></i> Saving...</span>
          <span v-if="!isSaving">Save</span>
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import { getServiceAnnouncement, updateServiceAnnouncement } from '@/api/config';

export default {
  name: 'EditServiceAnnouncement',
  mixins: [Context, Util],
  data: () => ({
    error: undefined,
    text: undefined,
    isPublished: undefined,
    isSaving: false
  }),
  created() {
    getServiceAnnouncement().then(data => {
      this.text = data.text;
      this.isPublished = data.isLive;
    })
  },
  methods: {
    save() {
      this.error = null;
      this.isSaving = true;
      this.text = this.trim(this.text);
      if (!this.text.length && this.isPublished) {
        this.error = 'You are not allowed to publish empty text.';
        this.isSaving = false;
      } else {
        updateServiceAnnouncement(this.text, this.isPublished).then(data => {
          this.text = data.text;
          this.isPublished = data.isLive;
          this.isSaving = false;
        });
      }
    }
  }
}
</script>
