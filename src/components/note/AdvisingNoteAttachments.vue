<template>
  <div>
    <div
      :id="`${idPrefix}-attachments-list-label`"
      class="d-inline-block font-size-16 font-weight-bold"
      :class="labelClass"
    >
      Attachments
    </div>
    <div v-if="!isReadOnly" class="mt-2 position-relative">
      <label
        class="note-attachment-inner-label font-size-16 align-center d-flex flex-wrap justify-center"
        :class="{
          'text-medium-emphasis': disabled,
          'cursor-pointer': !(isUploadingAttachments || disabled || attachmentLimitReached)
        }"
        :for="inputId"
      >
        <div v-if="isUploadingAttachments" class="text-medium-emphasis">
          Adding attachments...
        </div>
        <div v-if="!isUploadingAttachments" class="mr-2">
          <span aria-hidden="true">Add attachment:</span>
          <span class="sr-only">Select file for attachment; {{ pluralize('file', attachments.length) }} attached.</span>
        </div>
        <v-btn
          v-if="!isUploadingAttachments"
          :id="`${inputId}-btn`"
          class="bg-white"
          color="black"
          :disabled="isUploadingAttachments || disabled || attachmentLimitReached"
          density="comfortable"
          tabindex="-1"
          type="file"
          variant="outlined"
          @click="onClickBrowseForAttachment"
        >
          Select File
        </v-btn>
      </label>
      <v-file-input
        :id="inputId"
        ref="attachmentFileInput"
        :aria-busy="isUploadingAttachments"
        :aria-describedby="isUploadingAttachments ? progressBarId : `${idPrefix}-attachment-details`"
        class="border-sm choose-file-for-note-attachment rounded"
        :class="{'border-md border-error': !!attachmentError}"
        :clearable="false"
        :disabled="isUploadingAttachments || disabled || attachmentLimitReached"
        flat
        hide-details
        :loading="isUploadingAttachments ? 'primary' : false"
        :model-value="attachments"
        :multiple="true"
        :prepend-icon="null"
        variant="solo-filled"
        @click:control="onClickBrowseForAttachment"
        @update:focused="v => isFocused = v"
        @update:model-value="onAttachmentsInput"
      >
        <template #selection>
          <div />
        </template>
      </v-file-input>
    </div>
    <div :id="`${idPrefix}-attachment-details`">
      <v-alert
        v-if="attachmentError"
        :id="`${idPrefix}-attachment-error`"
        aria-live="polite"
        class="bg-white font-size-14 w-100 my-1"
        density="compact"
        :icon="mdiAlert"
        icon-size="21"
        role="none"
        :text="attachmentError"
        type="error"
        variant="tonal"
      />
      <v-alert
        v-if="attachmentLimitReached"
        :id="`${idPrefix}-attachment-limit`"
        class="bg-white w-100 my-1"
        density="compact"
        icon-size="21"
        role="none"
        type="warning"
        variant="tonal"
      >
        <v-alert-title class="font-size-14">A note can have no more than {{ contextStore.config.maxAttachmentsPerNote }} attachments.</v-alert-title>
      </v-alert>
    </div>
    <ul
      v-if="size(attachments)"
      :id="`${idPrefix}-attachments-list`"
      :aria-labelledby="`${idPrefix}-attachments-list-label`"
      class="list-no-bullets mt-2"
    >
      <li
        v-for="(attachment, index) in attachments"
        :key="index"
      >
        <PillItem
          :id="`${idPrefix}-attachment-${index}`"
          class="my-1 w-fit-content"
          :closable="canRemoveAttachments"
          :disabled="disabled"
          :href="downloadUrl(attachment)"
          :icon="mdiPaperclip"
          :label="attachment.displayName"
          name="attachment"
          @close-clicked="onRemoveAttachment(index)"
        >
          <span v-if="isDownloadable && attachment.id" class="sr-only text-capitalize">Download attachment&nbsp;</span>
          <span
            class="truncate-with-ellipsis"
            :class="{
              'demo-mode-blur': currentUser.inDemoMode,
              'text-anchor': isDownloadable && attachment.id
            }"
          >
            {{ attachment.displayName }}
          </span>
          <span v-if="noteDescription" class="sr-only text-capitalize">, {{ noteDescription }}</span>
        </PillItem>
      </li>
    </ul>
  </div>
</template>

<script setup>
import {computed, onBeforeMount, onBeforeUnmount, onMounted, reactive, ref, watch} from 'vue'
import {each, size} from 'lodash'
import {mdiAlert, mdiPaperclip} from '@mdi/js'
import {storeToRefs} from 'pinia'
import PillItem from '@/components/util/PillItem'
import {addFileDropEventListeners, canUserEditNote, validateAttachment} from '@/lib/note'
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'
import {isPeerAdvisor} from '@/lib/boa-user'

const props = defineProps({
  add: {
    default: () => {},
    required: false,
    type: Function
  },
  attachments: {
    required: true,
    type: Object
  },
  disabled: {
    required: true,
    type: Boolean
  },
  idPrefix: {
    default: 'note',
    required: false,
    type: String
  },
  isDownloadable: {
    required: false,
    type: Boolean
  },
  isReadOnly: {
    required: false,
    type: Boolean
  },
  labelClass: {
    default: '',
    required: false,
    type: String
  },
  note: {
    required: true,
    type: Object
  },
  noteDescription: {
    default: '',
    required: false,
    type: String
  },
  remove: {
    default: () => {},
    required: false,
    type: Function
  }
})

const contextStore = useContextStore()
const noteStore = useNoteStore()

const attachmentFileInput = ref(null)
const attachmentError = ref(undefined)
const attachmentLimitReached = computed(() => {
  return size(props.attachments) >= contextStore.config.maxAttachmentsPerNote
})
const canRemoveAttachments = ref(false)
const currentUser = reactive(contextStore.currentUser)
const inputId = computed(() => `${props.idPrefix}-choose-file-for-note-attachment`)
const isFocused = ref(false)
const {isUploadingAttachments} = storeToRefs(noteStore)
let progressBarAlert
const progressBarId = computed(() => `${props.idPrefix}-attachment-progress`)

watch(isUploadingAttachments, v => {
  const el = attachmentFileInput.value.$el
  const progressBar = el && el.querySelector('.v-progress-linear')
  if (v) {
    progressBarAlert = setInterval(() => {
      alertScreenReader('Still uploading attachments')
    }, 10000)
    if (progressBar) {
      const id = progressBarId.value
      progressBar.removeAttribute('aria-valuemin')
      progressBar.removeAttribute('aria-valuemax')
      progressBar.removeAttribute('aria-hidden')
      progressBar.setAttribute('aria-label', 'Attachment file upload')
      progressBar.setAttribute('aria-valuetext', 'Uploading attachments...')
      progressBar.setAttribute('tabindex', '0')
      progressBar.setAttribute('id', id)
    }
  }
  else {
    if (progressBarAlert) {
      clearInterval(progressBarAlert)
    }
    if (progressBar) {
      progressBar.removeAttribute('tabindex')
    }
  }
})

onBeforeMount(() => {
  addFileDropEventListeners()
})

onMounted(() => {
  canRemoveAttachments.value = !props.isReadOnly
    && (['createPeerAdvisorNote', 'editTemplate'].includes(noteStore.mode) || canUserEditNote(props.note, currentUser))
})

onBeforeUnmount(() => {
  if (progressBarAlert) {
    clearInterval(progressBarAlert)
  }
})

const downloadUrl = (attachment) => {
  let url = undefined
  if (props.isDownloadable && attachment.id) {
    const apiBaseUrl = contextStore.config.apiBaseUrl
    url = isPeerAdvisor(currentUser) ?
      `${apiBaseUrl}/api/peer_advisor/note/attachment/${attachment.id}` :
      `${apiBaseUrl}/api/notes/attachment/${attachment.id}`
  }
  return url
}

const onAttachmentsInput = files => {
  if (size(files)) {
    const pluralized = pluralize('attachment', files.length)
    alertScreenReader(`Adding ${pluralized}`)
    noteStore.setIsUploadingAttachments(true)
    attachmentError.value = validateAttachment(files, props.attachments)
    if (!attachmentError.value) {
      const attachments = []
      each(files, attachment => {
        attachment.displayName = attachment.name
        attachments.push(attachment)
      })
      props.add(attachments).then(() => {
        alertScreenReader(`Added ${pluralized}`)
        noteStore.setIsUploadingAttachments(false)
        putFocusNextTick(inputId.value)
      })
    } else {
      noteStore.setIsUploadingAttachments(false)
      putFocusNextTick(inputId.value)
    }
  }
}

const onClickBrowseForAttachment = () => {
  attachmentError.value = null
  attachmentFileInput.value.click()
}

const onRemoveAttachment = index => {
  attachmentError.value = null
  const lastItemIndex = size(props.attachments) - 1
  if (lastItemIndex > 0) {
    const nextFocusIndex = (index === lastItemIndex ) ? index - 1 : index
    putFocusNextTick(`remove-${props.idPrefix}-attachment-${nextFocusIndex}-btn`)
  } else {
    putFocusNextTick(inputId.value)
  }
  props.remove(index)
}
</script>

<style scoped>
.note-attachment-inner-label {
  height: 100%;
  position: absolute;
  width: 100%;
  z-index: 1;
}
</style>

<style>
.choose-file-for-note-attachment input {
  cursor: pointer;
}
</style>
