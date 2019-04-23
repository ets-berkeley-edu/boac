<script>
export default {
  name: 'NoteUtil',
  methods: {
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
