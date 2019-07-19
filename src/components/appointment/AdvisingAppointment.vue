<template>
  <div>
    <div>{{ appointment.summary }} <span v-if="isOpen && appointment.recurringEventId">(Recurring)</span></div>
    <div>Created by: {{ appointment.creator.email }}</div>
    <div>Status: {{ appointment.status }}</div>
    <div>{{ appointment.start }} to {{ appointment.end }}</div>
    <div>
      <a
        :id="`link-to-appointment-hangout-${appointment.id}`"
        :href="appointment.hangoutLink"
        target="_blank"
        aria-label="Open in new window">Google Hangout <font-awesome icon="external-link-alt" class="pr-1" /></a>
    </div>
    <div v-if="appointment.link">
      See
      <a
        :id="`link-to-appointment.link-${appointment.id}`"
        :href="appointment.link"
        target="_blank"
        aria-label="Open in new window">appointment in Google Calendar <font-awesome icon="external-link-alt" class="pr-1" /></a>.
    </div>
    <div v-if="size(appointment.attendees) > 1" class="mt-2">
      Attendees
      <ul>
        <li v-for="attendee in appointment.attendees" :key="attendee.email" class="pb-1">
          <div v-if="attendee.displayName">Name: {{ attendee.displayName }}</div>
          <div v-if="attendee.email">Email: {{ attendee.email }}</div>
          <div v-if="attendee.responseStatus">Status: {{ attendee.responseStatus }}</div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingAppointment',
  mixins: [Util],
  props: {
    isOpen: Boolean,
    appointment: Object
  }
}
</script>
