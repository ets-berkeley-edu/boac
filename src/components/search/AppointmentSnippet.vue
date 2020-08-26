<template>
  <div
    :id="`appointment-search-result-${appointment.id}`"
    :class="{'demo-mode-blur': $currentUser.inDemoMode}"
    class="advising-note-search-result">
    <h3 v-if="appointment.student" class="advising-note-search-result-header">
      <router-link
        :id="`appointment-link-to-student-${appointment.student.uid}`"
        :class="{'demo-mode-blur': $currentUser.inDemoMode}"
        :to="`${studentRoutePath(appointment.student.uid, $currentUser.inDemoMode)}#appointment-${appointment.id}`"
        class="advising-note-search-result-header-link"
        v-html="`${appointment.student.firstName} ${appointment.student.lastName}`"></router-link>
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
      v-html="appointment.detailsSnippet">
    </div>
    <div :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="advising-note-search-result-footer">
      <span v-if="appointment.advisorName" :id="`appointment-search-result-advisor-${appointment.id}`">
        {{ appointment.advisorName }} -
      </span>
      <span v-if="createdAt">{{ createdAt | moment('MMM D, YYYY') }}</span>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'AppointmentSnippet',
  mixins: [Context, Util],
  props: {
    appointment: Object,
  },
  data: () => ({
    createdAt: undefined
  }),
  created() {
    const timestamp = this.get(this.appointment, 'createdAt')
    if (timestamp) {
      this.createdAt = this.$moment(timestamp).tz(this.$config.timezone)
    }
  }
}
</script>
