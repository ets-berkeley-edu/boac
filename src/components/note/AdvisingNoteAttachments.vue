<template>
  <div>
    <div v-if="attachmentError" class="mt-3 mb-3 w-100">
      <font-awesome icon="exclamation-triangle" class="text-danger pr-1" />
      <span id="attachment-error" aria-live="polite" role="alert">{{ attachmentError }}</span>
    </div>
    <div v-if="size(existingAttachments) < $config.maxAttachmentsPerNote" class="w-100">
      <div class="choose-attachment-file-wrapper h-100 no-wrap pl-3 pr-3 w-100">
        Add attachment:
        <b-btn
          id="choose-file-for-note-attachment"
          :disabled="disabled"
          type="file"
          variant="outline-primary"
          class="btn-file-upload mt-2 mb-2"
          size="sm"
          @keydown.enter.prevent="clickBrowseForAttachment">
          Select File
        </b-btn>
        <b-form-file
          ref="attachmentFileInput"
          v-model="attachment"
          :disabled="disabled || size(existingAttachments) === $config.maxAttachmentsPerNote"
          :state="Boolean(attachment)"
          :plain="true"
        ></b-form-file>
      </div>
    </div>
    <div v-if="size(existingAttachments) === $config.maxAttachmentsPerNote" class="w-100">
      A note can have no more than {{ $config.maxAttachmentsPerNote }} attachments.
    </div>
    <div>
      <ul class="pill-list pl-0 mt-3">
        <li
          v-for="(attachment, index) in existingAttachments"
          :id="`new-note-attachment-${index}`"
          :key="attachment.name"
          class="mt-2">
          <span class="pill pill-attachment text-nowrap">
            <font-awesome icon="paperclip" />
            {{ attachment.displayName }}
            <b-btn
              :id="`remove-note-attachment-${index}`"
              :disabled="disabled"
              variant="link"
              class="p-0"
              @click.prevent="removeAttachmentByIndex(index)">
              <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
              <span class="sr-only">Delete attachment '{{ attachment.displayName }}'</span>
            </b-btn>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import Attachments from '@/mixins/Attachments';
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingNoteAttachments',
  mixins: [Attachments, Context, Util],
  props: {
    addAttachment: {
      required: true,
      type: Function
    },
    disabled: {
      default: false,
      required: false,
      type: Boolean
    },
    existingAttachments: {
      required: true,
      type: Array
    },
    removeAttachment: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    attachment: undefined,
    attachmentError: undefined
  }),
  watch: {
    attachment(file) {
      if (file) {
        this.attachmentError = this.validateAttachment(file, this.existingAttachments);
        if (this.attachmentError) {
          this.attachment = null;
        } else {
          this.attachmentError = null;
          this.attachment = file;
          this.attachment.displayName = file.name;
          this.addAttachment(this.attachment);
          this.alertScreenReader(`Attachment '${this.attachment.displayName}' added`);
        }
      }
      this.$refs.attachmentFileInput.reset();
    }
  },
  methods: {
    removeAttachmentByIndex(index) {
      this.alertScreenReader(`Attachment '${this.existingAttachments[index].name}' removed`);
      this.removeAttachment(index);
    }
  }
}
</script>
