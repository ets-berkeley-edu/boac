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
          v-for="appointment in waitlist"
          :key="appointment.id"
          class="border-bottom">
          <div class="font-size-16 mb-3 ml-1 mt-3">
            {{ appointment }}
          </div>
        </div>
      </div>
      <AppointmentDetailsModal
        v-if="showAppointmentDetailsModal"
        :appointment="appointment"
        :close="closeAppointmentDetailsModal"
        :check-in="appointmentCheckIn"
        :modal-header="student.name"
        :show-modal="showAppointmentDetailsModal" />
    </div>
  </div>
</template>

<script>
import AppointmentDetailsModal from '@/components/appointment/AppointmentDetailsModal';
import CreateAppointmentModal from '@/components/appointment/CreateAppointmentModal';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { checkIn, create, getDropInAppointmentWaitlist } from '@/api/appointments'

export default {
  name: 'AppointmentWaitlist',
  components: {AppointmentDetailsModal, CreateAppointmentModal, Spinner},
  mixins: [Loading, UserMetadata, Util],
  data: () => ({
    now: undefined,
    showAppointmentDetailsModal: false,
    showCreateAppointmentModal: false,
    waitlist: undefined
  }),
  created() {
    this.now = this.$moment();
    getDropInAppointmentWaitlist().then(waitlist => {
      this.waitlist = waitlist;
      this.loaded();
    });
  },
  methods: {
    appointmentCheckIn(appointment) {
      checkIn(appointment.id).then(updated => {
        Object.assign(appointment, updated);
      });
    },
    cancelCreateAppointment() {
      this.showCreateAppointmentModal = false;
    },
    closeAppointmentDetailsModal() {
      this.showAppointmentDetailsModal = false;
    },
    createAppointment(details, sid, topics) {
      create(
        this.myDeptCodes(),
        this.user.name,
        this.title || this.isAdmin ? 'BOA Admin' : null,
        this.user.uid,
        details,
        sid,
        topics
      ).then(appointment => {
        this.showCreateAppointmentModal = false;
        this.waitlist.push(appointment);
      });
    }
  }
}
</script>

<style scoped>

</style>
