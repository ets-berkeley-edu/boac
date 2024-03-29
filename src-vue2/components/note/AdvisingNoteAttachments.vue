<template>
  <div>
    <div v-if="attachmentError" class="mt-3 mb-3 w-100">
      <font-awesome icon="exclamation-triangle" class="text-danger pr-1" />
      <span id="attachment-error" aria-live="polite" role="alert">{{ attachmentError }}</span>
    </div>
    <div v-if="_size(existingAttachments) < config.maxAttachmentsPerNote" class="w-100">
      <div class="choose-attachment-file-wrapper h-100 no-wrap pl-3 pr-3 w-100">
        Add attachment:
        <b-btn
          id="choose-file-for-note-attachment"
          :disabled="disabled"
          type="file"
          aria-hidden="true"
          variant="outline-primary"
          class="btn-file-upload mt-2 mb-2"
          size="sm"
          @keydown.enter.prevent="clickBrowseForAttachment"
        >
          Select File
        </b-btn>
        <b-form-file
          ref="attachment-file-input"
          v-model="attachments"
          aria-label="Select file for attachment"
          :disabled="disabled || _size(existingAttachments) === config.maxAttachmentsPerNote"
          :multiple="true"
          :plain="true"
          :state="Boolean(attachments && attachments.length)"
        />
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
            <font-awesome icon="paperclip" />
            {{ attachment.displayName }}
            <b-btn
              :id="`remove-note-attachment-${index}`"
              :disabled="disabled"
              variant="link"
              class="p-0"
              @click.prevent="() => deleteAttachmentByIndex(index)"
            >
              <font-awesome icon="times-circle" class="font-size-20 has-error pl-2" />
              <span class="sr-only">Delete attachment '{{ attachment.displayName }}'</span>
            </b-btn>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {removeAttachmentByIndex} from '@/store/modules/note-edit-session/utils'
import {addFileDropEventListeners, validateAttachment} from '@/lib/note'

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
      removeAttachmentByIndex(index)
    }
  }
}
</script>
