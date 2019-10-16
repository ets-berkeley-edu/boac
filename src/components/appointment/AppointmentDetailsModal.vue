<template>
  <b-modal
    id="advising-appointment-check-in"
    v-model="showDetailsModal"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    :no-close-on-backdrop="true"
    @cancel.prevent="functionCancel"
    @hide.prevent="functionCancel"
    @shown="putFocusNextTick('are-you-sure-confirm')">
    <div>
      <div class="modal-header">
        <h3>{{ student.name }}</h3>
      </div>
      <div class="modal-body w-100">
        <div class="mr-3">
          <div class="d-flex">
            <div class="font-weight-bolder w-25">
              <label for="appointment-topics">
                Reason
              </label>
            </div>
            <div>
              <span id="appointment-topics">
                {{ oxfordJoin(appointment.topics) }}
              </span>
            </div>
          </div>
          <div class="d-flex">
            <div class="font-weight-bolder w-25">
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
              <label for="appointment-details">
                Details
              </label>
            </div>
            <div>
              <span id="appointment-details" v-html="appointment.details"></span>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <b-btn
          id="btn-appointment-check-in"
          class="pl-2"
          variant="primary"
          @click.stop="checkIn">
          Check In
        </b-btn>
        <b-btn
          id="btn-appointment-cancel"
          class="pl-2"
          variant="link"
          @click.stop="close">
          Close
        </b-btn>
      </div>
    </div>
  </b-modal>
</template>

<script>
import Util from '@/mixins/Util';

export default {
  name: 'AppointmentDetailsModal',
  mixins: [Util],
  props: {
    appointment: {
      type: Object,
      required: true
    },
    checkIn: {
      type: Function,
      required: false
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
    showDetailsModal: false
  }),
  watch: {
    showModal(value) {
      this.showDetailsModal = value;
    }
  },
  created() {
    this.showDetailsModal = this.showModal;
  }
}
</script>

<style scoped>
.appointment-details-label {
  min-width: 25%;
}
</style>
