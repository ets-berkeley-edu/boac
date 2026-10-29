<template>
  <div>
    <div
      :id="`${idPrefix}-attachments-list-label`"
      class="d-inline-block font-size-16 font-weight-bold"
      :class="labelClass"
    >
      Attachments
    </div>
    <template v-if="!isReadOnly">
      <span class="font-size-16 ml-1">(</span><v-btn
        :id="`${idPrefix}-allowed-attachment-types-toggle`"
        :aria-controls="`${idPrefix}-allowed-attachment-types`"
        :aria-expanded="showAllowedTypes"
        class="font-size-16 px-0 text-none"
        color="primary"
        density="compact"
        height="auto"
        min-width="0"
        slim
        variant="text"
        @click="showAllowedTypes = !showAllowedTypes"
      >
        <v-icon :icon="showAllowedTypes ? mdiMenuDown : mdiMenuRight" size="1.25rem" />
        {{ showAllowedTypes ? 'hide' : 'show' }} allowed attachment file types
      </v-btn><span class="font-size-16">)</span>
      <v-expand-transition>
        <ul
          v-show="showAllowedTypes"
          :id="`${idPrefix}-allowed-attachment-types`"
          class="font-size-14 list-no-bullets mt-1"
        >
          <li v-for="allowedType in contextStore.config.allowedAttachmentTypes" :key="allowedType.label">
            <span class="font-italic">{{ allowedType.label }}:</span> {{ allowedType.extensions.join(', ') }}
          </li>
        </ul>
      </v-expand-transition>
    </template>
    <div v-if="!isReadOnly" class="mt-2 position-relative">
      <label
        class="note-attachment-inner-label font-size-16 align-center d-flex flex-wrap justify-center"
        :class="{
          'text-medium-emphasis': disabled,
          'cursor-pointer': canAddAttachments
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
          :disabled="!canAddAttachments"
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
        :disabled="!canAddAttachments"
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
        icon-size="1.3125rem"
        role="none"
        :text="attachmentError"
        type="error"
        variant="tonal"
      />
      <v-alert
        v-if="!isReadOnly && attachmentLimitReached"
        :id="`${idPrefix}-attachment-limit`"
        class="bg-white w-100 my-1"
        density="compact"
        icon-size="1.3125rem"
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
            class="wrap-anywhere"
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
    <ul
      v-if="!isReadOnly && size(rejectedAttachments)"
      :id="`${idPrefix}-rejected-attachments-list`"
      class="list-no-bullets"
    >
      <li
        v-for="(rejected, index) in rejectedAttachments"
        :key="rejected.name"
        class="align-center d-flex flex-wrap"
      >
        <PillItem
          :id="`${idPrefix}-rejected-attachment-${index}`"
          class="my-1 mr-2 w-fit-content"
          :closable="true"
          :disabled="disabled"
          :icon="mdiPaperclip"
          :label="rejected.name"
          name="attachment"
          @close-clicked="onRemoveRejectedAttachment(index)"
        >
          <span class="text-decoration-line-through wrap-anywhere">{{ rejected.name }}</span>
        </PillItem>
        <span
          :id="`${idPrefix}-rejected-attachment-${index}-error`"
          class="font-size-14 font-weight-bold text-error"
        >
          {{ rejected.message }}
        </span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import {computed, onBeforeMount, onBeforeUnmount, reactive, ref, watch} from 'vue'
import {each, find, partition, size} from 'lodash'
import {mdiAlert, mdiMenuDown, mdiMenuRight, mdiPaperclip} from '@mdi/js'
import {storeToRefs} from 'pinia'
import PillItem from '@/components/util/PillItem'
import {
  addFileDropEventListeners,
  canUserEditNote,
  getFileExtension,
  isAllowedAttachmentType,
  validateAttachment
} from '@/lib/note'
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
const currentUser = reactive(contextStore.currentUser)
const inputId = computed(() => `${props.idPrefix}-choose-file-for-note-attachment`)
const isFocused = ref(false)
const {isUploadingAttachments} = storeToRefs(noteStore)
let progressBarAlert
const progressBarId = computed(() => `${props.idPrefix}-attachment-progress`)
const rejectedAttachments = ref([])
const showAllowedTypes = ref(false)
const canAddAttachments = computed(() => {
  return !isUploadingAttachments.value && !props.disabled && !attachmentLimitReached.value
})
const canRemoveAttachments = computed(() => {
  return !props.isReadOnly && (
    ['createPeerAdvisorNote', 'editTemplate'].includes(noteStore.mode) || canUserEditNote(props.note, currentUser)
  )
})

watch(isUploadingAttachments, v => {
  const el = attachmentFileInput.value ? attachmentFileInput.value.$el : null
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

const onAttachmentsInput = selected => {
  attachmentError.value = null
  const [files, rejected] = partition(selected, file => isAllowedAttachmentType(file.name))
  each(rejected, file => {
    if (!find(rejectedAttachments.value, {name: file.name})) {
      const extension = getFileExtension(file.name)
      const message = extension ? `.${extension.toUpperCase()} file attachment not allowed` : 'File attachment without a file type not allowed'
      rejectedAttachments.value.push({message, name: file.name})
      alertScreenReader(`${file.name}: ${message}`)
    }
  })
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

const onRemoveRejectedAttachment = index => {
  const lastItemIndex = size(rejectedAttachments.value) - 1
  if (lastItemIndex > 0) {
    const nextFocusIndex = (index === lastItemIndex ) ? index - 1 : index
    putFocusNextTick(`remove-${props.idPrefix}-rejected-attachment-${nextFocusIndex}-btn`)
  } else {
    putFocusNextTick(inputId.value)
  }
  rejectedAttachments.value.splice(index, 1)
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
