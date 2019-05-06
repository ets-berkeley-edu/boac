<template>
  <div v-if="user.isAdmin && announcement !== undefined">
    <h2 class="page-section-header-sub">Service Alert</h2>
    <div class="p-2">
      <span
        v-if="isSaving"
        role="alert"
        aria-live="passive"
        class="sr-only">{{ isPublished ? 'Publishing' : 'Unpublishing' }} the service announcement</span>
      <b-form-checkbox
        id="publish-service-announcement"
        v-model="isPublished"
        :disabled="isSaving">
        <span v-if="isSaving"><i class="fa fa-spinner fa-spin"></i> Saving...</span>
        <span v-if="!isSaving">{{ isPublished ? 'Published' : 'Unpublished' }}</span>
      </b-form-checkbox>
      <b-form-textarea
        id="service-announcement-textarea"
        v-model="announcement"
        aria-label="Enter service announcement for users to read"
        rows="3"
        max-rows="5"
        :disabled="isSaving"
      ></b-form-textarea>
      <div class="mt-1">
        <b-btn variant="primary" @click="save">Save</b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import { getServiceAnnouncement, updateServiceAnnouncement } from '@/api/config';

export default {
  name: 'EditServiceAnnouncement',
  mixins: [Context, UserMetadata],
  data: () => ({
    announcement: undefined,
    isPublished: undefined,
    isSaving: false
  }),
  created() {
    getServiceAnnouncement().then(data => {
      this.announcement = data.text;
      this.isPublished = data.isLive;
    })
  },
  methods: {
    save() {
      this.isSaving = true;
      updateServiceAnnouncement(this.announcement, this.isPublished).then(data => {
        this.announcement = data.text;
        this.isPublished = data.isLive;
        this.isSaving = false;
      });
    }
  }
}
</script>
