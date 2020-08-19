<template>
  <b-row
    :class="{'border-bottom': isLast, 'row-assigned-to-me': appointment.status === 'reserved' && appointment.advisorId === $currentUser.id}"
    class="font-size-16 p-2 border-top"
    no-gutters>
    <b-col sm="2" class="pb-2 text-nowrap">
      <span class="sr-only">Created at </span><span :id="`appointment-${appointment.id}-created-at`">{{ new Date(appointment.createdAt) | moment('LT') }}</span>
    </b-col>
    <b-col sm="6">
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
                :class="{'demo-mode-blur': $currentUser.inDemoMode}"
                :to="studentRoutePath(appointment.student.uid, $currentUser.inDemoMode)">
                {{ appointment.student.name }}
              </router-link>
              <div v-if="!linkToStudentProfiles">
                <span
                  :id="`appointment-${appointment.id}-student-name`"
                  :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ appointment.student.name }}</span>
              </div>
            </div>
            <div>
              <span class="font-weight-bolder pr-1">
                (<span
                  :id="`appointment-${appointment.id}-student-sid`"
                  :class="{'demo-mode-blur': $currentUser.inDemoMode}"
                  aria-label="Student ID">{{ appointment.student.sid }}</span>)
              </span>
              <span
                v-if="appointment.student.academicCareerStatus === 'Inactive' || displayAsAscInactive(appointment.student) || displayAsCoeInactive(appointment.student)"
                class="inactive-info-icon"
                uib-tooltip="Inactive"
                tooltip-placement="bottom">
                <font-awesome icon="info-circle" />
              </span>
              <span
                v-if="appointment.student.academicCareerStatus === 'Completed'"
                uib-tooltip="Graduated"
                tooltip-placement="bottom">
                <font-awesome icon="graduation-cap" />
              </span>
            </div>
          </div>
          <div
            v-if="appointment.topics.length"
            :id="`appointment-${appointment.id}-topics`"
            class="appointment-topics font-size-14 pb-2">
            {{ oxfordJoin(appointment.topics) }}
          </div>
          <div v-if="appointment.status === 'reserved'" class="has-error">
            <span v-if="appointment.advisorId" :id="`assigned-to-${appointment.id}`">Assigned to {{ appointment.advisorId === $currentUser.id ? 'you' : appointment.advisorName }}</span>
            <span v-if="!appointment.advisorId" :id="`assigned-to-${appointment.id}`">Assigned</span>
          </div>
          <div v-if="appointment.advisorName && !reopening">
            <div class="font-size-14 pb-2 text-nowrap">
              <span v-if="appointment.status === 'checked_in'">
                <font-awesome icon="calendar-check" class="status-checked-in-icon" />
                {{ appointment.advisorName }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </b-col>
    <b-col sm="4">
      <DropInAppointmentDropdown
        v-if="includes(['reserved', 'waiting'], appointment.status)"
        :appointment="appointment"
        :dept-code="deptCode"
        :self-check-in="isHomepage"
        :on-appointment-status-change="onAppointmentStatusChange" />
      <div v-if="includes(['checked_in', 'cancelled'], appointment.status)" class="d-flex justify-content-end">
        <div>
          <button
            v-if="!reopening"
            class="btn btn-link pr-1 pt-1"
            @click="reopenAppointment"
            @keyup.enter="reopenAppointment">
            Undo<span class="sr-only"> {{ appointment.status }} status</span>
          </button>
          <div v-if="reopening" :id="`appointment-${appointment.id}-reopen-spinner`" class="float-right pl-2 pr-3 pt-1">
            <font-awesome icon="spinner" spin />
          </div>
        </div>
        <div
          v-if="appointment.status === 'cancelled' && !reopening"
          :id="`appointment-${appointment.id}-cancelled`"
          class="float-right pill-appointment-status pill-cancelled pl-2 pr-2">
          Cancelled<span class="sr-only"> appointment</span>
        </div>
        <div v-if="appointment.status === 'checked_in' && !reopening">
          <div
            :id="`appointment-${appointment.id}-checked-in`"
            class="pill-appointment-status pill-checked-in pl-2 pr-2 text-nowrap">
            <span class="sr-only">Student was </span>Checked In
          </div>
        </div>
      </div>
    </b-col>
  </b-row>
</template>

<script>
import Context from '@/mixins/Context';
import DropInAppointmentDropdown from '@/components/appointment/DropInAppointmentDropdown';
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentMetadata from '@/mixins/StudentMetadata';
import Util from '@/mixins/Util';
import { reopen as apiReopen } from '@/api/appointments';

export default {
  name: 'DropInWaitlist',
  components: {
    DropInAppointmentDropdown,
    StudentAvatar
  },
  mixins: [Context, StudentMetadata, Util],
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
      default: false
    },
    isLast: {
      type: Boolean,
      default: false
    },
    onAppointmentStatusChange: {
      type: Function,
      required: true
    },
  },
  data: () => ({
    creating: false,
    linkToStudentProfiles: undefined,
    now: undefined,
    reopening: false,
    showCreateAppointmentModal: false
  }),
  created() {
    this.linkToStudentProfiles = this.$currentUser.isAdmin || this.get(this.$currentUser, 'dropInAdvisorStatus.length');
    this.now = this.$moment();
  },
  methods: {
    reopenAppointment() {
      this.reopening = true;
      apiReopen(this.appointment.id).then(() => {
        this.onAppointmentStatusChange(this.appointment.id).then(() => {
          this.reopening = false;
          this.alertScreenReader(`${this.appointment.student.name} appointment reopened`);
        });
      }).catch(this.handleBadRequestError);
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
.status-cancelled-icon {
  color: #f0ad4e;
}
.status-checked-in-icon {
  color: #00c13a;
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
.row-assigned-to-me {
  background-color: #ecf5fb;
}
</style>
