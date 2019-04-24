<script>
export default {
  name: 'NoteUtil',
  created() {
    this.maxAttachmentMegabytes = 20;
    this.maxAttachmentBytes = this.maxAttachmentMegabytes * 1024 * 1024;
  },
  methods: {
    onAttachmentSubmitted() {
      if (!this.attachment) {
        return;
      }
      const name = this.attachment.name;
      if (this.attachment.size > this.maxAttachmentBytes) {
        this.attachmentError = `The file '${name}' is too large. Attachments are limited to ${this.maxAttachmentMegabytes} MB in size.`;
        return;
      }
      const matching = this.filterList(this.attachments, a => name === a.displayName);
      if (this.size(matching)) {
        this.attachmentError = `Another attachment has the name '${name}'. Please rename your file.`;
        return;
      }
      this.attachment.displayName = name;
      this.clearErrors();
      this.attachments.push(this.attachment);
      this.alertScreenReader(`Attachment '${name}' added`);
    },
    initFileDropPrevention() {
      window.addEventListener('dragenter', this.preventFileDropOutsideFormControl, false);
      window.addEventListener('dragover', this.preventFileDropOutsideFormControl);
      window.addEventListener('drop', this.preventFileDropOutsideFormControl);
    },
    preventFileDropOutsideFormControl(e) {
      if (!e.target.classList.contains('form-control-file')) {
        e.preventDefault();
        e.dataTransfer.effectAllowed = 'none';
        e.dataTransfer.dropEffect = 'none';
      }
    }
  }
}
</script>
