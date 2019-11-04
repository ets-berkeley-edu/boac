<template>
  <div>
    <AppointmentCancellationModal
      v-if="showCancelAppointmentModal"
      :appointment="appointment"
      :appointment-cancellation="appointmentCancellation"
      :close="closeAppointmentCancellationModal"
      :show-modal="showCancelAppointmentModal"
      :student="appointment.student" />
    <AppointmentDetailsModal
      v-if="showAppointmentDetailsModal"
      :appointment="appointment"
      :close="closeAppointmentDetailsModal"
      :check-in="launchCheckIn"
      :show-modal="showAppointmentDetailsModal"
      :student="appointment.student" />
    <CheckInModal
      v-if="showCheckInModal"
      :appointment="appointment"
      :appointment-checkin="checkInAppointment"
      :close="closeCheckInModal"
      :show-modal="showCheckInModal" />
    <b-dropdown
      v-if="includes(['reserved', 'waiting'], appointment.status)"
      :id="`appointment-${appointment.id}-dropdown`"
      :disabled="appointment.status === 'checked_in' || appointment.status === 'canceled'"
      @click="launchCheckInForAppointment(appointment)"
      class="bg-white float-right text-nowrap"
      right
      split
      text="Check In"
      variant="outline-dark">
      <b-dropdown-item-button :id="`btn-appointment-${appointment.id}-details`" @click="showAppointmentDetails(appointment)">
        Details
      </b-dropdown-item-button>
      <b-dropdown-item-button
        v-if="isUserDropInAdvisor(deptCode) && (appointment.status !== 'reserved' || appointment.statusBy.id !== user.id)"
        :id="`btn-appointment-${appointment.id}-reserve`"
        @click="reserveAppointment(appointment)">
        <span class="text-nowrap">Reserve</span>
      </b-dropdown-item-button>
      <b-dropdown-item-button
        v-if="appointment.status === 'reserved' && appointment.statusBy.id === user.id"
        :id="`btn-appointment-${appointment.id}-unreserve`"
        @click="unreserveAppointment(appointment)">
        <span class="text-nowrap">Unreserve</span>
      </b-dropdown-item-button>
      <b-dropdown-item-button
        :id="`btn-appointment-${appointment.id}-cancel`"
        @click="openCancelAppointmentModal(appointment)">
        <span aria-hidden="true" class="text-nowrap">Cancel Appt</span>
        <span class="sr-only">Cancel Appointment</span>
      </b-dropdown-item-button>
    </b-dropdown>
  </div>
</template>

<script>
import AppointmentDetailsModal from '@/components/appointment/AppointmentDetailsModal';
import AppointmentCancellationModal from '@/components/appointment/AppointmentCancellationModal';
import CheckInModal from '@/components/appointment/CheckInModal';
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import {
  cancel as apiCancel,
  checkIn as apiCheckIn,
  reserve as apiReserve,
  unreserve as apiUnreserve,
} from '@/api/appointments';

export default {
  name: 'DropInAppointmentDropdown',
  components: {
    AppointmentCancellationModal,
    AppointmentDetailsModal,
    CheckInModal
  },
  mixins: [Context, UserMetadata, Util],
  props: {
    appointment: {
      type: Object,
      required: true
    },
    deptCode: {
      type: String,
      required: true
    },
    isHomepage: {
      type: Boolean,
      required: true
    },
    onAppointmentStatusChange: {
      type: Function,
      required: true
    },
    setSelectedAppointment: {
      type: Function,
      required: true
    },
    waitlist: {
      type: Array,
      required: true
    }
  },
  data: () => ({
    showAppointmentDetailsModal: false,
    showCancelAppointmentModal: false,
    showCheckInModal: false,
    showCreateAppointmentModal: false
  }),
  methods: {
    appointmentCancellation(appointmentId, reason, reasonExplained) {
      apiCancel(this.appointment.id, reason, reasonExplained).then(canceled => {
        if (this.isHomepage) {
          let match = this.waitlist.find(a => a.id === +canceled.id);
          Object.assign(match, canceled);
        } else {
          const indexOf = this.waitlist.findIndex(a => a.id === canceled.id);
          this.waitlist.splice(indexOf, 1);
        }
        this.alertScreenReader(`${canceled.student.name} appointment canceled`);
        this.setSelectedAppointment(undefined);
        this.onAppointmentStatusChange();
      });
    },
    checkInAppointment(advisor, deptCodes) {
      if (!advisor) {
        advisor = this.user;
        deptCodes = this.map(this.user.departments, 'code');
      }
      const appointmentId = this.appointment.id;
      apiCheckIn(
        deptCodes,
        advisor.name,
        advisor.title,
        advisor.uid,
        appointmentId
      ).then(checkedIn => {
        this.onAppointmentStatusChange();
        this.alertScreenReader(`${checkedIn.student.name} checked in`);
        this.closeCheckInModal();
      });
    },
    closeAppointmentCancellationModal() {
      this.showCancelAppointmentModal = false;
      this.putFocusNextTick(`waitlist-student-${this.appointment.student.sid}`);
      this.alertScreenReader('Dialog closed');
      this.setSelectedAppointment(undefined);
    },
    closeAppointmentDetailsModal() {
      this.showAppointmentDetailsModal = false;
      this.putFocusNextTick(`waitlist-student-${this.appointment.student.sid}`);
      this.alertScreenReader(`Dialog closed`);
      this.setSelectedAppointment(undefined);
    },
    closeCheckInModal() {
      this.showCheckInModal = false;
      this.showAppointmentDetailsModal = false;
      this.setSelectedAppointment(undefined);
    },
    launchCheckIn() {
      if (this.isHomepage) {
        this.checkInAppointment();
      } else {
        this.showCheckInModal = true;
      }
    },
    launchCheckInForAppointment(appointment) {
      this.setSelectedAppointment(appointment);
      this.launchCheckIn();
    },
    openCancelAppointmentModal(appointment) {
      this.setSelectedAppointment(appointment);
      this.showCancelAppointmentModal = true;
    },
    reserveAppointment(appointment) {
      apiReserve(appointment.id).then(reserved => {
        let match = this.waitlist.find(a => a.id === +reserved.id);
        Object.assign(match, reserved);
        this.onAppointmentStatusChange();
        this.alertScreenReader(`${reserved.student.name} appointment reserved`);
      });
    },
    showAppointmentDetails(appointment) {
      this.setSelectedAppointment(appointment);
      this.showAppointmentDetailsModal = true;
    },
    unreserveAppointment(appointment) {
      apiUnreserve(appointment.id).then(unreserved => {
        let match = this.waitlist.find(a => a.id === +unreserved.id);
        Object.assign(match, unreserved);
        this.onAppointmentStatusChange();
        this.alertScreenReader(`${unreserved.student.name} appointment unreserved`);
      });
    }
  }
}
</script>
