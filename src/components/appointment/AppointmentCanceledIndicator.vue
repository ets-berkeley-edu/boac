<template>
  <v-alert
    class="align-center d-flex font-size-14 text-no-wrap text-uppercase"
    :color="appointment.status === 'cancelled' ? 'warning' : 'error'"
    density="compact"
    :icon="appointment.isRescheduled ? mdiCalendarClock : (appointment.isStudentNoShow ? mdiCalendarRemove : mdiCalendarMinus)"
    icon-size="21"
    min-width="7rem"
    role="none"
    variant="text"
  >
    {{ appointment.isRescheduled ? 'Rescheduled' : (appointment.isStudentNoShow ? 'No Show' : 'Canceled') }}
  </v-alert>
</template>

<script setup>
import {mdiCalendarClock, mdiCalendarMinus, mdiCalendarRemove} from '@mdi/js'

defineProps({
  appointment: {
    required: true,
    type: Object
  }
})
</script>
