<template>
  <div v-if="!isTimelineLoading">
    <h2 class="student-section-header">Academic Timeline</h2>
    <div id="screen-reader-alert" class="sr-only" aria-live="polite">{{ screenReaderAlert }}</div>
    <div class="d-flex mt-3 mb-3" v-if="size(distinctTypes) > 1">
      <div class="align-self-center mr-3">Filter Type:</div>
      <div>
        <b-btn id="timeline-tab-all"
               class="tab pl-2 pr-2"
               :class="{ 'tab-active text-white': !filter, 'tab-inactive text-dark': filter }"
               variant="link"
               @click="filter = null">All</b-btn>
      </div>
      <div v-for="type in distinctTypes" :key="type">
        <b-btn :id="`timeline-tab-${filter}`"
               class="tab ml-2 pl-2 pr-2 text-center"
               :class="{ 'tab-active text-white': type === filter, 'tab-inactive text-dark': type !== filter }"
               variant="link"
               @click="filter = type">{{ filterTypes[type] }}</b-btn>
      </div>
    </div>
    <div class="pb-4 pl-2" v-if="!size(messagesFiltered)">
      <span id="zero-messages" class="messages-none">
        <span v-if="filter">No {{ filterLabel }}</span>
        <span v-if="!filter">None</span>
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
            :class="{'message-row-dismissed': message.dismissed}"
            v-for="(message, index) in messagesInView"
            :key="index">
          <td class="column-pill align-top p-2">
            <div :id="`timeline-tab-${filter || 'all'}-pill-${index}`"
                 class="pill text-center text-uppercase text-white"
                 :class="`pill-${message.type}`"
                 tabindex="0">
              <span class="sr-only">Message of type </span>{{ message.typeLabel }}
            </div>
          </td>
          <td class="column-message align-top"
              :class="{ 'font-weight-bold': !message.dismissed }">
            <div :id="`timeline-tab-${filter || 'all'}-message-${index}`"
                 :class="{
                   'align-top': message.openOnTab === (filter || 'all'),
                   'message-text-ellipsis': message.openOnTab !== (filter || 'all')
                 }"
                 tabindex="0"
                 role="link"
                 @keyup.enter="toggle(message)"
                 @click="toggle(message)">
              <i class="fas fa-check text-success" v-if="message.status === 'Satisfied'"></i>
              {{ message.text }}
            </div>
          </td>
          <td class="message-date align-top pt-2">
            <div :id="`timeline-tab-${filter || 'all'}-date-${index}`"
                 class="text-nowrap"
                 v-if="message.updatedAt">
              <span tabindex="0"><span class="sr-only">Last updated on </span>{{ message.updatedAt }}</span>
            </div>
          </td>
        </tr>
      </table>
    </div>
    <div class="text-center pt-2" v-if="messagesFiltered.length > 5">
      <b-btn :id="`timeline-tab-${filter || 'all'}-previous-messages`"
             class="no-wrap pr-2 pt-0"
             variant="link"
             :aria-label="`isShowingAll ? 'Hide previous messages' : 'Show previous messages'`"
             @click="isShowingAll = !isShowingAll">
        <i :class="{
          'fas fa-caret-up': isShowingAll,
          'fas fa-caret-right': !isShowingAll
        }"></i>
        {{ isShowingAll ? 'Hide' : 'Show' }} Previous Messages
      </b-btn>
    </div>
  </div>
</template>

<script>
import Util from '@/mixins/Util';
import { dismissStudentAlert, getStudentAlerts } from '@/api/student';
import { format as formatDate, parse as parseDate } from 'date-fns';

export default {
  name: 'AcademicTimeline',
  mixins: [Util],
  props: {
    student: Object
  },
  data: () => ({
    distinctTypes: undefined,
    filter: undefined,
    filterTypes: {
      alert: 'Alerts',
      degreeProgress: 'Reqs',
      hold: 'Holds'
    },
    isTimelineLoading: true,
    messages: undefined,
    now: new Date(),
    isShowingAll: false,
    screenReaderAlert: undefined
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
            true,
            null,
            requirement.status
          )
        );
      }
    );
    getStudentAlerts(this.student.sid).then(data => {
      const alertCategories = this.partition(data, ['alertType', 'hold']);
      this.each({ hold: 0, alert: 1 }, (arrayIndex, alertType) => {
        this.each(alertCategories[arrayIndex], alert => {
          this.messages.push(
            this.newMessage(
              alert.id,
              alertType,
              alert.message,
              alert.dismissed,
              alert.updatedAt
            )
          );
        });
      });
      this.distinctTypes = this.uniq(this.map(this.messages, 'type'));
      this.isTimelineLoading = false;
      this.screenReaderAlert = 'Academic Timeline has loaded';
    });
  },
  computed: {
    filterLabel() {
      return this.filter
        ? this.filter === 'degreeProgress'
          ? 'requirements'
          : this.filterTypes[this.filter].toLowerCase()
        : null;
    },
    messagesFiltered() {
      return this.filter
        ? this.filterList(this.messages, ['type', this.filter])
        : this.messages;
    },
    messagesInView() {
      return this.isShowingAll
        ? this.messagesFiltered
        : this.slice(this.messagesFiltered, 0, 5);
    }
  },
  methods: {
    describeTheActiveTab() {
      const inViewCount = this.size(this.messagesInView);
      return `Showing ${
        this.isShowingAll ? 'all' : 'the first'
      } ${inViewCount} ${this.filter ? this.filterLabel : 'messages'}.`;
    },
    newMessage(id, type, text, dismissed, updatedAt, status) {
      const typeLabel = {
        alert: 'Alert',
        degreeProgress: 'Requirements',
        hold: 'Hold'
      }[type];
      let date = updatedAt && parseDate(updatedAt);
      if (date) {
        const dateFormat =
          date.getFullYear() === this.now.getFullYear()
            ? 'MMM DD'
            : 'MMM DD, YYYY';
        date = formatDate(date, dateFormat);
      }
      return {
        id,
        type,
        typeLabel,
        text,
        dismissed,
        updatedAt: date,
        openOnTab: undefined,
        status
      };
    },
    toggle(message) {
      message.openOnTab = message.openOnTab ? null : this.filter || 'all';
      const isAlert = this.includes(['alert', 'hold'], message.type);
      if (isAlert && !message.dismissed) {
        message.dismissed = true;
        dismissStudentAlert(message.id);
      }
    }
  },
  watch: {
    filter() {
      this.screenReaderAlert = this.describeTheActiveTab();
    },
    isShowingAll() {
      this.screenReaderAlert = this.describeTheActiveTab();
    }
  }
};
</script>

<style scoped>
.message-date {
  max-width: 80px;
  width: 80px;
}
.column-message {
  max-width: 1px;
  padding: 10px;
  vertical-align: middle;
}
.column-pill {
  white-space: nowrap;
  width: 146px;
}
.messages-none {
  font-size: 18px;
  font-weight: 500;
}
.message-row:active,
.message-row:focus,
.message-row:hover {
  background-color: #e3f5ff;
}
.message-row-dismissed {
  background-color: #f9f9f9;
}
.message-text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pill {
  border-radius: 5px;
  font-size: 14px;
  height: 26px;
  padding: 3px 5px 0 5px;
}
.pill-alert {
  width: 60px;
  background-color: #eb9d3e;
}
.pill-degreeProgress {
  width: 130px;
  background-color: #93c165;
}
.pill-hold {
  width: 60px;
  background-color: #bc74fe;
}
.tab {
  border-radius: 5px;
  font-size: 16px;
  font-weight: 800;
  height: 40px;
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
</style>
