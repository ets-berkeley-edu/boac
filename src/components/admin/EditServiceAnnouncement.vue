<template>
  <div>
    <div class="align-center d-flex publish-checkbox-container">
      <div v-if="isTogglingPublish" class="align-center d-flex font-weight-bold">
        <v-progress-circular
          class="mr-2"
          color="grey"
          :size="25"
          indeterminate
        />
        <span class="text-medium-emphasis">
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
        <label class="font-weight-bold text-medium-emphasis" for="checkbox-publish-service-announcement">
          {{ isPublished ? 'Posted' : 'Post' }}
        </label>
      </div>
    </div>
    <div v-if="error" class="mt-2 text-error w-100">
      <span aria-live="polite" role="alert">{{ error }}</span>
    </div>
    <RichTextEditor
      id="textarea-update-service-announcement"
      :disabled="isSaving"
      :initial-value="originalText ? originalText : ''"
      label="Service alert input"
      :on-value-update="onEditorUpdate"
    />
    <ProgressButton
      id="button-update-service-announcement"
      :action="updateText"
      class="mt-2"
      :disabled="isSaving || text === originalText"
      :in-progress="isSaving"
      :text="isSaving ? 'Updating...' : 'Update'"
    />
  </div>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton'
import RichTextEditor from '@/components/util/RichTextEditor'
import {alertScreenReader} from '@/lib/utils'
import {getServiceAnnouncement, publishAnnouncement, updateAnnouncement} from '@/api/config'
import {onMounted, ref} from 'vue'
import {trim} from 'lodash'

const error = ref(undefined)
const isPublished = ref(undefined)
const isTogglingPublish = ref(false)
const isSaving = ref(false)
const originalText = ref('')
const text = ref('')

onMounted(() => {
  getServiceAnnouncement().then(data => {
    originalText.value = text.value = data.text || ''
    isPublished.value = data.isPublished
  })
})

const onEditorUpdate = value => {
  text.value = value
}

const togglePublish = () => {
  error.value = null
  isTogglingPublish.value = true
  if (!originalText.value.length && isPublished.value) {
    error.value = 'You are not allowed to publish empty text.'
    isTogglingPublish.value = false
  } else {
    publishAnnouncement(isPublished.value).then(data => {
      isPublished.value = data.isPublished
      isTogglingPublish.value = false
      alertScreenReader(`Service announcement has been ${isPublished.value ? 'published' : 'unpublished'}.`)
    })
  }
}

const updateText = () => {
  error.value = null
  isSaving.value = true
  if (!trim(text.value).length && isPublished.value) {
    error.value = 'You are not allowed to publish empty text.'
    isSaving.value = false
  } else {
    updateAnnouncement(text.value).then(data => {
      originalText.value = text.value = data.text
      isPublished.value = data.isPublished
      isSaving.value = false
      alertScreenReader('The service announcement has been updated.')
    })
  }
}
</script>

<style scoped>
.publish-checkbox-container {
  height: 50px;
}
</style>
