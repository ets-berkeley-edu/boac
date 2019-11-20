<template>
  <div>
    <CreateAppointmentModal
      v-if="showCreateAppointmentModal"
      :advisors="advisors"
      :cancel="cancelCreateAppointment"
      :create-appointment="createAppointment"
      :dept-code="deptCode"
      :show-modal="showCreateAppointmentModal" />
    <div v-if="isHomepage" class="homepage-header-border">
      <div class="align-items-center d-flex justify-content-between mb-2">
        <div aria-live="polite" role="alert">
          <h2 class="page-section-header">Drop-in Waitlist - {{ $moment() | moment('MMM D') }}</h2>
        </div>
        <div v-if="!user.isAdmin">
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
      <DropInAvailabilityToggle :dept-code="deptCode" />
    </div>
    <div v-if="!isHomepage">
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
          id="waitlist-appointment-creation-spinner"
          v-if="creating"
          no-gutters
          class="border-bottom font-size-16 mt-3 pb-4 pt-2">
          <b-col sm="12" class="text-center">
            <font-awesome icon="spinner" spin />
          </b-col>
        </b-row>
        <b-row
          v-for="(appointment, index) in waitlist"
          :key="appointment.id"
          :class="{'border-thick-grey': index < (waitlist.length - 1) && appointment.status !== 'cancelled' && waitlist[index + 1].status === 'cancelled'}"
          no-gutters
          class="border-bottom font-size-16 mt-2 pb-1 pt-1">
          <b-col sm="2" class="pb-2 text-nowrap">
            <span class="sr-only">Created at </span><span :id="`appointment-${appointment.id}-created-at`">{{ new Date(appointment.createdAt) | moment('LT') }}</span>
          </b-col>
          <b-col sm="7">
            <div class="d-flex">
              <div v-if="isHomepage" class="mr-2">
                <StudentAvatar :student="appointment.student" size="small" />
              </div>
              <div>
                <div class="d-flex flex-wrap font-size-16">
                  <div class="pr-1">
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
                  <div>
                    <div class="font-weight-bolder pr-1">
                      (<span
                        :id="`appointment-${appointment.id}-student-sid`"
                        :class="{'demo-mode-blur' : user.inDemoMode}"
                        aria-label="Student ID">{{ appointment.student.sid }}</span>)
                    </div>
                  </div>
                </div>
                <div
                  v-if="appointment.topics.length"
                  :id="`appointment-${appointment.id}-topics`"
                  class="appointment-topics font-size-14 pb-2">
                  {{ oxfordJoin(appointment.topics) }}
                </div>
                <div v-if="appointment.status === 'reserved'" class="has-error">
                  <span :id="`reserved-for-${appointment.id}`" v-if="appointment.statusBy">Reserved for {{ appointment.statusBy.id === user.id ? 'you' : appointment.statusBy.name }}</span>
                  <span :id="`reserved-for-${appointment.id}`" v-if="!appointment.statusBy">Reserved</span>
                </div>
              </div>
            </div>
          </b-col>
          <b-col sm="3">
            <div>
              <DropInAppointmentDropdown
                :appointment="appointment"
                :dept-code="deptCode"
                :self-check-in="isHomepage"
                :on-appointment-status-change="onAppointmentStatusChange"
                :set-selected-appointment="setSelectedAppointment" />
            </div>
            <div
              v-if="appointment.status === 'cancelled'"
              :id="`appointment-${appointment.id}-cancelled`"
              class="float-right pill-appointment-status pill-cancelled pl-2 pr-2">
              Cancelled<span class="sr-only"> appointment</span>
            </div>
            <div
              v-if="appointment.status === 'checked_in'"
              :id="`appointment-${appointment.id}-checked-in`"
              class="float-right pill-appointment-status pill-checked-in pl-2 pr-2 text-nowrap">
              <span class="sr-only">Student was </span>Checked In
            </div>
          </b-col>
        </b-row>
      </b-container>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import CreateAppointmentModal from '@/components/appointment/CreateAppointmentModal';
import DropInAppointmentDropdown from '@/components/appointment/DropInAppointmentDropdown';
import DropInAvailabilityToggle from '@/components/appointment/DropInAvailabilityToggle';
import StudentAvatar from '@/components/student/StudentAvatar';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { create as apiCreate } from '@/api/appointments';

export default {
  name: 'DropInWaitlist',
  components: {
    CreateAppointmentModal,
    DropInAppointmentDropdown,
    DropInAvailabilityToggle,
    StudentAvatar
  },
  mixins: [Context, UserMetadata, Util],
  props: {
    advisors: {
      type: Array,
      required: false
    },
    deptCode: {
      type: String,
      required: true
    },
    isHomepage: {
      type: Boolean,
      default: false
    },
    onAppointmentStatusChange: {
      type: Function,
      required: true
    },
    waitlist: {
      type: Array,
      required: true
    }
  },
  data: () => ({
    creating: false,
    linkToStudentProfiles: undefined,
    now: undefined,
    selectedAppointment: undefined,
    showCreateAppointmentModal: false
  }),
  created() {
    this.linkToStudentProfiles = this.user.isAdmin || this.get(this.user, 'dropInAdvisorStatus.length');
    this.now = this.$moment();
  },
  methods: {
    cancelCreateAppointment() {
      this.showCreateAppointmentModal = false;
      this.alertScreenReader('Dialog closed');
      this.selectedAppointment = undefined;
    },
    createAppointment(
      details,
      student,
      topics,
      advisorDeptCodes,
      advisorName,
      advisorRole,
      advisorUid
    ) {
      this.creating = true;
      apiCreate(
        this.deptCode,
        details,
        student.sid,
        'Drop-in',
        topics,
        advisorDeptCodes,
        advisorName,
        advisorRole,
        advisorUid
      ).then(() => {
        this.showCreateAppointmentModal = false;
        this.onAppointmentStatusChange().then(() => {
          this.creating = false;
          this.alertScreenReader(`${student.label} appointment created`);
          this.putFocusNextTick(`waitlist-student-${student.sid}`)
        });
      });
    },
    openCreateAppointmentModal() {
      this.showCreateAppointmentModal = true;
      this.alertScreenReader('Create appointment form is open');
    },
    setSelectedAppointment(appointment) {
      this.selectedAppointment = appointment;
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
.border-thick-grey {
  border-color: #aaa !important;
  border-width: 3px !important;
}
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
.pill-cancelled {
  background-color: #ffecc0;
  color: #857103;
}
.pill-waiting {
  background-color: #78b1c9;
  color: #ffffff;
}
</style>
