<template>
  <div v-if="announcement !== undefined && originalText !== undefined">
    <div class="pa-5">
      <div v-if="isTogglingPublish">
        <Spinner />
        {{ isPublished ? 'Unposting...' : 'Posting...' }}
      </div>
      <div v-if="!isTogglingPublish">
        <v-checkbox
          id="checkbox-publish-service-announcement"
          v-model="isPublished"
          :disabled="isSaving || !originalText || !originalText.length"
          @change="togglePublish"
        >
          <span id="checkbox-service-announcement-label">{{ isPublished ? 'Posted' : 'Post' }}</span>
        </v-checkbox>
      </div>
      <div>
        <div v-if="error" class="mt-2 has-error w-100">
          <span aria-live="polite" role="alert">{{ error }}</span>
        </div>
        <RichTextEditor
          id="textarea-update-service-announcement"
          :initial-value="originalText"
          :disabled="isSaving"
          label="Service alert input"
          :on-value-update="onEditorUpdate"
        />
        <div>
          <v-btn
            id="button-update-service-announcement"
            :disabled="text === originalText"
            variant="primary"
            class="btn-primary-color-override mt-2"
            @click="updateText"
          >
            <!-- <span v-if="isSaving"><font-awesome icon="spinner" spin /> Update...</span> -->
            <span v-if="!isSaving">Update</span>
          </v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import Context from '@/mixins/Context'
import RichTextEditor from '@/components/util/RichTextEditor'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {getServiceAnnouncement, publishAnnouncement, updateAnnouncement} from '@/api/config'
import {useContextStore} from '@/stores/context'

export default {
  name: 'EditServiceAnnouncement',
  components: {RichTextEditor, Spinner},
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
          useContextStore().alertScreenReader(`Service announcement has been ${this.isPublished ? 'published' : 'unpublished'}.`)
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
          useContextStore().alertScreenReader('The service announcement has been updated.')
        })
      }
    }
  }
}
</script>
