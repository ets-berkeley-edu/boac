<template>
  <v-alert
    :class="{'border-sm': showReason}"
    :color="appointment.status === 'cancelled' ? 'warning' : 'error'"
    density="compact"
    :icon="appointment.isRescheduled ? mdiCalendarClock : (appointment.isStudentNoShow ? mdiCalendarRemove : mdiCalendarMinus)"
    icon-size="21"
    min-width="7.6rem"
    role="none"
    variant="text"
  >
    <v-alert-title class="text-uppercase font-size-14">
      {{ appointment.isRescheduled ? 'Rescheduled' : (appointment.isStudentNoShow ? 'No Show' : 'Canceled') }}
    </v-alert-title>
    <div v-if="showReason" class="text-body pt-1">
      <span :id="`appointment-${appointment.id}-cancel-reason`">{{ appointment.cancelReason }}</span>
    </div>
  </v-alert>
</template>

<script setup>
import {mdiCalendarClock, mdiCalendarMinus, mdiCalendarRemove} from '@mdi/js'

defineProps({
  appointment: {
    required: true,
    type: Object
  },
  showReason: {
    required: false,
    type: Boolean
  }
})
</script>
