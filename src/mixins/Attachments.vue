<script>
import _ from 'lodash';

export default {
  name: 'Attachments',
  beforeCreate() {
    const preventFileDropOutsideFormControl = e => {
      if (!e.target.classList.contains('choose-attachment-file-wrapper')) {
        e.preventDefault();
        e.dataTransfer.effectAllowed = 'none';
        e.dataTransfer.dropEffect = 'none';
      }
    };
    window.addEventListener('dragenter', preventFileDropOutsideFormControl, false);
    window.addEventListener('dragover', preventFileDropOutsideFormControl);
    window.addEventListener('drop', preventFileDropOutsideFormControl);
  },
  methods: {
    clickBrowseForAttachment() {
      this.$refs['attachment-file-input'].$el.click();
    },
    validateAttachment(attachments, existingAttachments) {
      const maxAttachmentMegabytes = 20;
      const maxAttachmentBytes = maxAttachmentMegabytes * 1024 * 1024;
      if (!(attachments && attachments.length)) {
        return 'No attachment provided.';
      }
      if (_.size(attachments) + _.size(existingAttachments) > parseInt(this.$config.maxAttachmentsPerNote)) {
        return `A note can have no more than ${this.$config.maxAttachmentsPerNote} attachments.`;
      }
      let error = null;
      for (const attachment of attachments) {
        if (attachment.size > maxAttachmentBytes) {
          error = `The file '${attachment.name}' is too large. Attachments are limited to ${maxAttachmentMegabytes} MB in size.`;
          break;
        }
        const matching = _.filter(existingAttachments, a => attachment.name === a.displayName);
        if (matching.length) {
          error = `Another attachment has the name '${attachment.name}'. Please rename your file.`;
          break;
        }
      }
      return error;
    }
  }
}
</script>
