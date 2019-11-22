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
      :show-modal="showAppointmentDetailsModal"
      :student="appointment.student"
      :update-appointment="updateAppointment" />
    <CheckInModal
      v-if="showCheckInModal"
      :appointment="appointment"
      :appointment-checkin="checkInAppointment"
      :close="closeCheckInModal"
      :self-check-in="selfCheckIn"
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
          class="bg-white float-right text-nowrap"
          right
          split
          text="Details"
          variant="outline-dark"
          @click="showAppointmentDetails()">
          <b-dropdown-item-button
            :id="`btn-appointment-${appointment.id}-cancel`"
            @click="openCancelAppointmentModal()">
            <span aria-hidden="true" class="text-nowrap">Cancel Appt</span>
            <span class="sr-only">Cancel Appointment</span>
          </b-dropdown-item-button>
        </b-dropdown>
      </div>
      <div v-if="!user.isAdmin">
        <b-dropdown
          :id="`appointment-${appointment.id}-dropdown`"
          :disabled="appointment.status === 'checked_in' || appointment.status === 'cancelled'"
          class="bg-white float-right text-nowrap"
          right
          split
          text="Check In"
          variant="outline-dark"
          @click="launchCheckIn()">
          <b-dropdown-item-button
            v-if="includeDetailsOption"
            :id="`btn-appointment-${appointment.id}-details`"
            @click="showAppointmentDetails()">
            Details
          </b-dropdown-item-button>
          <b-dropdown-item-button
            v-if="isUserDropInAdvisor(deptCode) && (appointment.status !== 'reserved' || appointment.statusBy.id !== user.id)"
            :id="`btn-appointment-${appointment.id}-reserve`"
            @click="reserveAppointment()">
            <span class="text-nowrap">Assign</span>
          </b-dropdown-item-button>
          <b-dropdown-item-button
            v-if="appointment.status === 'reserved' && appointment.statusBy.id === user.id"
            :id="`btn-appointment-${appointment.id}-unreserve`"
            @click="unreserveAppointment()">
            <span class="text-nowrap">Unassign</span>
          </b-dropdown-item-button>
          <b-dropdown-item-button
            :id="`btn-appointment-${appointment.id}-cancel`"
            @click="openCancelAppointmentModal()">
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
  update as apiUpdate,
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
      apiCancel(this.appointment.id, reason, reasonExplained).then(cancelled => {
        this.onAppointmentStatusChange(this.appointment.id).then(() => {
          this.loading = false;
          this.alertScreenReader(`${cancelled.student.name} appointment cancelled`);
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
    },
    closeAppointmentDetailsModal() {
      this.showAppointmentDetailsModal = false;
      this.putFocusNextTick(`waitlist-student-${this.appointment.student.sid}`);
      this.alertScreenReader(`Dialog closed`);
    },
    closeCheckInModal() {
      this.showCheckInModal = false;
      this.showAppointmentDetailsModal = false;
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
      this.showCheckInModal = true;
    },
    openCancelAppointmentModal() {
      this.showCancelAppointmentModal = true;
    },
    reserveAppointment() {
      this.loading = true;
      apiReserve(this.appointment.id).then(reserved => {
        this.onAppointmentStatusChange(this.appointment.id).then(() => {
          this.loading = false;
          this.alertScreenReader(`${reserved.student.name} appointment assigned`);
        });
      }).catch(this.handleBadRequestError);
    },
    showAppointmentDetails() {
      this.showAppointmentDetailsModal = true;
    },
    unreserveAppointment() {
      this.loading = true;
      apiUnreserve(this.appointment.id).then(unreserved => {
        this.onAppointmentStatusChange(this.appointment.id).then(() => {
          this.loading = false;
          this.alertScreenReader(`${unreserved.student.name} appointment unassigned`);
        });
      }).catch(this.handleBadRequestError);
    },
    updateAppointment(details, topics) {
      this.loading = true;
      apiUpdate(this.appointment.id, details, topics).then(updated => {
        this.onAppointmentStatusChange(this.appointment.id).then(() => {
          this.loading = false;
          this.alertScreenReader(`${updated.student.name} appointment updated`);
        });
      }).catch(this.handleBadRequestError);
    }
  }
}
</script>
