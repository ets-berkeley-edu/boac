<template>
  <div>
    <div class="align-center d-flex publish-checkbox-container">
      <div v-if="isTogglingPublish" class="align-center d-flex font-weight-700">
        <v-progress-circular
          class="mr-2"
          color="grey"
          :size="25"
          indeterminate
        />
        <span class="text-grey">
          {{ isPublished ? 'Posting...' : 'Unposting...' }}
        </span>
      </div>
      <div v-if="!isTogglingPublish" class="align-center d-flex">
        <v-checkbox
          id="checkbox-publish-service-announcement"
          v-model="isPublished"
          class="mr-1"
          color="primary"
          density="compact"
          :disabled="isSaving || !originalText || !originalText.length"
          hide-details
          @change="togglePublish"
        />
        <label class="font-weight-700 text-grey" for="checkbox-publish-service-announcement">
          {{ isPublished ? 'Posted' : 'Post' }}
        </label>
      </div>
    </div>
    <div v-if="error" class="mt-2 text-error w-100">
      <span aria-live="polite" role="alert">{{ error }}</span>
    </div>
    <RichTextEditor
      id="textarea-update-service-announcement"
      :initial-value="originalText ? originalText : ''"
      :disabled="isSaving"
      label="Service alert input"
      :on-value-update="onEditorUpdate"
    />
    <v-btn
      id="button-update-service-announcement"
      class="btn-primary-color-override mt-2"
      color="primary"
      :disabled="text === originalText"
      variant="flat"
      @click="updateText"
    >
      <span v-if="isSaving">
        <v-progress-circular
          :size="25"
          color="primary"
          indeterminate
        />
        Update...
      </span>
      <span v-if="!isSaving">Update</span>
    </v-btn>
  </div>
</template>

<script>
import RichTextEditor from '@/components/util/RichTextEditor'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
import {getServiceAnnouncement, publishAnnouncement, updateAnnouncement} from '@/api/config'
import {useContextStore} from '@/stores/context'

export default {
  name: 'EditServiceAnnouncement',
  components: {RichTextEditor},
  mixins: [Util],
  data: () => ({
    error: undefined,
    isPublished: undefined,
    isTogglingPublish: false,
    isSaving: false,
    originalText: undefined,
    text: undefined,
    announcement: useContextStore().announcement
  }),
  created() {
    getServiceAnnouncement().then(data => {
      this.originalText = this.text = data.text || ''
      this.isPublished = data.isPublished
    })
  },
  methods: {
    onEditorUpdate(value) {
      this.text = value
    },
    togglePublish() {
      this.error = null
      this.isTogglingPublish = true
      if (!this.originalText.length && this.isPublished) {
        this.error = 'You are not allowed to publish empty text.'
        this.isTogglingPublish = false
      } else {
        publishAnnouncement(this.isPublished).then(data => {
          this.isPublished = data.isPublished
          this.isTogglingPublish = false
          alertScreenReader(`Service announcement has been ${this.isPublished ? 'published' : 'unpublished'}.`)
        })
      }
    },
    updateText() {
      this.error = null
      this.isSaving = true
      if (!this._trim(this.text).length && this.isPublished) {
        this.error = 'You are not allowed to publish empty text.'
        this.isSaving = false
      } else {
        updateAnnouncement(this.text).then(data => {
          this.originalText = this.text = data.text
          this.isPublished = data.isPublished
          this.isSaving = false
          alertScreenReader('The service announcement has been updated.')
        })
      }
    }
  }
}
</script>

<style scoped>
.publish-checkbox-container {
  height: 50px;
}
</style>
