<template>
  <div>
    <slot name="label"></slot>
    <v-file-input
      v-if="!readOnly"
      :id="inputId"
      ref="attachmentFileInput"
      :model-value="model.attachments"
      :aria-busy="isAdding"
      :aria-describedby="isAdding ? progressBarId : null"
      :aria-label="`Select file for attachment; ${pluralize('file', model.attachments.length)} attached.`"
      class="border-sm choose-file-for-note-attachment rounded"
      :class="{'border-success': disabled || attachmentLimitReached, 'border-md border-error': !!attachmentError}"
      :clearable="false"
      :disabled="isAdding || disabled || attachmentLimitReached"
      flat
      hide-details
      :loading="isAdding ? 'success' : false"
      multiple
      :prepend-icon="null"
      single-line
      :variant="disabled || attachmentLimitReached ? 'outlined' : 'solo-filled'"
      @click:control="clickBrowseForAttachment"
      @update:model-value="onAttachmentsInput"
    >
      <template #label>
        <div
          class="font-size-16 align-center d-flex justify-center"
          :class="{
            'font-weight-bold text-black text-center': disabled || attachmentLimitReached,
            'font-weight-medium': !disabled && !attachmentLimitReached
          }"
        >
          <div v-if="isAdding" class="pb-1">
            Adding attachments...
          </div>
          <div v-if="!isAdding" class="mr-2 ">
            Add attachment:
          </div>
          <v-btn
            v-if="!isAdding"
            :id="`${idPrefix}choose-file-for-note-attachment-btn`"
            :aria-hidden="true"
            class="bg-white"
            color="black"
            :disabled="disabled || attachmentLimitReached"
            density="comfortable"
            tabindex="-1"
            type="file"
            variant="outlined"
          >
            Select File
          </v-btn>
        </div>
      </template>
      <template #selection>
        <div></div>
      </template>
    </v-file-input>
    <v-alert
      v-if="attachmentError"
      :id="`${idPrefix}attachment-error`"
      aria-live="polite"
      class="font-size-14 w-100 mb-1 mt-2"
      density="compact"
      :icon="mdiAlert"
      :text="attachmentError"
      type="error"
      variant="tonal"
    />
    <v-alert
      v-if="attachmentLimitReached"
      :id="`${idPrefix}attachment-limit`"
      aria-live="polite"
      class="w-100 mt-2"
      density="compact"
      type="warning"
      variant="tonal"
    >
      A note can have no more than {{ contextStore.config.maxAttachmentsPerNote }} attachments.
    </v-alert>
    <ul
      :id="`${idPrefix}attachments-list`"
      aria-label="attachments"
      class="list-no-bullets mt-2"
    >
      <li
        v-for="(attachment, index) in modelProxy.attachments"
        :key="index"
      >
        <PillItem
          :id="`${idPrefix}attachment-${index}`"
          :aria-label="downloadable ? `Download attachment ${attachment.displayName}` : null"
          clazz="attachment-chip"
          :closable="!readOnly && currentUser.uid === get(modelProxy.author, 'uid')"
          :disabled="disabled"
          :href="downloadUrl(attachment)"
          :icon="mdiPaperclip"
          :label="attachment.displayName"
          name="attachment"
          :on-click-close="() => onRemoveAttachment(index)"
        >
          <span class="truncate-with-ellipsis pr-1">
            {{ attachment.displayName }}
          </span>
        </PillItem>
      </li>
    </ul>
  </div>
</template>

<script setup>
import PillItem from '@/components/util/PillItem'
import {addFileDropEventListeners, validateAttachment} from '@/lib/note'
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'
import {computed, onBeforeMount, onBeforeUnmount, reactive, ref, watch} from 'vue'
import {each, get, size} from 'lodash'
import {mdiAlert, mdiPaperclip} from '@mdi/js'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  addAttachments: {
    default: () => {},
    required: false,
    type: Function
  },
  disabled: {
    required: true,
    type: Boolean
  },
  downloadable: {
    required: false,
    type: Boolean
  },
  idPrefix: {
    default: '',
    required: false,
    type: String
  },
  note: {
    default: undefined,
    required: false,
    type: Object
  },
  readOnly: {
    required: false,
    type: Boolean
  },
  removeAttachment: {
    default: () => {},
    required: false,
    type: Function
  }
})

const noteStore = useNoteStore()

const attachmentFileInput = ref(null)
const attachmentError = ref(undefined)
const contextStore = useContextStore()
const currentUser = reactive(contextStore.currentUser)
const isAdding = ref(false)
const {mode, model} = storeToRefs(noteStore)
const modelProxy = ref(props.note || noteStore.model)

const attachmentLimitReached = computed(() => {
  return size(model.value.attachments) >= contextStore.config.maxAttachmentsPerNote
})

const inputId = `${props.idPrefix}choose-file-for-note-attachment`
const progressBarId = `${props.idPrefix}note-attachment-progress`
let progressBarAlert

watch(isAdding, v => {
  if (v) {
    progressBarAlert = setInterval(() => {
      alertScreenReader('Still uploading attachments')
    }, 10000)
    const el = attachmentFileInput.value.$el
    const progressBar = el && el.querySelector('.v-progress-linear')
    if (progressBar) {
      const id = progressBarId
      progressBar.removeAttribute('aria-valuemin')
      progressBar.removeAttribute('aria-valuemax')
      progressBar.setAttribute('aria-label', 'Attachment file upload')
      progressBar.setAttribute('aria-valuetext', 'Uploading attachments...')
      progressBar.setAttribute('tabindex', '0')
      progressBar.setAttribute('id', id)
      putFocusNextTick(id)
    } else {
      putFocusNextTick(inputId)
    }
  }
  else {
    if (progressBarAlert) {
      clearInterval(progressBarAlert)
      putFocusNextTick(inputId)
    }
  }
})

watch(mode, () => {
  modelProxy.value = props.note || noteStore.model
})

watch(model, () => {
  modelProxy.value = props.note || noteStore.model
})

const clickBrowseForAttachment = () => {
  attachmentFileInput.value.click()
}

const downloadUrl = (attachment) => {
  return props.downloadable ? `${contextStore.config.apiBaseUrl}/api/notes/attachment/${attachment.id}` : null
}

const onAttachmentsInput = files => {
  if (size(files)) {
    const pluralized = pluralize('attachment', files.length)
    alertScreenReader(`Adding ${pluralized}`)
    isAdding.value = true
    attachmentError.value = validateAttachment(files, modelProxy.value.attachments)
    if (!attachmentError.value) {
      const attachments = []
      each(files, attachment => {
        attachment.displayName = attachment.name
        attachments.push(attachment)
      })
      props.addAttachments(attachments).then(() => {
        alertScreenReader(`${pluralized} added`)
        isAdding.value = false
      })
    } else {
      isAdding.value = false
    }
  }
}

const onRemoveAttachment = index => {
  const lastItemIndex = size(modelProxy.value.attachments) - 1
  if (lastItemIndex > 0) {
    const nextFocusIndex = (index === lastItemIndex ) ? index - 1 : index
    putFocusNextTick(`remove-${props.idPrefix}attachment-${nextFocusIndex}-btn`)
  } else {
    putFocusNextTick(inputId)
  }
  props.removeAttachment(index)
}

onBeforeMount(() => {
  addFileDropEventListeners()
})

onBeforeUnmount(() => {
  if (progressBarAlert) {
    clearInterval(progressBarAlert)
  }
})
</script>

<style scoped>
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.attachment-chip {
  max-width: 450px;
}
</style>

<style>
.choose-file-for-note-attachment .v-label.v-field-label {
  visibility: visible !important;
  width: 100%;
}
.choose-file-for-note-attachment input {
  cursor: pointer;
}
</style>
