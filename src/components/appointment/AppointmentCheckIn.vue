<template>
  <b-modal
    id="advising-appointment-check-in"
    v-model="showCheckInModal"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    :no-close-on-backdrop="true"
    @cancel.prevent="functionCancel"
    @hide.prevent="functionCancel"
    @shown="putFocusNextTick('are-you-sure-confirm')">
    <div>
      <div class="modal-header">
        <h3>{{ modalHeader }}</h3>
      </div>
      <div class="modal-body">
        <div>
          <div class="d-flex">
            <div>
              Reason
            </div>
            <div>
              {{ appointment.reason }}
            </div>
          </div>
          <div class="d-flex">
            <div>
              Arrival Time
            </div>
            <div>
              {{ appointment.arrivalTime }}
            </div>
          </div>
          <div class="d-flex">
            <div>
              Details
            </div>
            <div>
              {{ appointment.details }}
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <form @submit.prevent="functionConfirm">
          <b-btn
            id="btn-appointment-check-in"
            class="btn-primary-color-override"
            variant="primary"
            :aria-label="modalHeader"
            @click.prevent="functionConfirm">
            Check In
          </b-btn>
          <b-btn
            id="btn-appointment-cancel"
            class="pl-2"
            variant="link"
            @click.stop="functionCancel">
            Close
          </b-btn>
        </form>
      </div>
    </div>
  </b-modal>
</template>

<script>
import Util from '@/mixins/Util';

export default {
  name: 'AppointmentCheckIn',
  mixins: [Util],
  props: {
    appointment: {
      type: Object,
      required: true
    },
    functionCancel: {
      type: Function,
      required: true
    },
    functionConfirm: {
      type: Function,
      required: true
    },
    modalHeader: {
      type: String,
      required: true
    },
    showModal: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    showCheckInModal: false
  }),
  watch: {
    showModal(value) {
      this.showCheckInModal = value;
    }
  },
  created() {
    this.showCheckInModal = this.showModal;
  }
}
</script>
