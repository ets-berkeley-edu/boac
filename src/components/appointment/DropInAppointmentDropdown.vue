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
    <AppointmentUpdateModal
      v-if="showUpdateModal"
      :appointment-update="appointmentUpdate"
      :close="closeUpdateModal"
      :show-modal="showUpdateModal" />
    <div v-if="!loading && includes(['reserved', 'waiting'], appointment.status)">
      <div v-if="user.isAdmin">
        <b-dropdown
          :id="`appointment-${appointment.id}-dropdown`"
          @click="showAppointmentDetails(appointment)"
          class="bg-white float-right text-nowrap"
          right
          split
          text="Details"
          variant="outline-dark">
          <b-dropdown-item-button
            :id="`btn-appointment-${appointment.id}-cancel`"
            @click="openCancelAppointmentModal(appointment)">
            <span aria-hidden="true" class="text-nowrap">Cancel Appt</span>
            <span class="sr-only">Cancel Appointment</span>
          </b-dropdown-item-button>
        </b-dropdown>
      </div>
      <div v-if="!user.isAdmin">
        <b-dropdown
          :id="`appointment-${appointment.id}-dropdown`"
          :disabled="appointment.status === 'checked_in' || appointment.status === 'canceled'"
          @click="launchCheckInForAppointment(appointment)"
          class="bg-white float-right text-nowrap"
          right
          split
          text="Check In"
          variant="outline-dark">
          <b-dropdown-item-button
            v-if="includeDetailsOption"
            :id="`btn-appointment-${appointment.id}-details`"
            @click="showAppointmentDetails(appointment)">
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
    </div>
    <div v-if="loading" :id="`appointment-${appointment.id}-dropdown-spinner`" class="float-right pr-3">
      <font-awesome icon="spinner" spin />
    </div>
  </div>
</template>

<script>
import AppointmentCancellationModal from '@/components/appointment/AppointmentCancellationModal';
import AppointmentDetailsModal from '@/components/appointment/AppointmentDetailsModal';
import AppointmentUpdateModal from '@/components/appointment/AppointmentUpdateModal';
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
    AppointmentUpdateModal,
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
    onAppointmentStatusChange: {
      type: Function,
      required: true
    },
    selfCheckIn: {
      type: Boolean,
      required: true
    },
    setSelectedAppointment: {
      default: () => {},
      type: Function,
      required: false
    },
    includeDetailsOption: {
      default: true,
      type: Boolean,
      required: false
    }
  },
  data: () => ({
    appointmentUpdate: null,
    loading: false,
    showAppointmentDetailsModal: false,
    showCancelAppointmentModal: false,
    showCheckInModal: false,
    showCreateAppointmentModal: false,
    showUpdateModal: false
  }),
  methods: {
    appointmentCancellation(appointmentId, reason, reasonExplained) {
      this.loading = true;
      apiCancel(this.appointment.id, reason, reasonExplained).then(canceled => {
        this.setSelectedAppointment(undefined);
        this.onAppointmentStatusChange(this.appointment.id).then(() => {
          this.loading = false;
          this.alertScreenReader(`${canceled.student.name} appointment canceled`);
        });
      }).catch(this.handleBadRequestError);
    },
    checkInAppointment(advisor, deptCodes) {
      if (!advisor) {
        advisor = this.user;
        deptCodes = this.map(this.user.departments, 'code');
      }
      const appointmentId = this.appointment.id;
      this.loading = true;
      apiCheckIn(
        deptCodes,
        advisor.name,
        advisor.title,
        advisor.uid,
        appointmentId
      ).then(checkedIn => {
        this.closeCheckInModal();
        this.onAppointmentStatusChange(appointmentId).then(() => {
          this.loading = false;
          this.alertScreenReader(`${checkedIn.student.name} checked in`);
        });
      }).catch(this.handleBadRequestError);
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
    closeUpdateModal() {
      this.showUpdateModal = false;
      this.onAppointmentStatusChange(this.appointmentUpdate.id).then(() => {
        this.loading = false;
      });
      this.appointmentUpdate = null;
    },
    handleBadRequestError(error) {
      if (error.response && error.response.status === 400) {
        const appointmentUpdate = this.get(error, 'response.data.message');
        if (appointmentUpdate) {
          this.appointmentUpdate = appointmentUpdate;
          this.showUpdateModal = true;
          this.loading = false;
        }
      } else {
        this.loading = false;
      }
    },
    launchCheckIn() {
      if (this.selfCheckIn) {
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
      this.loading = true;
      apiReserve(appointment.id).then(reserved => {
        this.onAppointmentStatusChange(appointment.id).then(() => {
          this.loading = false;
          this.alertScreenReader(`${reserved.student.name} appointment reserved`);
        });
      }).catch(this.handleBadRequestError);
    },
    showAppointmentDetails(appointment) {
      this.setSelectedAppointment(appointment);
      this.showAppointmentDetailsModal = true;
    },
    unreserveAppointment(appointment) {
      this.loading = true;
      apiUnreserve(appointment.id).then(unreserved => {
        this.onAppointmentStatusChange(appointment.id).then(() => {
          this.loading = false;
          this.alertScreenReader(`${unreserved.student.name} appointment unreserved`);
        });
      }).catch(this.handleBadRequestError);
    }
  }
}
</script>
