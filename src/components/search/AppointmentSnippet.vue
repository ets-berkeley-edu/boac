<template>
  <div
    :id="`appointment-search-result-${appointment.id}`"
    :class="{'demo-mode-blur': currentUser.inDemoMode}"
    class="advising-note-search-result"
  >
    <h3 v-if="appointment.student" class="advising-note-search-result-header">
      <router-link
        v-if="appointment.student.uid"
        :id="`appointment-link-to-student-${appointment.student.uid}`"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        :to="`${studentRoutePath(appointment.student.uid, currentUser.inDemoMode)}#appointment-${appointment.id}`"
        class="advising-note-search-result-header-link"
        v-html="`${appointment.student.firstName} ${appointment.student.lastName}`"
      />
      <span
        v-if="!appointment.student.uid"
        :id="`student-${appointment.student.sid}-has-no-uid`"
        class="font-weight-500"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        v-html="`${appointment.student.firstName} ${appointment.student.lastName}`"
      />
      ({{ appointment.student.sid }})
    </h3>
    <div v-if="!appointment.student">
      <h3 class="advising-note-search-result-header">
        <span class="font-weight-500">Appointment for SID {{ appointment.studentSid }}</span>
      </h3>
      <div>
        <i>No student record found.</i>
      </div>
    </div>
    <div
      :id="`appointment-search-result-snippet-${appointment.id}`"
      class="advising-note-search-result-snippet"
      v-html="appointment.detailsSnippet"
    >
    </div>
    <div :class="{'demo-mode-blur': currentUser.inDemoMode}" class="advising-note-search-result-footer">
      <span v-if="appointment.advisorName" :id="`appointment-search-result-advisor-${appointment.id}`">
        {{ appointment.advisorName }} -
      </span>
      <span v-if="createdAt">{{ DateTime.fromJSDate(createdAt).toFormat('MMM D, YYYY') }}</span>
    </div>
  </div>
</template>

<script setup>
import {DateTime} from 'luxon'
</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'AppointmentSnippet',
  mixins: [Context, Util],
  props: {
    appointment: {
      required: true,
      type: Object
    },
  },
  data: () => ({
    createdAt: undefined
  }),
  created() {
    const timestamp = this._get(this.appointment, 'createdAt')
    if (timestamp) {
      this.createdAt = DateTime.fromJSDate(timestamp).setZone(this.config.timezone)
    }
  }
}
</script>
