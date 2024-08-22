<template>
  <div>
    <slot name="label"></slot>
    <v-file-input
      v-if="!readOnly"
      :id="`${idPrefix}choose-file-for-note-attachment`"
      ref="attachmentFileInput"
      :model-value="attachments"
      aria-label="Select file for attachment"
      class="border-sm choose-file-for-note-attachment rounded"
      :class="{'border-success': disabled || attachmentLimitReached, 'border-md border-error': !!attachmentError}"
      :clearable="false"
      :disabled="disabled || attachmentLimitReached"
      flat
      hide-details
      :loading="isAdding ? 'success' : false"
      multiple
      :prepend-icon="null"
      single-line
      :variant="disabled || attachmentLimitReached ? 'outlined' : 'solo-filled'"
      @keydown.enter="clickBrowseForAttachment"
      @update:model-value="onAttachmentsInput"
    >
      <template #label>
        <div
          class="font-size-16"
          :class="{
            'font-weight-bold text-black text-center': disabled || attachmentLimitReached,
            'align-center d-flex font-weight-medium justify-center': !disabled && !attachmentLimitReached
          }"
        >
          <div v-if="disabled" class="pb-1">
            Adding attachments...
          </div>
          <div v-if="!disabled" class="mr-2 ">
            Add attachment:
          </div>
          <v-btn
            v-if="!disabled"
            :id="`${idPrefix}choose-file-for-note-attachment-btn`"
            class="bg-white"
            color="black"
            :disabled="disabled"
            density="comfortable"
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
    <div v-if="attachmentLimitReached" class="w-100">
      A note can have no more than {{ contextStore.config.maxAttachmentsPerNote }} attachments.
    </div>
    <ul
      :id="`${idPrefix}attachments-list`"
      aria-label="attachments"
      class="list-no-bullets mt-2"
    >
      <li
        v-for="(attachment, index) in modelProxy.attachments"
        :key="index"
      >
        <v-chip
          :id="`${idPrefix}attachment-${index}`"
          :aria-label="downloadable ? `Download attachment ${attachment.displayName}` : null"
          class="attachment-chip v-chip-content-override font-weight-bold my-1 pa-4 text-medium-emphasis text-no-wrap text-uppercase"
          density="compact"
          :disabled="disabled"
          :href="downloadUrl(attachment)"
          :prepend-icon="mdiPaperclip"
          variant="outlined"
        >
          <span class="truncate-with-ellipsis">{{ attachment.displayName }}</span>
          <template #append>
            <v-btn
              v-if="!readOnly"
              :id="`${idPrefix}remove-attachment-${index}-btn`"
              :aria-label="`Remove attachment ${attachment.displayName}`"
              class="pl-4"
              color="error"
              density="compact"
              :disabled="disabled"
              :icon="mdiCloseCircle"
              size="20px"
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
  visibility: visible !important;
  width: 100%;
}
.choose-file-for-note-attachment input {
  cursor: pointer;
}
</style>
