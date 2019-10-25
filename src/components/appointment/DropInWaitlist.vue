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
    <div v-if="isHomepage" class="align-items-center d-flex homepage-header-border justify-content-between mb-2">
      <div aria-live="polite" role="alert">
        <h2 class="page-section-header">Drop-in Waitlist - {{ $moment() | moment('MMM D') }}</h2>
      </div>
      <div>
        <b-btn
          id="btn-homepage-create-appointment"
          @click="showCreateAppointmentModal = true"
          variant="link"
          class="mb-1"
          aria-label="Create appointment. Modal window will open.">
          <font-awesome icon="plus" />
        </b-btn>
      </div>
    </div>
    <div v-if="!isHomepage">
      <div class="mb-4 pb-3 pt-3 text-center">
        <b-btn
          id="btn-create-appointment"
          @click="openCreateAppointmentModal()"
          variant="primary"
          class="btn-primary-color-override pl-3 pr-3"
          aria-label="Create appointment. Modal window will open.">
          New Drop-in Appointment
        </b-btn>
      </div>
      <div class="border-bottom d-flex justify-content-between">
        <div>
          <h1 class="font-size-18 font-weight-bold text-nowrap">
            <span aria-live="polite" role="alert">Today's Drop-In Waitlist ({{ size(waitlist) }}<span class="sr-only"> students</span>)</span>
          </h1>
        </div>
        <div>
          <h2 id="waitlist-today-date" class="font-size-18 font-weight-bold text-nowrap">{{ $moment() | moment('ddd, MMM D') }}</h2>
        </div>
      </div>
    </div>
    <div v-if="!waitlist.length" class="border-bottom">
      <div
        id="waitlist-is-empty"
        class="font-size-16 mb-3 ml-1 mt-3"
        aria-live="polite"
        role="alert">
        No appointments yet
      </div>
    </div>
    <div v-if="waitlist.length">
      <b-container fluid class="pl-0 pr-0">
        <b-row
          v-for="appointment in waitlist"
          :key="appointment.id"
          no-gutters
          class="border-bottom font-size-16 mt-3 pb-2 pt-2">
          <b-col cols="2" class="pb-2 text-nowrap">
            <span class="sr-only">Created at </span><span :id="`appointment-${appointment.id}-created-at`">{{ new Date(appointment.createdAt) | moment('LT') }}</span>
          </b-col>
          <b-col cols="7">
            <div class="d-flex">
              <div v-if="isHomepage" class="mr-2">
                <StudentAvatar :student="appointment.student" size="small" />
              </div>
              <div>
                <div class="font-size-16">
                  <router-link
                    v-if="linkToStudentProfiles"
                    :id="`appointment-${appointment.id}-student-name`"
                    :class="{'demo-mode-blur' : user.inDemoMode}"
                    :to="studentRoutePath(appointment.student.uid, user.inDemoMode)">
                    {{ appointment.student.name }}
                  </router-link>
                  <div v-if="!linkToStudentProfiles">
                    <span
                      :id="`appointment-${appointment.id}-student-name`"
                      :class="{'demo-mode-blur' : user.inDemoMode}">{{ appointment.student.name }}</span>
                  </div>
                </div>
                <div
                  v-if="appointment.topics.length"
                  :id="`appointment-${appointment.id}-topics`"
                  class="appointment-topics font-size-14 pb-2">
                  {{ oxfordJoin(appointment.topics) }}
                </div>
              </div>
            </div>
          </b-col>
          <b-col cols="3">
            <b-dropdown
              v-if="isNil(appointment.checkedInAt) && isNil(appointment.canceledAt)"
              :id="`appointment-${appointment.id}-dropdown`"
              :disabled="!!appointment.checkedInBy || !!appointment.canceledAt"
              @click="launchCheckInForAppointment(appointment)"
              class="bg-white float-right text-nowrap"
              right
              split
              text="Check In"
              variant="outline-dark">
              <b-dropdown-item-button :id="`btn-appointment-${appointment.id}-details`" @click="showAppointmentDetails(appointment)">Details</b-dropdown-item-button>
              <b-dropdown-item-button
                :id="`btn-appointment-${appointment.id}-cancel`"
                @click="cancelAppointment(appointment)">
                <span aria-hidden="true">Cancel Appt</span>
                <span class="sr-only">Cancel Appointment</span>
              </b-dropdown-item-button>
            </b-dropdown>
            <div
              v-if="isNil(appointment.checkedInAt) && !isNil(appointment.canceledAt)"
              :id="`appointment-${appointment.id}-canceled`"
              class="float-right pill-appointment-status pill-canceled pl-2 pr-2">
              Canceled<span class="sr-only"> appointment</span>
            </div>
            <div
              v-if="!isNil(appointment.checkedInAt) && isNil(appointment.canceledAt)"
              :id="`appointment-${appointment.id}-checked-in`"
              class="float-right pill-appointment-status pill-checked-in pl-2 pr-2">
              <span class="sr-only">Student was </span>Checked In
            </div>
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
        if (this.isHomepage) {
          let match = this.waitlist.find(a => a.id === +canceled.id);
          Object.assign(match, canceled);
        } else {
          const indexOf = this.waitlist.findIndex(a => a.id === canceled.id);
          this.waitlist.splice(indexOf, 1);
        }
        this.alertScreenReader(`${canceled.student.name} appointment canceled`);
        this.selectedAppointment = undefined;
      });
    },
    cancelAppointment(appointment) {
      this.selectedAppointment = appointment;
      this.showCancelAppointmentModal = true;
    },
    cancelCreateAppointment() {
      this.showCreateAppointmentModal = false;
      this.alertScreenReader('Dialog closed');
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
      ).then(checkedIn => {
        if (this.isHomepage) {
          let match = this.waitlist.find(a => a.id === +checkedIn.id);
          Object.assign(match, checkedIn);
        } else {
          const indexOf = this.waitlist.findIndex(a => a.id === checkedIn.id);
          this.waitlist.splice(indexOf, 1);
        }
        this.alertScreenReader(`${checkedIn.student.name} checked in`);
        this.closeCheckInModal();
      });
    },
    closeAppointmentCancellationModal() {
      this.showCancelAppointmentModal = false;
      this.putFocusNextTick(`waitlist-student-${this.selectedAppointment.student.sid}`);
      this.alertScreenReader('Dialog closed');
      this.selectedAppointment = undefined;
    },
    closeAppointmentDetailsModal() {
      this.showAppointmentDetailsModal = false;
      this.putFocusNextTick(`waitlist-student-${this.selectedAppointment.student.sid}`);
      this.alertScreenReader(`Dialog closed`);
      this.selectedAppointment = undefined;
    },
    closeCheckInModal() {
      this.showCheckInModal = false;
      this.showAppointmentDetailsModal = false;
      this.selectedAppointment = undefined;
    },
    createAppointment(details, student, topics) {
      apiCreate(this.deptCode, details, student.sid, 'Drop-in', topics).then(appointment => {
        this.alertScreenReader(`${student.label} appointment created`);
        this.showCreateAppointmentModal = false;
        this.waitlist.unshift(appointment);
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
    openCreateAppointmentModal() {
      this.showCreateAppointmentModal = true;
      this.alertScreenReader('Create appointment form is open');
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

<style>
.pill-appointment-status {
  border-radius: 5px;
  display: inline-block;
  font-size: 14px;
  font-weight: 800;
  height: 32px;
  min-width: 108px;
  max-width: 108px;
  padding-top: 6px;
  text-align: center;
  text-transform: uppercase;
  whitespace: nowrap;
}
.pill-checked-in {
  background-color: #e2ffc0;
  color: #518019;
}
.pill-canceled {
  background-color: #ffecc0;
  color: #857103;
}
.pill-waiting {
  background-color: #78b1c9;
  color: #ffffff;
}
</style>
