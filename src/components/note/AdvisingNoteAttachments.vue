<template>
  <div>
    <label
      :id="`${idPrefix}-attachments-list-label`"
      class="d-inline-block font-size-16 font-weight-bold text-medium-emphasis"
      :for="`${idPrefix}-attachments-list`"
    >
      Attachments
    </label>
    <div v-if="!isReadOnly" class="mt-2 position-relative">
      <label
        class="note-attachment-inner-label font-size-16 align-center d-flex flex-wrap justify-center"
        :class="{
          'font-weight-bold text-black text-center': disabled,
          'font-weight-medium': !disabled
        }"
        :for="inputId"
      >
        <div v-if="isAdding">
          Adding attachments...
        </div>
        <div v-if="!isAdding" class="mr-2 ">
          Add attachment:
        </div>
        <v-btn
          v-if="!isAdding"
          :id="`${idPrefix}choose-file-for-note-attachment-btn`"
          class="bg-white"
          color="black"
          :disabled="disabled"
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
        v-if="!attachmentLimitReached"
        :id="inputId"
        ref="attachmentFileInput"
        :aria-busy="isAdding"
        :aria-describedby="isAdding ? progressBarId : null"
        :aria-label="`Select file for attachment; ${pluralize('file', attachments.length)} attached.`"
        class="border-sm choose-file-for-note-attachment rounded"
        :class="{'border-success': disabled, 'border-md border-error': !!attachmentError}"
        :clearable="false"
        :disabled="isAdding || disabled"
        flat
        hide-details
        :loading="isAdding ? 'primary' : false"
        :model-value="attachments"
        multiple
        :prepend-icon="null"
        :variant="disabled ? 'outlined' : 'solo-filled'"
        @click:control="onClickBrowseForAttachment"
        @update:model-value="onAttachmentsInput"
      >
        <template #selection>
          <div />
        </template>
      </v-file-input>
    </div>
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
      <v-alert-title class="text-warning-darken-1 font-size-16">A note can have no more than {{ contextStore.config.maxAttachmentsPerNote }} attachments.</v-alert-title>
    </v-alert>
    <ul
      :id="`${idPrefix}attachments-list`"
      :aria-labelledby="`${idPrefix}-attachments-list-label`"
      class="list-no-bullets advising-note-pill-list mt-1"
    >
      <li
        v-for="(attachment, index) in attachments"
        :key="index"
      >
        <PillItem
          :id="`${idPrefix}attachment-${index}`"
          :aria-label="isDownloadable ? `Download attachment ${attachment.displayName}` : null"
          :closable="canRemoveAttachments"
          :disabled="disabled"
          :href="downloadUrl(attachment)"
          :icon="mdiPaperclip"
          :label="attachment.displayName"
          name="attachment"
          @close-clicked="onRemoveAttachment(index)"
        >
          <span class="truncate-with-ellipsis" :class="{'demo-mode-blur': currentUser.inDemoMode, 'text-anchor': isDownloadable}">
            {{ attachment.displayName }}
          </span>
        </PillItem>
      </li>
    </ul>
  </div>
</template>

<script setup>
import {computed, onBeforeMount, onBeforeUnmount, onMounted, reactive, ref, watch} from 'vue'
import {each, size} from 'lodash'
import {mdiAlert, mdiPaperclip} from '@mdi/js'
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
    default: '',
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
  note: {
    required: true,
    type: Object
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
const inputId = `${props.idPrefix}choose-file-for-note-attachment`
const isAdding = ref(false)
let progressBarAlert
const progressBarId = `${props.idPrefix}note-attachment-progress`

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
  if (props.isDownloadable) {
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
    isAdding.value = true
    attachmentError.value = validateAttachment(files, props.attachments)
    if (!attachmentError.value) {
      const attachments = []
      each(files, attachment => {
        attachment.displayName = attachment.name
        attachments.push(attachment)
      })
      props.add(attachments).then(() => {
        alertScreenReader(`${pluralized} added`)
        isAdding.value = false
      })
    } else {
      isAdding.value = false
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
    putFocusNextTick(`remove-${props.idPrefix}attachment-${nextFocusIndex}-btn`)
  } else {
    putFocusNextTick(inputId)
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
