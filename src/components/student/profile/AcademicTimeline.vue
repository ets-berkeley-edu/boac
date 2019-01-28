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
          <tr class="border-top border-bottom" v-for="(message, index) in messagesFiltered" :key="index">
            <td class="w-25">
              {{ message.typeLabel }}
            </td>
            <td class="w-50">
              {{ message.text }}
            </td>
            <td>
              {{ message.date || '--' }}
            </td>
          </tr>
        </table>
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
    }
  }),
  created() {
    this.messages = [];
    this.each(
      this.get(this.student, 'sisProfile.degreeProgress.requirements'),
      requirement => {
        this.messages.push(
          this.newMessage(
            'degreeProgress',
            `${requirement.name} ${requirement.status}`
          )
        );
        getStudentAlerts(this.student.sid).then(data => {
          const alerts = this.get(data, 'shown', []).concat(
            this.get(data, 'dismissed', [])
          );
          const partitions = this.partition(alerts, ['alertType', 'hold']);
          this.each(partitions[0], alert => {
            this.messages.push(this.newMessage('alert', alert.message));
          });
          this.each(partitions[1], alert => {
            this.messages.push(this.newMessage('hold', alert.message));
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
    newMessage(type, text, date) {
      const typeLabel = {
        alert: 'Alert',
        degreeProgress: 'Requirements',
        hold: 'Hold'
      }[type];
      return { type, typeLabel, text, date };
    }
  }
};
</script>
