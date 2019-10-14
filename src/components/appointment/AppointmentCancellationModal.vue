<template>
  <b-modal
    id="advising-appointment-check-in"
    v-model="showCancellationModal"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    :no-close-on-backdrop="true"
    @cancel.prevent="close"
    @hide.prevent="close"
    @shown="putFocusNextTick('are-you-sure-confirm')">
    <div>
      <div class="modal-header">
        <h3>{{ student.name }}</h3>
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
        <form @submit.prevent="appointmentCancellation">
          <b-btn
            id="btn-appointment-check-in"
            class="btn-primary-color-override"
            variant="primary"
            :aria-label="`Cancel appointment with ${student.name}`"
            @click.prevent="appointmentCancellation">
            Cancel Appointment
          </b-btn>
          <b-btn
            id="btn-appointment-cancel"
            class="pl-2"
            variant="link"
            @click.stop="close">
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
  name: 'AppointmentCancellationModal',
  mixins: [Util],
  props: {
    appointment: {
      type: Object,
      required: true
    },
    appointmentCancellation: {
      type: Function,
      required: true
    },
    close: {
      type: Function,
      required: true
    },
    showModal: {
      type: Boolean,
      required: true
    },
    student: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    showCancellationModal: false
  }),
  watch: {
    showModal(value) {
      this.showCancellationModal = value;
    }
  },
  created() {
    this.showCancellationModal = this.showModal;
  }
}
</script>
