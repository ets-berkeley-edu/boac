<template>
  <b-modal
    v-if="selfCheckIn || !isNil(dropInAdvisors)"
    id="advising-appointment-check-in"
    v-model="showCheckInModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="close"
    @hide.prevent="close">
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
        <div v-if="!selfCheckIn && dropInAdvisors.length" class="pb-3 pt-3">
          <label for="checkin-modal-advisor-select" class="font-weight-bolder">
            Select a drop-in advisor:
          </label>
          <b-form-select
            id="checkin-modal-advisor-select"
            v-model="selectedAdvisorUid"
            :options="dropInAdvisors"
            value-field="uid"
            text-field="name">
            <template v-slot:first>
              <option :value="null">Select...</option>
            </template>
          </b-form-select>
        </div>
        <div v-if="!selfCheckIn && !dropInAdvisors.length" class="has-error pb-1 pt-3">
          Sorry, no advisors are on duty.
        </div>
      </div>
      <div class="modal-footer">
        <form @submit.prevent="checkIn">
          <b-btn
            v-if="selfCheckIn || dropInAdvisors.length"
            id="btn-appointment-check-in"
            :aria-label="`Check in ${appointment.student.name}`"
            :disabled="!selfCheckIn && !selectedAdvisorUid"
            class="btn-primary-color-override"
            variant="primary"
            @click.prevent="checkIn">
            Check In
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
    selfCheckIn: {
      type: Boolean,
      required: true
    },
    showModal: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    dropInAdvisors: undefined,
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
    if (!this.selfCheckIn) {
      getDropInAdvisorsForDept(this.appointment.deptCode).then(dropInAdvisors => {
        this.dropInAdvisors = this.filterList(dropInAdvisors, d => d.status.startsWith('on_duty'));
      });
    }
  },
  methods: {
    checkIn() {
      if (this.selfCheckIn) {
        this.appointmentCheckin();
      } else {
        const advisor = this.find(this.dropInAdvisors, {'uid': this.selectedAdvisorUid});
        if (advisor) {
          const deptCodes = this.map(advisor.departments, 'code');
          this.appointmentCheckin(advisor, deptCodes);
        }
      }
      this.alertScreenReader(`Checked in ${this.appointment.student.name}`);
      this.showCheckInModal = false;
    }
  }
}
</script>

<style scoped>
.appointment-details-label {
  min-width: 25%;
}
</style>
