<template>
  <div>
    <v-alert
      v-if="attachmentError"
      id="attachment-error"
      aria-live="polite"
      class="font-size-14 w-100 mb-1"
      density="compact"
      :icon="mdiAlert"
      :text="attachmentError"
      type="error"
      variant="tonal"
    ></v-alert>
    <v-file-input
      id="choose-file-for-note-attachment"
      ref="attachment-file-input"
      :model-value="attachments"
      aria-label="Select file for attachment"
      class="choose-file-for-note-attachment border rounded"
      :clearable="false"
      density="comfortable"
      :disabled="disabled || attachmentLimitReached"
      :error="attachmentError"
      flat
      hide-details
      :loading="isAdding ? 'primary' : false"
      multiple
      :prepend-icon="null"
      single-line
      variant="solo-filled"
      @update:model-value="onAttachmentsInput"
    >
      <template #label>
        <div class="d-flex align-center justify-center">
          <div class="font-size-14">
            Add attachment:
          </div>
          <v-btn
            id="choose-file-for-note-attachment-btn"
            :disabled="disabled"
            aria-hidden="true"
            class="my-2 ml-2 px-2"
            density="comfortable"
            hide-details
            type="file"
            variant="outlined"
            @keydown.enter.prevent="clickBrowseForAttachment"
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
      A note can have no more than {{ useContextStore().config.maxAttachmentsPerNote }} attachments.
    </div>
    <div>
      <ul aria-label="attachments" class="list-no-bullets mt-1">
        <li
          v-for="(attachment, index) in useNoteStore().model.attachments"
          :key="index"
        >
          <v-chip
            :id="`new-note-attachment-${index}`"
            class="v-chip-content-override font-weight-bold text-medium-emphasis text-uppercase text-no-wrap mt-1"
            closable
            :close-label="`Remove attachment ${attachment.displayName}`"
            density="comfortable"
            :disabled="disabled"
            :prepend-icon="mdiPaperclip"
            variant="outlined"
            @click:close="deleteAttachmentByIndex(index)"
            @keyup.enter="deleteAttachmentByIndex(index)"
          >
            <span class="truncate-with-ellipsis">{{ attachment.displayName }}</span>
            <template #close>
              <v-icon color="error" :icon="mdiCloseCircle"></v-icon>
            </template>
          </v-chip>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {each, size} from 'lodash'
import {mdiAlert, mdiCloseCircle, mdiPaperclip} from '@mdi/js'
</script>

<script>
import {addFileDropEventListeners, validateAttachment} from '@/lib/note'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

export default {
  name: 'AdvisingNoteAttachments',
  props: {
    addAttachments: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    attachments: [],
    attachmentError: undefined,
    isAdding: false
  }),
  computed: {
    attachmentLimitReached() {
      return size(useNoteStore().model.attachments) >= useContextStore().config.maxAttachmentsPerNote
    },
    disabled() {
      return !!(useNoteStore().isSaving || useNoteStore().boaSessionExpired)
    }
  },
  beforeCreate() {
    addFileDropEventListeners()
  },
  created() {
    this.attachments = useNoteStore().model.attachments
  },
  methods: {
    clickBrowseForAttachment() {
      this.$refs['attachment-file-input'].$el.click()
    },
    deleteAttachmentByIndex(index) {
      useContextStore().alertScreenReader(`Attachment '${useNoteStore().model.attachments[index].name}' removed`)
      useNoteStore().removeAttachmentByIndex(index)
    },
    onAttachmentsInput(files) {
      if (size(files)) {
        this.isAdding = true
        useContextStore().alertScreenReader(`Adding ${files.length} attachments`)
        this.attachmentError = validateAttachment(files, useNoteStore().model.attachments)
        if (!this.attachmentError) {
          const attachments = []
          each(files, attachment => {
            attachment.displayName = attachment.name
            attachments.push(attachment)
          })
          this.addAttachments(attachments).then(() => {
            useContextStore().alertScreenReader('Attachments added')
            this.isAdding = false
          })
        } else {
          this.isAdding = false
        }
      }
    },
    useContextStore,
    useNoteStore
  }
}
</script>

<style>
.choose-file-for-note-attachment .v-label.v-field-label {
  visibility: visible !important;
  width: 100%;
}
.choose-file-for-note-attachment input {
  cursor: pointer;
}
</style>
