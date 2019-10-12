<template>
  <div>
    <AppointmentDetailsModal
      v-if="showAppointmentDetailsModal"
      :appointment="appointment"
      :close="closeAppointmentDetailsModal"
      :check-in="appointmentCheckIn"
      :modal-header="student.name"
      :show-modal="showAppointmentDetailsModal" />
  </div>
</template>

<script>
import AppointmentDetailsModal from '@/components/appointment/AppointmentDetailsModal';
import { checkIn } from '@/api/appointments'

export default {
  name: 'DropInWaitlist',
  components: { AppointmentDetailsModal },
  data: () => ({
    showAppointmentDetailsModal: false
  }),
  methods: {
    appointmentCheckIn(appointment) {
      checkIn(appointment.id).then(updated => {
        Object.assign(appointment, updated);
      });
    },
    closeAppointmentDetailsModal() {
      this.showAppointmentDetailsModal = false;
    }
  }
}
</script>

<style scoped>

</style>
