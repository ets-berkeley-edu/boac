<template>
  <div class="ml-3 mt-3">
    <Spinner />
    <div v-if="!loading" style="margin: 0 auto; width: 480px;">
      <div class="mb-4 mt-4 text-center">
        <b-btn
          id="new-drop-in-appointment"
          variant="primary"
          class="btn-primary-color-override pl-3 pr-3"
          @click="showCreateAppointmentModal = true">
          New Drop-in Appointment
        </b-btn>
        <CreateAppointmentModal
          v-if="showCreateAppointmentModal"
          :cancel="cancelCreateAppointment"
          :create-appointment="createAppointment"
          :show-modal="showCreateAppointmentModal" />
      </div>
      <div class="border-bottom d-flex justify-content-between">
        <div>
          <h1 class="font-size-18 font-weight-bold text-nowrap">Today's Drop-In Waitlist ({{ size(waitlist) }})</h1>
        </div>
        <div>
          <h2 class="font-size-18 font-weight-bold text-nowrap">{{ $moment() | moment('ddd, MMM D') }}</h2>
        </div>
      </div>
      <div v-if="isEmpty(waitlist)" class="border-bottom">
        <div class="font-size-16 mb-3 ml-1 mt-3">
          No appointments yet
        </div>
      </div>
      <div v-if="!isEmpty(waitlist)">
        <div
          v-for="(appointment, index) in waitlist"
          :key="appointment.id"
          class="align-items-start border-bottom d-flex font-size-16 justify-content-between mb-3 ml-1 mt-3">
          <div>
            <span class="sr-only">Created at </span>{{ new Date(appointment.createdAt) | moment('LT') }}
          </div>
          <div>
            <div class="d-flex">
              <div class="mr-2">
                <StudentAvatar size="small" :student="appointment.student" />
              </div>
              <div>
                <router-link
                  v-if="linkToStudentProfiles"
                  :id="`link-to-student-${appointment.student.uid}`"
                  :to="studentRoutePath(appointment.student.uid, user.inDemoMode)">
                  <span :id="`waitlist-student-name-${index}`">{{ appointment.student.name }}</span>
                </router-link>
                <div v-if="!linkToStudentProfiles">
                  <span :id="`waitlist-student-name-${index}`">{{ appointment.student.name }}</span>
                </div>
                <div class="font-size-12">
                  {{ oxfordJoin(appointment.topics) }}
                </div>
              </div>
            </div>
          </div>
          <div>
            <b-dropdown
              class="bg-white mb-3"
              split
              :disabled="!!appointment.checkedInBy || !!appointment.canceledAt"
              text="Check In"
              variant="outline-dark"
              @click="appointmentCheckIn(appointment)">
              <b-dropdown-item-button @click="showAppointmentDetails(appointment)">Details</b-dropdown-item-button>
              <b-dropdown-item-button @click="cancelAppointment(appointment)">Cancel</b-dropdown-item-button>
            </b-dropdown>
            <AppointmentDetailsModal
              v-if="showAppointmentDetailsModal"
              :appointment="selectedAppointment"
              :close="closeAppointmentDetailsModal"
              :check-in="appointmentCheckIn"
              :show-modal="showAppointmentDetailsModal"
              :student="appointment.student" />
            <AppointmentCancellationModal
              v-if="showCancelAppointmentModal"
              :appointment="selectedAppointment"
              :appointment-cancellation="appointmentCancellation"
              :close="closeAppointmentCancellationModal"
              :show-modal="showCancelAppointmentModal"
              :student="appointment.student" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AppointmentDetailsModal from '@/components/appointment/AppointmentDetailsModal';
import AppointmentCancellationModal from '@/components/appointment/AppointmentCancellationModal';
import CreateAppointmentModal from '@/components/appointment/CreateAppointmentModal';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import StudentAvatar from '@/components/student/StudentAvatar';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { cancel as cancelAppointment, checkIn, create, getDropInAppointmentWaitlist } from '@/api/appointments'

export default {
  name: 'AppointmentWaitlist',
  components: {AppointmentCancellationModal, AppointmentDetailsModal, CreateAppointmentModal, Spinner, StudentAvatar},
  mixins: [Loading, UserMetadata, Util],
  data: () => ({
    linkToStudentProfiles: undefined,
    now: undefined,
    selectedAppointment: undefined,
    showAppointmentDetailsModal: false,
    showCancelAppointmentModal: false,
    showCreateAppointmentModal: false,
    waitlist: undefined
  }),
  created() {
    this.deptCode = this.get(this.$route, 'params.deptCode');
    this.linkToStudentProfiles = this.user.isAdmin || this.dropInAdvisorDeptCodes().length;
    this.now = this.$moment();
    getDropInAppointmentWaitlist(this.deptCode).then(waitlist => {
      this.waitlist = waitlist;
      this.loaded();
    });
  },
  methods: {
    appointmentCancellation(appointmentId, reason, reasonExplained) {
      cancelAppointment(this.selectedAppointment.id, reason, reasonExplained).then(canceled => {
        const indexOf = this.waitlist.findIndex(a => a.id === canceled.id);
        this.waitlist.splice(indexOf, 1);
      });
    },
    appointmentCheckIn(appointment) {
      checkIn(appointment.id).then(updated => {
        Object.assign(appointment, updated);
      });
    },
    cancelAppointment(appointment) {
      this.selectedAppointment = appointment;
      this.showCancelAppointmentModal = true;
    },
    cancelCreateAppointment() {
      this.showCreateAppointmentModal = false;
      this.selectedAppointment = undefined;
    },
    closeAppointmentCancellationModal() {
      this.showCancelAppointmentModal = false;
      this.selectedAppointment = undefined;
    },
    closeAppointmentDetailsModal() {
      this.showAppointmentDetailsModal = false;
      this.selectedAppointment = undefined;
    },
    createAppointment(details, sid, topics) {
      create(this.deptCode, details, sid, topics).then(appointment => {
        this.showCreateAppointmentModal = false;
        this.waitlist.push(appointment);
      });
    },
    showAppointmentDetails(appointment) {
      this.selectedAppointment = appointment;
      this.showAppointmentDetailsModal = true;
    }
  }
}
</script>

<style scoped>

</style>
