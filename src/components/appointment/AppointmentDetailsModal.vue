<template>
  <b-modal
    id="appointment-check-in"
    v-model="showDetailsModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="close"
    @hide.prevent="close">
    <div>
      <div class="ml-3 modal-header">
        <h3 id="appointment-check-in-student" :class="{'demo-mode-blur' : user.inDemoMode}">{{ student.name }}</h3>
      </div>
      <div class="modal-body w-100">
        <b-container fluid>
          <b-row v-if="appointment.topics.length">
            <b-col class="font-weight-bolder" cols="3">
              <label for="appointment-topics">
                Reason
              </label>
            </b-col>
            <b-col id="appointment-topics">
              {{ oxfordJoin(appointment.topics) }}
            </b-col>
          </b-row>
          <b-row class="mt-2">
            <b-col cols="3">
              <label class="font-weight-bolder text-nowrap" for="appointment-created-at">
                Arrival Time
              </label>
            </b-col>
            <b-col id="appointment-created-at">
              {{ new Date(appointment.createdAt) | moment('LT') }}
            </b-col>
          </b-row>
          <b-row>
            <b-col class="font-weight-bolder" cols="3">
              <label for="appointment-details">
                Details
              </label>
            </b-col>
            <b-col>
              <span id="appointment-details" v-html="appointment.details"></span>
            </b-col>
          </b-row>
        </b-container>
      </div>
      <div class="modal-footer">
        <b-btn
          v-if="!user.isAdmin"
          id="btn-appointment-details-check-in"
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
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import UserMetadata from '@/mixins/UserMetadata';

export default {
  name: 'AppointmentDetailsModal',
  mixins: [Context, UserMetadata, Util],
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
    this.alertScreenReader(`Opened appointment details of student ${this.student.name}`);
    this.putFocusNextTick('appointment-check-in-student');
  }
}
</script>

<style scoped>
.appointment-details-label {
  min-width: 25%;
}
</style>
