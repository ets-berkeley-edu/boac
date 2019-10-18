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
        <h3>Cancel Appointment</h3>
      </div>
      <div class="modal-body w-100">
        <div class="mr-3">
          <div class="d-flex">
            <div class="appointment-details-label font-weight-bolder w-25">
              <label for="appointment-topics">
                Date
              </label>
            </div>
            <div>
              <span id="appointment-created-at">
                {{ new Date(appointment.createdAt) | moment('ddd, MMMM D') }}
              </span>
            </div>
          </div>
          <div class="d-flex">
            <div class="appointment-details-label font-weight-bolder w-25">
              <label for="appointment-topics">
                Arrival Time
              </label>
            </div>
            <div>
              <span id="appointment-created-at">
                {{ new Date(appointment.createdAt) | moment('LT') }}
              </span>
            </div>
          </div>
          <div class="d-flex">
            <div class="appointment-details-label font-weight-bolder w-25">
              <label for="appointment-name">
                Student
              </label>
            </div>
            <div>
              <span id="appointment-name" v-html="appointment.student.name"></span>
            </div>
          </div>
        </div>
        <hr>
        <div class="mb-3">
          <label for="cancellation-reason">
            <span class="font-weight-bolder">Cancellation Reason</span> (required)
          </label>
          <b-form-select
            id="cancellation-reason"
            v-model="reason"
            :options="reasonOptions">
          </b-form-select>
        </div>
        <div>
          <label for="cancellation-reason-explained">
            <span class="font-weight-bolder">Additional Information</span>
          </label>
          <b-form-textarea
            id="cancellation-reason-explained"
            v-model="reasonExplained"
            rows="4">
          </b-form-textarea>
        </div>
      </div>
      <div class="modal-footer">
        <form @submit.prevent="cancelTheAppointment">
          <b-btn
            id="btn-appointment-cancel"
            class="btn-primary-color-override"
            variant="primary"
            :disabled="!reason"
            :aria-label="`Cancel appointment with ${student.name}`"
            @click.prevent="cancelTheAppointment">
            Cancel Appointment
          </b-btn>
          <b-btn
            id="btn-appointment-close"
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
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';

export default {
  name: 'AppointmentCancellationModal',
  mixins: [Context, Util],
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
    reason: undefined,
    reasonExplained: undefined,
    reasonOptions: [
      { value: null, text: 'Choose one...' },
      { value: 'Canceled by student', text: 'Canceled by student' },
      { value: 'Canceled by department/advisor', text: 'Canceled by department/advisor' },
    ],
    showCancellationModal: false
  }),
  watch: {
    showModal(value) {
      this.showCancellationModal = value;
    }
  },
  created() {
    this.showCancellationModal = this.showModal;
  },
  methods: {
    cancelTheAppointment() {
      this.appointmentCancellation(this.appointment.id, this.reason, this.reasonExplained);
      this.alertScreenReader(`Appointment with ${this.student.name} canceled`);
      this.showCancellationModal = false;
    }
  }
}
</script>

<style scoped>
.appointment-details-label {
  min-width: 25%;
}
</style>
