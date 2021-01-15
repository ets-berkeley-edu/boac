<template>
  <b-modal
    v-model="showUpdateModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="close"
    @hide.prevent="close"
    @shown="putFocusNextTick('modal-header')"
  >
    <div>
      <ModalHeader text="Drop-in Update" />
      <div class="modal-body">
        {{ appointmentUpdate.statusBy.name }} recently updated the status of this drop-in appointment to
        <strong>{{ appointmentUpdate.status.replace('_', ' ') }}</strong>.
      </div>
      <div class="modal-footer">
        <b-btn
          id="btn-update-modal-close"
          class="pl-2"
          variant="primary"
          @click.stop="close"
        >
          Okay
        </b-btn>
      </div>
    </div>
  </b-modal>
</template>

<script>
import Context from '@/mixins/Context'
import ModalHeader from '@/components/util/ModalHeader'
import Util from '@/mixins/Util'

export default {
  name: 'AppointmentUpdateModal',
  mixins: [Context, Util],
  components: {ModalHeader},
  props: {
    appointmentUpdate: {
      type: Object,
      required: true
    },
    close: {
      type: Function,
      required: true
    },
    showModal: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    showUpdateModal: false
  }),
  watch: {
    showModal(value) {
      this.showUpdateModal = value
    }
  },
  created() {
    this.showUpdateModal = this.showModal
    this.alertScreenReader('Drop-in Update')
  }
}
</script>
