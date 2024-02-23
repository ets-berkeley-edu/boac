<template>
  <div>
    <ModalHeader text="FERPA Reminder" />
    <div class="modal-body">
      <FerpaReminder />
    </div>
    <div class="modal-footer">
      <b-btn
        id="ferpa-reminder-confirm"
        class="btn-primary-color-override px-3"
        variant="primary"
        @click="onClickConfirm"
      >
        I understand
      </b-btn>
      <b-btn
        id="ferpa-reminder-cancel"
        class="pl-2"
        variant="link"
        @click="cancel"
      >
        Cancel
      </b-btn>
    </div>
  </div>
</template>

<script>
import FerpaReminder from '@/components/util/FerpaReminder'
import ModalHeader from '@/components/util/ModalHeader'

export default {
  name: 'ExportListModal',
  components: {FerpaReminder, ModalHeader},
  props: {
    cancel: {
      required: true,
      type: Function
    },
    confirm: {
      required: true,
      type: Function
    }
  },
  methods: {
    onClickConfirm() {
      this.confirm()
    }
  }
}
</script>
