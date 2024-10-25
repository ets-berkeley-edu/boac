<template>
  <div>
    <div class="align-center d-flex publish-checkbox-container">
      <div v-if="isTogglingPublish" class="align-center d-flex font-weight-bold">
        <v-progress-circular
          class="mr-2"
          color="primary"
          :size="25"
          indeterminate
        />
        <span class="text-medium-emphasis">
          {{ isPublished ? 'Posting...' : 'Unposting...' }}
        </span>
      </div>
      <div :class="{'sr-only': isTogglingPublish}" class="align-center d-flex">
        <input
          id="checkbox-publish-service-announcement"
          v-model="isPublished"
          aria-label="Post Service Alert"
          class="checkbox mr-2"
          :disabled="isSaving || !originalText || !originalText.length"
          type="checkbox"
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
      :disabled="isSaving || isTogglingPublish"
      :initial-value="originalText ? originalText : ''"
      label="Service alert input"
      :on-value-update="onEditorUpdate"
    />
    <ProgressButton
      id="button-update-service-announcement"
      :action="updateText"
      aria-label="Update Service Alert"
      class="mt-2"
      :disabled="isSaving || text === originalText || isTogglingPublish"
      :in-progress="isSaving"
      :text="isSaving ? 'Updating...' : 'Update'"
    />
  </div>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton'
import RichTextEditor from '@/components/util/RichTextEditor'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
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
  alertScreenReader(isPublished.value ? 'Publishing' : 'Unpublishing')
  error.value = null
  isTogglingPublish.value = true
  if (!originalText.value.length && isPublished.value) {
    error.value = 'You are not allowed to publish empty text.'
    isTogglingPublish.value = false
  } else {
    const beforeAlertShown = isPublished => alertScreenReader(`${isPublished ? 'Published' : 'Unpublished'} Service Alert.`, 'assertive')
    publishAnnouncement(isPublished.value, beforeAlertShown).then(data => {
      isPublished.value = data.isPublished
      isTogglingPublish.value = false
      putFocusNextTick('checkbox-publish-service-announcement')
    })
  }
}

const updateText = () => {
  alertScreenReader('Updating service alert')
  error.value = null
  isSaving.value = true
  if (!trim(text.value).length && isPublished.value) {
    error.value = 'You are not allowed to publish empty text.'
    isSaving.value = false
  } else {
    const beforeAlertShown = () => alertScreenReader('Service alert updated.')
    updateAnnouncement(text.value, beforeAlertShown).then(data => {
      originalText.value = text.value = data.text
      isPublished.value = data.isPublished
      isSaving.value = false
    })
  }
}
</script>

<style scoped>
.publish-checkbox-container {
  height: 50px;
}
</style>
