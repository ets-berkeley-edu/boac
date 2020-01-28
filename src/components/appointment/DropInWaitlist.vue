<template>
  <div>
    <CreateAppointmentModal
      v-if="showCreateAppointmentModal"
      :advisors="advisors"
      :cancel="cancelCreateAppointment"
      :create-appointment="createAppointment"
      :dept-code="deptCode"
      :show-modal="showCreateAppointmentModal"
      :waitlist-unresolved="waitlist.unresolved" />
    <div v-if="isHomepage" class="homepage-header-border">
      <div class="align-items-center d-flex justify-content-between mb-2">
        <div aria-live="polite" role="alert">
          <h2 class="page-section-header">Drop-in Waitlist - {{ $moment() | moment('MMM D') }}</h2>
        </div>
        <div v-if="!$currentUser.isAdmin">
          <b-btn
            id="btn-homepage-create-appointment"
            variant="link"
            class="mb-1"
            aria-label="Create appointment. Modal window will open."
            @click="showCreateAppointmentModal = true">
            <font-awesome icon="plus" />
          </b-btn>
        </div>
      </div>
      <div class="mb-2">
        <DropInAvailabilityToggle
          :availability="dropInAvailability"
          :dept-code="deptCode"
          :is-homepage="isHomepage"
          :reserved-appointments="myReservedAppointments"
          :uid="$currentUser.uid" />
      </div>
      <div v-if="dropInStatusLoading" class="pl-2">
        <font-awesome icon="spinner" spin />
      </div>
      <b-form v-if="!dropInStatusLoading && !dropInStatus" @submit="submitDropInStatus">
        <div class="d-flex mb-2">
          <div class="drop-in-status-label-outer">
            <label class="drop-in-status-label" for="drop-in-status-input">My Status:</label>
          </div>
          <div class="drop-in-status-input-outer pr-3">
            <b-form-input
              id="drop-in-status-input"
              v-model="dropInStatusNew"
              class="drop-in-status-input"
              maxlength="255"></b-form-input>
          </div>
          <div class="drop-in-status-submit-outer">
            <b-btn
              id="drop-in-status-submit"
              class="btn-primary-color-override"
              :disabled="!dropInStatusNew"
              type="submit"
              variant="primary">
              Set Status
            </b-btn>
          </div>
        </div>
      </b-form>
      <div v-if="!dropInStatusLoading && dropInStatus" class="mb-2">
        <span class="drop-in-status-label">My Status:</span>
        {{ dropInStatus }}
        <button
          id="drop-in-status-clear"
          class="btn btn-link pb-0 pl-2 pt-0"
          @click="clearDropInStatus"
          @keyup.enter="clearDropInStatus">
          Clear Status
        </button>
      </div>
    </div>
    <div v-if="!isHomepage">
      <div class="border-bottom d-flex justify-content-between">
        <div>
          <h1 class="font-size-18 font-weight-bold text-nowrap">
            <span aria-live="polite" role="alert">Today's Drop-In Waitlist ({{ waitlist.unresolved.length }}<span class="sr-only"> students</span>)</span>
          </h1>
        </div>
        <div>
          <h2 id="waitlist-today-date" class="font-size-18 font-weight-bold text-nowrap">{{ $moment() | moment('ddd, MMM D') }}</h2>
        </div>
      </div>
    </div>
    <div v-if="!waitlist.unresolved.length && !waitlist.resolved.length && !creating" class="border-bottom">
      <div
        id="waitlist-is-empty"
        class="font-size-16 mb-3 ml-1 mt-3"
        aria-live="polite"
        role="alert">
        No appointments yet
      </div>
    </div>
    <div v-if="waitlist.unresolved.length || waitlist.resolved.length || creating">
      <b-container fluid class="pl-0 pr-0" :class="{'homepage-header-border': isHomepage}">
        <b-row v-if="waitlist.unresolved.length">
          <span class="sr-only">{{ waitlist.unresolved.length }} appointments not yet checked in</span>
        </b-row>
        <DropInWaitlistAppointment
          v-for="(appointment, index) in waitlist.unresolved"
          :key="appointment.id"
          :appointment="appointment"
          :dept-code="deptCode"
          :is-homepage="isHomepage"
          :is-last="!creating && (index + 1 === waitlist.unresolved.length)"
          :on-appointment-status-change="onAppointmentStatusChange" />
        <b-row
          v-if="creating"
          id="waitlist-appointment-creation-spinner"
          no-gutters
          class="font-size-16 mt-2 pb-4 pt-1">
          <b-col sm="12" class="text-center">
            <font-awesome icon="spinner" spin />
          </b-col>
        </b-row>
        <b-row
          :class="waitlist.unresolved.length && waitlist.resolved.length ? 'border-thick-grey' : ''"
          no-gutters
          class="border-top">
          <span v-if="waitlist.resolved.length" class="sr-only">{{ waitlist.resolved.length }} appointments checked in or cancelled</span>
        </b-row>
        <DropInWaitlistAppointment
          v-for="appointment in waitlist.resolved"
          :key="appointment.id"
          :appointment="appointment"
          :is-homepage="isHomepage"
          :dept-code="deptCode"
          :on-appointment-status-change="onAppointmentStatusChange" />
      </b-container>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import CreateAppointmentModal from '@/components/appointment/CreateAppointmentModal';
import DropInAvailabilityToggle from '@/components/appointment/DropInAvailabilityToggle';
import DropInWaitlistAppointment from '@/components/appointment/DropInWaitlistAppointment';
import Util from '@/mixins/Util';
import { create as apiCreate } from '@/api/appointments';
import { setDropInStatus } from '@/api/user';

export default {
  name: 'DropInWaitlist',
  components: {
    CreateAppointmentModal,
    DropInAvailabilityToggle,
    DropInWaitlistAppointment,
  },
  mixins: [Context, Util],
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
      type: Object,
      required: true
    }
  },
  data: () => ({
    creating: false,
    dropInAvailability: false,
    dropInStatus: null,
    dropInStatusLoading: false,
    dropInStatusNew: undefined,
    linkToStudentProfiles: undefined,
    now: undefined,
    showCreateAppointmentModal: false
  }),
  computed: {
    myReservedAppointments: function() {
      return this.filterList(this.waitlist.unresolved, (appt) => {
        return appt.status === 'reserved' && appt.advisorUid === this.$currentUser.uid;
      });
    }
  },
  created() {
    const currentUserDropInStatus = this.get(this.$currentUser, 'dropInAdvisorStatus');
    this.linkToStudentProfiles = this.$currentUser.isAdmin || !this.isEmpty(this.currentUserDropInStatus);
    this.now = this.$moment();
    if (this.isHomepage) {
      this.$eventHub.$on('drop-in-status-change', newAttributes => {
        this.updateDropInAttributes(newAttributes);
      });
      this.updateDropInAttributes(this.find(currentUserDropInStatus, {'deptCode': this.deptCode.toUpperCase()}))
    }
  },
  methods: {
    cancelCreateAppointment() {
      this.showCreateAppointmentModal = false;
      this.alertScreenReader('Dialog closed');
    },
    clearDropInStatus() {
      this.dropInStatusLoading = true;
      setDropInStatus(this.deptCode).then(response => {
        this.updateDropInAttributes(response);
        this.dropInStatusLoading = false;
        this.dropInStatusNew = null;
        this.alertScreenReader('Drop-in status cleared');
      });
    },
    createAppointment(
      details,
      student,
      topics,
      advisorUid
    ) {
      this.creating = true;
      apiCreate(
        this.deptCode,
        details,
        student.sid,
        'Drop-in',
        topics,
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
    submitDropInStatus() {
      this.dropInStatusLoading = true;
      setDropInStatus(this.deptCode, this.dropInStatusNew).then(response => {
        this.updateDropInAttributes(response);
        this.dropInStatusLoading = false;
        this.alertScreenReader('Drop-in status updated');
      });
    },
    updateDropInAttributes(attrs) {
      if (attrs) {
        this.dropInAvailability = attrs.available;
        this.dropInStatus = attrs.status;
      }
    }
  }
}
</script>

<style>
.border-thick-grey {
  border-color: lightgrey !important;
  border-width: 3px !important;
}
.drop-in-status-label {
  font-size: 12px;
  text-transform: uppercase;
}
.drop-in-status-input-outer {
  flex: 1;
}
.drop-in-status-label-outer {
  flex: 0 0 80px;
}
.drop-in-status-submit-outer {
  flex: 0 0 120px;
}
</style>
