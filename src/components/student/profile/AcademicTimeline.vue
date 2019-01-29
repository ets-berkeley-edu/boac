<template>
  <div>
    <h2>Academic Timeline</h2>
    <div v-if="!isTimelineLoading">
      <div class="d-flex">
        <div>Filter Type:</div>
        <div>
          <b-btn :class="{ 'font-weight-bold': !filter }"
                 variant="link"
                 @click="filter = null">All</b-btn>
        </div>
        <div v-for="(label, type) in filterTypes" :key="type">
          <b-btn :class="{ 'font-weight-bold': type === filter }"
                 variant="link"
                 @click="filter = type">{{ label }}</b-btn>
        </div>
      </div>
      <div>
        <table>
          <tr class="sr-only">
            <th>Type</th>
            <th>Summary</th>
            <th>Date</th>
          </tr>
          <tr class="border-top border-bottom" v-for="(message, index) in (showAll ? messagesFiltered : slice(messagesFiltered, 0, 5))" :key="index">
            <td tabindex="-1" class="w-25">
              <div>
                {{ message.typeLabel }}
              </div>
            </td>
            <td tabindex="-1" :class="{ 'font-weight-bold': !message.dismissed }">
              <div>
                {{ message.text }}
              </div>
            </td>
            <td tabindex="-1">
              {{ message.date || '--' }}
            </td>
          </tr>
        </table>
      </div>
      <div v-if="messagesFiltered.length > 5">
        <b-btn id="show-hide-details-button"
               class="no-wrap pr-2 pt-0"
               variant="link"
               :aria-label="`showAll ? 'Hide previous messages' : 'Show previous messages'`"
               @click="showAll = !showAll">
          {{showAll ? 'Hide' : 'Show'}} Previous Messages
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Util from '@/mixins/Util';
import { getStudentAlerts } from '@/api/student';

export default {
  name: 'AcademicTimeline',
  mixins: [Util],
  props: {
    student: Object
  },
  data: () => ({
    isTimelineLoading: true,
    messages: undefined,
    filter: undefined,
    filterTypes: {
      alert: 'Alerts',
      degreeProgress: 'Reqs',
      hold: 'Holds'
    },
    showAll: false
  }),
  created() {
    this.messages = [];
    this.each(
      this.get(this.student, 'sisProfile.degreeProgress.requirements'),
      requirement => {
        this.messages.push(
          this.newMessage(
            'degreeProgress',
            `${requirement.name} ${requirement.status}`,
            true
          )
        );
        getStudentAlerts(this.student.sid).then(data => {
          const alertCategories = this.partition(data, ['alertType', 'hold']);
          this.each(alertCategories[0], alert => {
            this.messages.push(
              this.newMessage('alert', alert.message, alert.dismissed)
            );
          });
          this.each(alertCategories[1], alert => {
            this.messages.push(
              this.newMessage('hold', alert.message, alert.dismissed)
            );
          });
          this.isTimelineLoading = false;
        });
      }
    );
  },
  computed: {
    messagesFiltered() {
      return this.filter
        ? this.filterList(this.messages, ['type', this.filter])
        : this.messages;
    }
  },
  methods: {
    newMessage(type, text, dismissed, date) {
      const typeLabel = {
        alert: 'Alert',
        degreeProgress: 'Requirements',
        hold: 'Hold'
      }[type];
      return { type, typeLabel, text, dismissed, date };
    }
  }
};
</script>
