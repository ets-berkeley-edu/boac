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
            variant="link"
            class="mb-1"
            aria-label="Create appointment. Modal window will open."
            @click="showCreateAppointmentModal = true">
            <font-awesome icon="plus" />
          </b-btn>
        </div>
      </div>
      <DropInAvailabilityToggle
        :availability="!!get(find(user.dropInAdvisorStatus, {'deptCode': deptCode.toUpperCase()}), 'available')"
        :dept-code="deptCode"
        :is-homepage="isHomepage"
        :uid="user.uid" />
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
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { create as apiCreate } from '@/api/appointments';

export default {
  name: 'DropInWaitlist',
  components: {
    CreateAppointmentModal,
    DropInAvailabilityToggle,
    DropInWaitlistAppointment,
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
      type: Object,
      required: true
    }
  },
  data: () => ({
    creating: false,
    linkToStudentProfiles: undefined,
    now: undefined,
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
    }
  }
}
</script>

<style>
.border-thick-grey {
  border-color: lightgrey !important;
  border-width: 3px !important;
}
</style>
