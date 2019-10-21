<template>
  <div>
    <AppointmentCancellationModal
      v-if="showCancelAppointmentModal"
      :appointment="selectedAppointment"
      :appointment-cancellation="appointmentCancellation"
      :close="closeAppointmentCancellationModal"
      :show-modal="showCancelAppointmentModal"
      :student="selectedAppointment.student" />
    <AppointmentDetailsModal
      v-if="showAppointmentDetailsModal"
      :appointment="selectedAppointment"
      :close="closeAppointmentDetailsModal"
      :check-in="launchCheckIn"
      :show-modal="showAppointmentDetailsModal"
      :student="selectedAppointment.student" />
    <CheckInModal
      v-if="showCheckInModal"
      :appointment="selectedAppointment"
      :appointment-checkin="checkInAppointment"
      :close="closeCheckInModal"
      :show-modal="showCheckInModal" />
    <CreateAppointmentModal
      v-if="showCreateAppointmentModal"
      :cancel="cancelCreateAppointment"
      :create-appointment="createAppointment"
      :show-modal="showCreateAppointmentModal" />
    <div v-if="isHomepage">
      <div class="align-items-center d-flex homepage-header-border justify-content-between">
        <div>
          <h2 class="page-section-header">Drop-in Waitlist - {{ $moment() | moment('MMM D') }}</h2>
        </div>
        <div>
          <b-btn
            id="create-drop-in-appointment"
            variant="link"
            class="mb-1"
            aria-label="Create appointment. Modal window will open."
            @click="showCreateAppointmentModal = true">
            <font-awesome icon="plus" />
          </b-btn>
        </div>
      </div>
    </div>
    <div v-if="!isHomepage">
      <div class="mb-4 mt-4 text-center">
        <b-btn
          id="new-drop-in-appointment"
          variant="primary"
          class="btn-primary-color-override pl-3 pr-3"
          aria-label="Create appointment. Modal window will open."
          @click="showCreateAppointmentModal = true">
          New Drop-in Appointment
        </b-btn>
      </div>
      <div class="border-bottom d-flex justify-content-between">
        <div>
          <h1 class="font-size-18 font-weight-bold text-nowrap">Today's Drop-In Waitlist ({{ size(waitlist) }})</h1>
        </div>
        <div>
          <h2 class="font-size-18 font-weight-bold text-nowrap">{{ $moment() | moment('ddd, MMM D') }}</h2>
        </div>
      </div>
    </div>
    <div v-if="!waitlist.length" class="border-bottom">
      <div class="font-size-16 mb-3 ml-1 mt-3" aria-live="polite" role="alert">
        No appointments yet
      </div>
    </div>
    <div v-if="waitlist.length">
      <b-container fluid class="pl-0 pr-0">
        <b-row
          v-for="appointment in waitlist"
          :key="appointment.id"
          no-gutters
          class="border-bottom font-size-16 mt-3 pb-3">
          <b-col cols="2" class="pb-2 text-nowrap">
            <span class="sr-only">Created at </span>{{ new Date(appointment.createdAt) | moment('LT') }}
          </b-col>
          <b-col cols="7">
            <div class="d-flex">
              <div v-if="isHomepage" class="mr-2">
                <StudentAvatar size="small" :student="appointment.student" />
              </div>
              <div>
                <div class="font-size-16">
                  <router-link
                    v-if="linkToStudentProfiles"
                    :id="`waitlist-student-${appointment.student.sid}`"
                    :class="{'demo-mode-blur' : user.inDemoMode}"
                    :to="studentRoutePath(appointment.student.uid, user.inDemoMode)">
                    {{ appointment.student.name }}
                  </router-link>
                  <div v-if="!linkToStudentProfiles">
                    <span
                      :id="`waitlist-student-${appointment.student.sid}`"
                      :class="{'demo-mode-blur' : user.inDemoMode}">{{ appointment.student.name }}</span>
                  </div>
                </div>
                <div v-if="appointment.topics.length" class="appointment-topics font-size-14 pb-2">
                  {{ oxfordJoin(appointment.topics) }}
                </div>
              </div>
            </div>
          </b-col>
          <b-col class="float-right">
            <b-dropdown
              class="bg-white text-nowrap"
              split
              :disabled="!!appointment.checkedInBy || !!appointment.canceledAt"
              text="Check In"
              variant="outline-dark"
              @click="launchCheckInForAppointment(appointment)">
              <b-dropdown-item-button @click="showAppointmentDetails(appointment)">Details</b-dropdown-item-button>
              <b-dropdown-item-button @click="cancelAppointment(appointment)">Cancel</b-dropdown-item-button>
            </b-dropdown>
          </b-col>
        </b-row>
      </b-container>
    </div>
  </div>
</template>

<script>
import AppointmentDetailsModal from '@/components/appointment/AppointmentDetailsModal';
import AppointmentCancellationModal from '@/components/appointment/AppointmentCancellationModal';
import CheckInModal from '@/components/appointment/CheckInModal';
import Context from '@/mixins/Context';
import CreateAppointmentModal from '@/components/appointment/CreateAppointmentModal';
import StudentAvatar from '@/components/student/StudentAvatar';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { cancel as apiCancel, checkIn as apiCheckIn, create as apiCreate } from '@/api/appointments';

export default {
  name: 'DropInWaitlist',
  components: {
    AppointmentCancellationModal,
    AppointmentDetailsModal,
    CheckInModal,
    CreateAppointmentModal,
    StudentAvatar
  },
  mixins: [Context, UserMetadata, Util],
  props: {
    deptCode: {
      type: String,
      required: true
    },
    isHomepage: {
      type: Boolean,
      default: false
    },
    waitlist: {
      type: Array,
      required: true
    }
  },
  data: () => ({
    linkToStudentProfiles: undefined,
    now: undefined,
    selectedAppointment: undefined,
    showAppointmentDetailsModal: false,
    showCancelAppointmentModal: false,
    showCheckInModal: false,
    showCreateAppointmentModal: false
  }),
  created() {
    this.linkToStudentProfiles = this.user.isAdmin || this.dropInAdvisorDeptCodes().length;
    this.now = this.$moment();
  },
  methods: {
    appointmentCancellation(appointmentId, reason, reasonExplained) {
      apiCancel(this.selectedAppointment.id, reason, reasonExplained).then(canceled => {
        const indexOf = this.waitlist.findIndex(a => a.id === canceled.id);
        this.waitlist.splice(indexOf, 1);
      });
    },
    cancelAppointment(appointment) {
      this.selectedAppointment = appointment;
      this.showCancelAppointmentModal = true;
    },
    cancelCreateAppointment() {
      this.showCreateAppointmentModal = false;
      this.alertScreenReader('Create appointment modal closed');
      this.selectedAppointment = undefined;
    },
    checkInAppointment(advisor, deptCodes) {
      if (!advisor) {
        advisor = this.user;
        deptCodes = this.map(this.user.departments, 'code');
      }
      const appointmentId = this.selectedAppointment.id;
      apiCheckIn(
        deptCodes,
        advisor.name,
        advisor.title,
        advisor.uid,
        appointmentId
      ).then(() => {
        const index = this.findIndex(this.waitlist, {id: appointmentId});
        this.alertScreenReader(`Student ${this.selectedAppointment.student.name} checked in`);
        this.selectedAppointment = undefined;
        if (index !== -1) {
          this.waitlist.splice(index, 1);
        }
      });
    },
    closeAppointmentCancellationModal() {
      this.showCancelAppointmentModal = false;
      this.putFocusNextTick(`waitlist-student-${this.selectedAppointment.student.sid}`);
      this.alertScreenReader('Cancel appointment modal closed');
      this.selectedAppointment = undefined;
    },
    closeAppointmentDetailsModal() {
      this.showAppointmentDetailsModal = false;
      this.putFocusNextTick(`waitlist-student-${this.selectedAppointment.student.sid}`);
      this.alertScreenReader('Appointment details modal closed');
      this.selectedAppointment = undefined;
    },
    closeCheckInModal() {
      this.showCheckInModal = false;
      this.showAppointmentDetailsModal = false;
      this.selectedAppointment = undefined;
    },
    createAppointment(details, student, topics) {
      apiCreate(this.deptCode, details, student.sid, 'Drop-in', topics).then(appointment => {
        this.alertScreenReader(`Appointment created for ${student.label}`);
        this.showCreateAppointmentModal = false;
        this.waitlist.push(appointment);
        this.putFocusNextTick(`waitlist-student-${student.sid}`)
      });
    },
    launchCheckIn() {
      if (this.isHomepage) {
        this.checkInAppointment();
      } else {
        this.showCheckInModal = true;
      }
    },
    launchCheckInForAppointment(appointment) {
      this.selectedAppointment = appointment;
      this.launchCheckIn();
    },
    showAppointmentDetails(appointment) {
      this.selectedAppointment = appointment;
      this.showAppointmentDetailsModal = true;
    }
  }
}
</script>

<style scoped>
.appointment-topics {
  max-width: 240px;
}
</style>
