<template>
  <div>
    <h2>Academic Timeline</h2>
    <div v-if="!isTimelineLoading">
      <div class="d-flex mt-3 mb-3">
        <div class="align-self-center mr-3">Filter Type:</div>
        <div>
          <b-btn id="student-timeline-filter-all"
                 class="tab pl-2 pr-2"
                 :class="{ 'tab-active text-white': !filter, 'tab-inactive text-dark': filter }"
                 variant="link"
                 @click="filter = null">All</b-btn>
        </div>
        <div v-for="(label, type) in filterTypes" :key="type">
          <b-btn :id="`student-timeline-filter-${filter}`"
                 class="tab ml-2 pl-2 pr-2 text-center"
                 :class="{ 'tab-active text-white': type === filter, 'tab-inactive text-dark': type !== filter }"
                 variant="link"
                 @click="filter = type">{{ label }}</b-btn>
        </div>
      </div>
      <div class="pb-4 pl-2" v-if="!size(messagesFiltered)">
        <span class="messages-none">
          <span v-if="!filter">None</span>
          <span v-if="filter === 'degreeProgress'">No requirements</span>
          <span v-if="filter && filter !== 'degreeProgress'">No {{ filterTypes[filter].toLowerCase() }}</span>
        </span>
      </div>
      <div v-if="size(messagesFiltered)">
        <table class="w-100">
          <tr class="sr-only">
            <th>Type</th>
            <th>Summary</th>
            <th>Date</th>
          </tr>
          <tr class="message-row border-top border-bottom"
              :class="{'message-dismissed-row': message.dismissed}"
              v-for="(message, index) in (showAll ? messagesFiltered : slice(messagesFiltered, 0, 5))"
              :key="index">
            <td class="messages-column-label" tabindex="-1">
              <div class="pill text-center text-uppercase text-white" :class="`pill-${message.type}`">
                {{ message.typeLabel }}
              </div>
            </td>
            <td tabindex="-1"
                class="message-text"
                :class="{ 'font-weight-bold': !message.dismissed }">
              <div role="link"
                   @click="dismiss(message)">
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
import { dismissStudentAlert, getStudentAlerts } from '@/api/student';

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
            null,
            'degreeProgress',
            `${requirement.name} ${requirement.status}`,
            true
          )
        );
        getStudentAlerts(this.student.sid).then(data => {
          const alertCategories = this.partition(data, ['alertType', 'hold']);
          this.each(alertCategories[0], alert => {
            this.messages.push(
              this.newMessage(alert.id, 'alert', alert.message, alert.dismissed)
            );
          });
          this.each(alertCategories[1], alert => {
            this.messages.push(
              this.newMessage(alert.id, 'hold', alert.message, alert.dismissed)
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
    dismiss(message) {
      const isAlert = this.includes(['alert', 'hold'], message.type);
      if (isAlert) {
        dismissStudentAlert(message.id).then(() => {
          message.dismissed = true;
        });
      } else {
        // TODO: The Notes feature will do something more advanced here.
        message.dismissed = true;
      }
    },
    newMessage(id, type, text, dismissed, date) {
      const typeLabel = {
        alert: 'Alert',
        degreeProgress: 'Requirements',
        hold: 'Hold'
      }[type];
      return { id, type, typeLabel, text, dismissed, date };
    }
  }
};
</script>

<style scoped>
.message-text {
  padding: 10px 10px 10px 0;
}
.messages-none {
  font-size: 18px;
  font-weight: 500;
}
.messages-column-label {
  width: 1%;
  padding-right: 10px;
  white-space: nowrap;
}
.message-dismissed-row {
  background-color: #f9f9f9;
}
.message-row:active,
.message-row:focus,
.message-row:hover {
  background-color: #e3f5ff;
}
.pill {
  border-radius: 5px;
  font-size: 14px;
  height: 30px;
  padding: 4px 10px 0 10px;
}
.pill-hold {
  width: 60px;
  background-color: #bc74fe;
}
.pill-alert {
  width: 60px;
  background-color: #eb9d3e;
}
.pill-degreeProgress {
  width: 130px;
  background-color: #93c165;
}
.tab-active {
  background-color: #555;
}
.tab-active:active,
.tab-active:focus,
.tab-active:hover {
  background-color: #444;
}
.tab-inactive {
  background-color: #eee;
}
.tab-inactive:hover,
.tab-inactive:hover,
.tab-inactive:hover {
  background-color: #ddd;
}
.tab {
  border-radius: 5px;
  font-size: 16px;
  font-weight: 800;
  height: 40px;
}
</style>
