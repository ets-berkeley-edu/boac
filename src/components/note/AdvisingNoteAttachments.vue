<template>
  <div>
    <v-alert
      v-if="attachmentError"
      :id="`${idPrefix}attachment-error`"
      aria-live="polite"
      class="font-size-14 w-100 mb-1"
      density="compact"
      :icon="mdiAlert"
      :text="attachmentError"
      type="error"
      variant="tonal"
    />
    <v-file-input
      :id="`${idPrefix}choose-file-for-note-attachment`"
      ref="attachmentFileInput"
      :model-value="attachments"
      aria-label="Select file for attachment"
      class="choose-file-for-note-attachment border rounded"
      :clearable="false"
      density="comfortable"
      :disabled="disabled || attachmentLimitReached"
      :error="!!attachmentError"
      flat
      hide-details
      :loading="isAdding ? 'primary' : false"
      multiple
      :prepend-icon="null"
      single-line
      variant="solo-filled"
      @keydown.enter="clickBrowseForAttachment"
      @update:model-value="onAttachmentsInput"
    >
      <template #label>
        <div class="d-flex align-center justify-center">
          <div class="font-size-14">
            Add attachment:
          </div>
          <v-btn
            :id="`${idPrefix}choose-file-for-note-attachment-btn`"
            :disabled="disabled"
            class="my-2 ml-2 px-2"
            density="comfortable"
            hide-details
            type="file"
            variant="outlined"
            @keydown.enter.stop.prevent="clickBrowseForAttachment"
          >
            Select File
          </v-btn>
        </div>
      </template>
      <template #selection>
        <div></div>
      </template>
    </v-file-input>
    <div v-if="attachmentLimitReached" class="w-100">
      A note can have no more than {{ contextStore.config.maxAttachmentsPerNote }} attachments.
    </div>
    <ul aria-label="attachments" class="list-no-bullets mt-1">
      <li
        v-for="(attachment, index) in modelProxy.attachments"
        :key="index"
      >
        <v-chip
          :id="`${idPrefix}attachment-${index}`"
          :aria-label="downloadable ? `Download attachment ${attachment.displayName}` : null"
          class="attachment-chip v-chip-content-override font-weight-bold text-medium-emphasis text-uppercase text-no-wrap my-1"
          density="compact"
          :disabled="disabled"
          :href="downloadUrl(attachment)"
          :prepend-icon="mdiPaperclip"
          variant="outlined"
        >
          <span class="truncate-with-ellipsis">{{ attachment.displayName }}</span>
          <template #close>
            <v-btn
              :id="`${idPrefix}remove-attachment-${index}-btn`"
              :aria-label="`Remove attachment ${attachment.displayName}`"
              color="error"
              :disabled="disabled"
              exact=""
              :icon="mdiCloseCircle"
              variant="text"
              @click.stop.prevent="removeAttachment(index)"
              @keyup.enter.stop.prevent="removeAttachment(index)"
            />
          </template>
        </v-chip>
      </li>
    </ul>
  </div>
</template>

<script setup>
import {addFileDropEventListeners, validateAttachment} from '@/lib/note'
import {alertScreenReader, pluralize} from '@/lib/utils'
import {computed, onBeforeMount, ref, watch} from 'vue'
import {each, size} from 'lodash'
import {mdiAlert, mdiCloseCircle, mdiPaperclip} from '@mdi/js'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  addAttachments: {
    required: true,
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
  removeAttachment: {
    required: true,
    type: Function
  }
})

const attachmentFileInput = ref(null)
const attachments = ref([])
const attachmentError = ref(undefined)
const contextStore = useContextStore()
const isAdding = ref(false)
const noteStore = useNoteStore()
const {mode, model} = storeToRefs(noteStore)
let modelProxy = props.note ? ref(props.note) : ref(noteStore.model)

const attachmentLimitReached = computed(() => {
  return size(model.value.attachments) >= contextStore.config.maxAttachmentsPerNote
})

watch(mode, () => {
  modelProxy = props.note ? ref(props.note) : ref(noteStore.model)
  init()
})

watch(model, () => {
  modelProxy = props.note ? ref(props.note) : ref(noteStore.model)
  init()
})

const init = () => {
  attachments.value = modelProxy.value.attachments
}

const clickBrowseForAttachment = () => {
  attachmentFileInput.value.click()
}

const downloadUrl = (attachment) => {
  return props.downloadable ? `${contextStore.config.apiBaseUrl}/api/notes/attachment/${attachment.id}` : null
}

const onAttachmentsInput = files => {
  if (size(files)) {
    isAdding.value = true
    const pluralized = pluralize('attachment', files.length)
    alertScreenReader(`Adding ${pluralized}`)
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

onBeforeMount(() => {
  addFileDropEventListeners()
})

init()

</script>

<style scoped>
.attachment-chip {
  max-width: 450px;
}
</style>

<style>
.choose-file-for-note-attachment .v-label.v-field-label {
  top: 2px !important;
  visibility: visible !important;
  width: 100%;
}
.choose-file-for-note-attachment input {
  cursor: pointer;
}
</style>
