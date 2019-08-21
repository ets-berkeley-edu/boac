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
    validateAttachment(attachment, attachments) {
      const maxAttachmentMegabytes = 20;
      const maxAttachmentBytes = maxAttachmentMegabytes * 1024 * 1024;
      let error = null;
      if (attachment) {
        const name = attachment.name;
        if (attachment.size > maxAttachmentBytes) {
          error = `The file '${name}' is too large. Attachments are limited to ${maxAttachmentMegabytes} MB in size.`;
        } else {
          const matching = _.filter(attachments, a => name === a.displayName);
          if (matching.length) {
            error = `Another attachment has the name '${name}'. Please rename your file.`;
          }
        }
      } else {
        error = 'No attachment provided.';
      }
      return error;
    }
  }
}
</script>
