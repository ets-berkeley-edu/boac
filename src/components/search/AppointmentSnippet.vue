<template>
  <div
    :id="`appointment-search-result-${appointment.id}`"
    class="advising-note-search-result"
    :class="{'demo-mode-blur': user.inDemoMode}">
    <h3 class="advising-note-search-result-header">
      <router-link
        :id="`appointment-link-to-student-${appointment.student.uid}`"
        class="advising-note-search-result-header-link"
        :class="{'demo-mode-blur': user.inDemoMode}"
        :to="`${studentRoutePath(appointment.student.uid, user.inDemoMode)}#appointment-${appointment.id}`"
        v-html="`${appointment.student.firstName} ${appointment.student.lastName}`"></router-link>
      ({{ appointment.student.sid }})
    </h3>
    <div
      :id="`appointment-search-result-snippet-${appointment.id}`"
      class="advising-note-search-result-snippet"
      v-html="appointment.detailsSnippet">
    </div>
    <div class="advising-note-search-result-footer" :class="{'demo-mode-blur': user.inDemoMode}">
      <span v-if="appointment.advisorName" :id="`appointment-search-result-advisor-${appointment.id}`">
        {{ appointment.advisorName }} -
      </span>
      <span v-if="createdAt">{{ createdAt | moment('MMM D, YYYY') }}</span>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'AppointmentSnippet',
  mixins: [Context, UserMetadata, Util],
  props: {
    appointment: Object,
  },
  data: () => ({
    createdAt: undefined
  }),
  created() {
    const timestamp = this.get(this.appointment, 'createdAt');
    if (timestamp) {
      this.createdAt = this.$moment(timestamp).tz(this.timezone);
    }
  }
};
</script>
