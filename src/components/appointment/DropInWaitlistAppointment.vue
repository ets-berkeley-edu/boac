<template>
  <b-row
    :class="isLast ? '' : 'border-bottom'"
    class="font-size-16 mt-2 pb-1 pt-2"
    no-gutters>
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
            <span v-if="appointment.statusBy" :id="`reserved-for-${appointment.id}`">Reserved for {{ appointment.statusBy.id === user.id ? 'you' : appointment.statusBy.name }}</span>
            <span v-if="!appointment.statusBy" :id="`reserved-for-${appointment.id}`">Reserved</span>
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
          :on-appointment-status-change="onAppointmentStatusChange" />
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
</template>

<script>
import Context from '@/mixins/Context';
import DropInAppointmentDropdown from '@/components/appointment/DropInAppointmentDropdown';
import StudentAvatar from '@/components/student/StudentAvatar';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'DropInWaitlist',
  components: {
    DropInAppointmentDropdown,
    StudentAvatar
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
    showCreateAppointmentModal: false
  }),
  created() {
    this.linkToStudentProfiles = this.user.isAdmin || this.get(this.user, 'dropInAdvisorStatus.length');
    this.now = this.$moment();
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
.pill-cancelled {
  background-color: #ffecc0;
  color: #857103;
}
.pill-waiting {
  background-color: #78b1c9;
  color: #ffffff;
}
</style>
