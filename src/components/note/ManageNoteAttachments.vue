<template>
  <div>
    <div v-if="attachmentError" class="mt-3 mb-3 w-100">
      <i class="fa fa-exclamation-triangle text-danger pr-1"></i>
      <span aria-live="polite" role="alert">{{ attachmentError }}</span>
    </div>
    <div v-if="size(attachments) <= maxAttachmentsPerNote" class="w-100">
      <label for="choose-file-for-note-attachment" class="sr-only"><span class="sr-only">Note </span>Attachments</label>
      <div class="choose-attachment-file-wrapper no-wrap pl-3 pr-3 w-100">
        Drop file to upload attachment or
        <b-btn
          id="choose-file-for-note-attachment"
          type="file"
          variant="outline-primary"
          class="btn-file-upload mt-2 mb-2"
          size="sm">
          Browse<span class="sr-only"> for file to upload</span>
        </b-btn>
        <b-form-file
          v-model="attachment"
          :disabled="size(attachments) === maxAttachmentsPerNote"
          :state="Boolean(attachment)"
          :plain="true"
        ></b-form-file>
      </div>
    </div>
    <div>
      <ul class="pill-list pl-0">
        <li
          v-for="(attachment, index) in attachments"
          :id="`new-note-attachment-${index}`"
          :key="attachment.name"
          :class="{'mt-2': index === 0}">
          <span class="pill text-nowrap">
            <i class="fas fa-paperclip pr-1 pl-1"></i> {{ attachment.displayName }}
            <b-btn
              :id="`remove-note-attachment-${index}`"
              variant="link"
              class="pr-0 pt-1 pl-0"
              @click.prevent="remove(attachment)">
              <i class="fas fa-times-circle has-error pl-2"></i>
            </b-btn>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';

export default {
  name: 'ManageNoteAttachments',
  mixins: [Context, Util],
  props: {
    attachments: Array,
    clearErrors: Function,
    removeAttachment: Function
  },
  data: () => ({
    attachment: undefined,
    attachmentError: undefined
  }),
  watch: {
    attachment() {
      const name = this.attachment.name;
      const matching = this.filterList(this.attachments, a => name === a.displayName);
      if (this.size(matching)) {
        this.attachmentError = `Another attachment has the name '${name}'. Please rename your file.`;
      } else {
        this.attachment.displayName = name;
        this.clearAllErrors();
        this.attachments.push(this.attachment);
        this.alertScreenReader(`Attachment '${name}' added`);
        if (this.size(this.attachments) === this.maxAttachmentsPerNote) {
          this.attachmentError = `A note can have no more than ${this.maxAttachmentsPerNote} attachments.`;
        } else {
          this.clearAllErrors();
        }
      }
    }
  },
  methods: {
    clearAllErrors() {
      this.attachmentError = null;
      this.clearErrors();
    },
    remove(attachment) {
      this.clearAllErrors();
      this.removeAttachment(attachment);
    }
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
