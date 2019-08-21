<template>
  <div>
    <div v-if="attachmentError" class="mt-3 mb-3 w-100">
      <font-awesome icon="exclamation-triangle" class="text-danger pr-1" />
      <span id="attachment-error" aria-live="polite" role="alert">{{ attachmentError }}</span>
    </div>
    <div v-if="size(existingAttachments) < maxAttachmentsPerNote" class="w-100">
      <div class="choose-attachment-file-wrapper form-control-file no-wrap pl-3 pr-3 w-100">
        <span class="sr-only">Add attachment to note: </span>
        Drop file to upload attachment or
        <b-btn
          id="choose-file-for-note-attachment"
          type="file"
          variant="outline-primary"
          class="btn-file-upload mt-2 mb-2"
          size="sm"
          @keydown.enter.prevent="clickBrowseForAttachment">
          Browse<span class="sr-only"> for file to upload</span>
        </b-btn>
        <b-form-file
          ref="attachmentFileInput"
          v-model="attachment"
          :disabled="size(existingAttachments) === maxAttachmentsPerNote"
          :state="Boolean(attachment)"
          :plain="true"
        ></b-form-file>
      </div>
    </div>
    <div v-if="size(existingAttachments) === maxAttachmentsPerNote" class="w-100">
      A note can have no more than {{ maxAttachmentsPerNote }} attachments.
    </div>
    <div>
      <ul class="pill-list pl-0 mt-3">
        <li
          v-for="(attachment, index) in existingAttachments"
          :id="`new-note-attachment-${index}`"
          :key="attachment.name"
          class="mt-2">
          <span class="pill pill-attachment text-nowrap">
            <font-awesome icon="paperclip" class="pr-1 pl-1" /> {{ attachment.name }}
            <b-btn
              :id="`remove-note-attachment-${index}`"
              variant="link"
              class="p-0"
              @click.prevent="removeAttachment(index)">
              <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
              <span class="sr-only">Delete attachment {{ attachment.name }}</span>
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
    existingAttachments: {
      required: true,
      type: Array
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
  }
}
</script>

<style scoped>
.btn-file-upload {
  border-color: grey;
  color: grey;
}
.btn-file-upload:hover,
.btn-file-upload:focus,
.btn-file-upload:active
{
  color: #333;
  background-color: #aaa;
}
.choose-attachment-file-wrapper {
  position: relative;
  align-items: center;
  overflow: hidden;
  display: inline-block;
  background-color: #f7f7f7;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  text-align: center;
}
.choose-attachment-file-wrapper input[type=file] {
  font-size: 100px;
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0;
}
.choose-attachment-file-wrapper:hover,
.choose-attachment-file-wrapper:focus,
.choose-attachment-file-wrapper:active
{
  color: #333;
  background-color: #eee;
}
</style>
