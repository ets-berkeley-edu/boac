<template>
  <b-modal
    v-model="showCancellationModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="close"
    @hide.prevent="close"
    @shown="$putFocusNextTick('modal-header')"
  >
    <div>
      <ModalHeader text="Cancel Appointment" />
      <div class="modal-body w-100">
        <div class="mr-3 mt-2">
          <b-container fluid>
            <b-row>
              <b-col cols="3" class="appointment-details-label font-weight-bolder pl-1">
                <label for="appointment-created-at-date">
                  Date
                </label>
              </b-col>
              <b-col>
                <span id="appointment-created-at-date">
                  {{ new Date(appointment.createdAt) | moment('ddd, MMMM D') }}
                </span>
              </b-col>
            </b-row>
            <b-row>
              <b-col cols="3" class="appointment-details-label font-weight-bolder pl-1 text-nowrap">
                <label for="appointment-created-at-time">
                  Arrival Time
                </label>
              </b-col>
              <b-col>
                <span id="appointment-created-at-time">
                  {{ new Date(appointment.createdAt) | moment('LT') }}
                </span>
              </b-col>
            </b-row>
            <b-row>
              <b-col cols="3" class="appointment-details-label font-weight-bolder pl-1">
                <label for="appointment-student">
                  Student
                </label>
              </b-col>
              <b-col>
                <span id="appointment-student" :class="{'demo-mode-blur': $currentUser.inDemoMode}" v-html="appointment.student.name"></span>
              </b-col>
            </b-row>
          </b-container>
        </div>
        <div class="ml-2 mr-3 mt-3">
          <label for="cancellation-reason">
            <span class="font-weight-bolder">Cancellation Reason</span> (required)
          </label>
          <b-form-select
            id="cancellation-reason"
            v-model="reason"
            :options="reasonOptions"
            @input="reasonSelected"
          >
            <template v-slot:first>
              <option :value="undefined">Select...</option>
            </template>
          </b-form-select>
        </div>
        <div class="ml-2 mr-3 mt-3">
          <label for="cancellation-reason-explained">
            <span class="font-weight-bolder">Additional Information</span>
          </label>
          <b-form-textarea
            id="cancellation-reason-explained"
            v-model="reasonExplained"
            rows="4"
          >
          </b-form-textarea>
        </div>
      </div>
      <div class="modal-footer mt-3 pt-4">
        <form @submit.prevent="cancelTheAppointment">
          <b-btn
            id="btn-appointment-cancel"
            :disabled="!reason"
            class="btn-primary-color-override mr-2"
            variant="primary"
            @click.prevent="cancelTheAppointment"
          >
            Cancel Appointment
          </b-btn>
          <b-btn
            id="btn-appointment-close"
            variant="link"
            @click.stop="close"
          >
            Close
          </b-btn>
        </form>
      </div>
    </div>
  </b-modal>
</template>

<script>
import Context from '@/mixins/Context'
import ModalHeader from '@/components/util/ModalHeader'
import Util from '@/mixins/Util'

export default {
  name: 'AppointmentCancellationModal',
  mixins: [Context, Util],
  components: {ModalHeader},
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
      {value: 'Canceled by student', text: 'Canceled by student'},
      {value: 'Canceled by department/advisor', text: 'Canceled by department/advisor'},
    ],
    showCancellationModal: false
  }),
  watch: {
    showModal(value) {
      this.showCancellationModal = value
    }
  },
  created() {
    this.showCancellationModal = this.showModal
    this.$announcer.polite('Cancel appointment modal is open')
  },
  methods: {
    cancelTheAppointment() {
      this.appointmentCancellation(this.appointment.id, this.reason, this.reasonExplained)
      this.$announcer.polite(`Appointment with ${this.student.name} canceled`)
      this.showCancellationModal = false
    },
    reasonSelected() {
      this.$announcer.polite(`Reason '${this.reason}' selected`)
      this.$putFocusNextTick('cancellation-reason-explained')
    }
  }
}
</script>

<style scoped>
.appointment-details-label {
  min-width: 25%;
}
</style>
