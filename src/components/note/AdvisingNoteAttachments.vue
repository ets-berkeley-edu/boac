<template>
  <div>
    <div v-if="attachmentError" class="mt-3 mb-3 w-100">
      <v-icon :icon="mdiAlert" class="text-danger pr-1" />
      <span id="attachment-error" aria-live="polite" role="alert">{{ attachmentError }}</span>
    </div>
    <div v-if="_size(existingAttachments) < config.maxAttachmentsPerNote" class="w-100">
      <div class="choose-attachment-file-wrapper h-100 no-wrap pl-3 pr-3 w-100">
        Add attachment:
        <v-btn
          id="choose-file-for-note-attachment"
          :disabled="disabled"
          aria-hidden="true"
          class="btn-file-upload mt-2 mb-2"
          size="sm"
          type="file"
          variant="outlined"
          @keydown.enter.prevent="clickBrowseForAttachment"
        >
          Select File
        </v-btn>
        <v-file-input
          ref="attachment-file-input"
          v-model="attachments"
          aria-label="Select file for attachment"
          density="compact"
          :disabled="disabled || _size(existingAttachments) === config.maxAttachmentsPerNote"
          :error="Boolean(attachments && attachments.length)"
          multiple
          variant="plain"
        ></v-file-input>
      </div>
    </div>
    <div v-if="_size(existingAttachments) >= config.maxAttachmentsPerNote" class="w-100">
      A note can have no more than {{ config.maxAttachmentsPerNote }} attachments.
    </div>
    <div>
      <ul class="pill-list pl-0 mt-3">
        <li
          v-for="(attachment, index) in existingAttachments"
          :id="`new-note-attachment-${index}`"
          :key="index"
          class="mt-1"
        >
          <span class="pill pill-attachment text-nowrap">
            <v-icon :icon="mdiPaperclip" />
            {{ attachment.displayName }}
            <v-btn
              :id="`remove-note-attachment-${index}`"
              class="p-0"
              :disabled="disabled"
              variant="plain"
              @click.prevent="() => deleteAttachmentByIndex(index)"
            >
              <v-icon :icon="mdiCloseCircle" class="font-size-20 has-error pl-2" />
              <span class="sr-only">Delete attachment '{{ attachment.displayName }}'</span>
            </v-btn>
          </span>
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
    attachmentError: undefined
  }),
  watch: {
    attachments(files) {
      if (files) {
        this.attachmentError = validateAttachment(files, this.existingAttachments)
        if (!this.attachmentError) {
          const attachments = []
          this._each(files, attachment => {
            attachment.displayName = attachment.name
            attachments.push(attachment)
          })
          this.addAttachments(attachments)
          this.alertScreenReader('Attachments added')
        }
      }
    }
  },
  beforeCreate() {
    addFileDropEventListeners()
  },
  methods: {
    clickBrowseForAttachment() {
      this.$refs['attachment-file-input'].$el.click()
    },
    deleteAttachmentByIndex(index) {
      this.alertScreenReader(`Attachment '${this.existingAttachments[index].name}' removed`)
      useNoteStore().removeAttachmentByIndex(index)
    }
  }
}
</script>
