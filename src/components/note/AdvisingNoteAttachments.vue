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
      v-if="_size(existingAttachments) < useContextStore().config.maxAttachmentsPerNote"
      id="choose-file-for-note-attachment"
      ref="attachment-file-input"
      v-model="attachments"
      aria-label="Select file for attachment"
      class="choose-file-for-note-attachment border rounded"
      :clearable="false"
      density="comfortable"
      :disabled="disabled || _size(existingAttachments) === useContextStore().config.maxAttachmentsPerNote"
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
    <div v-if="_size(existingAttachments) >= useContextStore().config.maxAttachmentsPerNote" class="w-100">
      A note can have no more than {{ useContextStore().config.maxAttachmentsPerNote }} attachments.
    </div>
    <div>
      <ul aria-label="attachments" class="list-no-bullets mt-1">
        <li
          v-for="(attachment, index) in existingAttachments"
          :key="index"
        >
          <v-chip
            :id="`new-note-attachment-${index}`"
            class="v-chip-content-override font-weight-bold text-medium-emphasis text-uppercase text-nowrap mt-1"
            closable
            :close-label="`Remove attachment ${attachment.displayName}`"
            density="comfortable"
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
import {mdiAlert, mdiCloseCircle, mdiPaperclip} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {addFileDropEventListeners, validateAttachment} from '@/lib/note'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

export default {
  name: 'AdvisingNoteAttachments',
  mixins: [Context, Util],
  props: {
    addAttachments: {
      required: true,
      type: Function
    },
    disabled: {
      required: false,
      type: Boolean
    },
    existingAttachments: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    attachments: [],
    attachmentError: undefined,
    isAdding: false
  }),
  beforeCreate() {
    addFileDropEventListeners()
  },
  created() {
    this.attachments = this.existingAttachments
  },
  methods: {
    clickBrowseForAttachment() {
      this.$refs['attachment-file-input'].$el.click()
    },
    deleteAttachmentByIndex(index) {
      this.alertScreenReader(`Attachment '${this.existingAttachments[index].name}' removed`)
      useNoteStore().removeAttachmentByIndex(index)
    },
    onAttachmentsInput(files) {
      if (this._size(files)) {
        this.isAdding = true
        this.alertScreenReader(`Adding ${files.length} attachments`)
        this.attachmentError = validateAttachment(files, this.existingAttachments)
        if (!this.attachmentError) {
          const attachments = []
          this._each(files, attachment => {
            attachment.displayName = attachment.name
            attachments.push(attachment)
          })
          this.addAttachments(attachments).then(() => {
            this.alertScreenReader('Attachments added')
            this.isAdding = false
          })
        } else {
          this.isAdding = false
        }
      }
    }
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
