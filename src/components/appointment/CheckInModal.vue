<template>
  <b-modal
    id="advising-appointment-check-in"
    v-model="showCheckInModal"
    :no-close-on-backdrop="true"
    @cancel.prevent="close"
    @hide.prevent="close"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header>
    <div>
      <div class="modal-header">
        <h3>Check In - {{ appointment.student.name }}</h3>
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
        <label for="checkin-modal-advisor-select">
          Select a drop-in advisor:
        </label>
        <b-form-select
          id="checkin-modal-advisor-select"
          v-model="selectedAdvisorUid"
          :options="dropInAdvisors"
          value-field="uid"
          text-field="name">
          <template v-slot:first>
            <option :value="null" disabled>Select...</option>
          </template>
        </b-form-select>
      </div>
      <div class="modal-footer">
        <form @submit.prevent="checkIn">
          <b-btn
            id="btn-appointment-check-in"
            :aria-label="`Check in ${appointment.student.name}`"
            @click.prevent="checkIn"
            class="btn-primary-color-override"
            variant="primary">
            Check In
          </b-btn>
          <b-btn
            id="btn-appointment-close"
            @click.stop="close"
            class="pl-2"
            variant="link">
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
import { getDropInAdvisorsForDept } from '@/api/user';

export default {
  name: 'CheckInModal',
  mixins: [Context, Util],
  props: {
    appointment: {
      type: Object,
      required: true
    },
    appointmentCheckin: {
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
    }
  },
  data: () => ({
    dropInAdvisors: [],
    reason: undefined,
    reasonExplained: undefined,
    selectedAdvisorUid: null,
    showCheckInModal: false
  }),
  watch: {
    showModal(value) {
      this.showCheckInModal = value;
    }
  },
  created() {
    this.showCheckInModal = this.showModal;
    getDropInAdvisorsForDept(this.appointment.deptCode).then(dropInAdvisors => {
      this.dropInAdvisors = dropInAdvisors;
    });
  },
  methods: {
    checkIn() {
      const advisor = this.find(this.dropInAdvisors, {'uid': this.selectedAdvisorUid});
      if (advisor) {
        const deptCodes = Object.keys(advisor.departments);
        this.appointmentCheckin(advisor, deptCodes);
        this.alertScreenReader(`Checked in ${this.appointment.student.name}`);
        this.showCheckInModal = false;
      }
    }
  }
}
</script>

<style scoped>
.appointment-details-label {
  min-width: 25%;
}
</style>
