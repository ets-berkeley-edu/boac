<template>
  <div v-if="!isTimelineLoading">
    <h2 class="student-section-header">Academic Timeline</h2>
    <div id="screen-reader-alert" class="sr-only" aria-live="polite">{{ screenReaderAlert }}</div>
    <div class="d-flex mt-3 mb-3">
      <div class="align-self-center mr-3">Filter Type:</div>
      <div>
        <b-btn
          id="timeline-tab-all"
          class="tab pl-2 pr-2"
          :class="{ 'tab-active text-white': !filter, 'tab-inactive text-dark': filter }"
          variant="link"
          @click="filter = null">
          All
        </b-btn>
      </div>
      <div v-for="type in keys(filterTypes)" :key="type">
        <b-btn
          :id="`timeline-tab-${type}`"
          class="tab ml-2 pl-2 pr-2 text-center"
          :class="{
            'tab-active text-white': type === filter && countsPerType[type],
            'tab-inactive text-dark': type !== filter && countsPerType[type],
            'tab-disabled text-muted': !countsPerType[type]
          }"
          :aria-label="`${filterTypes[type].name}s tab`"
          variant="link"
          :disabled="!countsPerType[type]"
          @click="filter = type">
          {{ filterTypes[type].tab }}
        </b-btn>
      </div>
    </div>
    <div v-if="!countPerActiveTab" class="pb-4 pl-2">
      <span id="zero-messages" class="messages-none">
        <span v-if="filter">No {{ filterTypes[filter].name.toLowerCase() }}s</span>
        <span v-if="!filter">None</span>
      </span>
    </div>
    <div v-if="countPerActiveTab">
      <table class="w-100">
        <tr class="sr-only">
          <th>Type</th>
          <th>Summary</th>
          <th>Date</th>
        </tr>
        <tr
          v-for="(message, index) in messagesInView"
          :key="index"
          class="message-row border-top border-bottom"
          :class="{ 'message-row-read': message.read }">
          <td class="column-pill align-top p-2">
            <div
              :id="`timeline-tab-${activeTab}-pill-${index}`"
              class="pill text-center text-uppercase text-white"
              :class="`pill-${message.type}`"
              tabindex="0">
              <span class="sr-only">Message of type </span>{{ filterTypes[message.type].name }}
            </div>
          </td>
          <td
            class="column-message align-top"
            :class="{ 'font-weight-bold': !message.read }">
            <div
              :id="`timeline-tab-${activeTab}-message-${index}`"
              :class="{
                'align-top message-open': includes(openMessages, message.transientId),
                'truncate': !includes(openMessages, message.transientId),
                'img-blur': user.inDemoMode && message.type === 'note'
              }"
              tabindex="0"
              @keyup.enter="toggle(message)"
              @click="toggle(message)">
              <i v-if="message.status === 'Satisfied'" class="requirements-icon fas fa-check text-success"></i>
              <i v-if="message.status === 'Not Satisfied'" class="requirements-icon fas fa-exclamation text-icon-exclamation"></i>
              <i v-if="message.status === 'In Progress'" class="requirements-icon fas fa-clock text-icon-clock"></i>
              <span v-html="message.message"></span>
            </div>
          </td>
          <td class="message-date align-top">
            <div
              :id="`timeline-tab-${activeTab}-date-${index}`"
              class="pt-2 pr-2 text-nowrap">
              <span v-if="message.updatedAt || message.createdAt"><span class="sr-only">Last updated on </span>{{ parseDatetime(message.updatedAt || message.createdAt) }}</span>
              <span
                v-if="!message.updatedAt && !message.createdAt"
                class="sr-only"
                tabindex="0">No last-updated date</span>
            </div>
          </td>
        </tr>
      </table>
    </div>
    <div v-if="countPerActiveTab > defaultShowPerTab" class="text-center pt-2">
      <b-btn
        :id="`timeline-tab-${activeTab}-previous-messages`"
        class="no-wrap pr-2 pt-0"
        variant="link"
        :aria-label="isShowingAll ? 'Hide previous messages' : 'Show previous messages'"
        @click="isShowingAll = !isShowingAll">
        <i
          :class="{
            'fas fa-caret-up': isShowingAll,
            'fas fa-caret-right': !isShowingAll
          }"></i>
        {{ isShowingAll ? 'Hide' : 'Show' }} Previous Messages
      </b-btn>
    </div>
  </div>
</template>

<script>
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { dismissStudentAlert } from '@/api/student';
import { format as formatDate, parse as parseDate } from 'date-fns';
import { markRead } from '@/api/notes';

export default {
  name: 'AcademicTimeline',
  mixins: [UserMetadata, Util],
  props: {
    student: Object
  },
  data: () => ({
    countsPerType: undefined,
    defaultShowPerTab: 5,
    filter: undefined,
    filterTypes: {
      note: {
        name: 'Advising Note',
        tab: 'Notes'
      },
      alert: {
        name: 'Alert',
        tab: 'Alerts'
      },
      hold: {
        name: 'Hold',
        tab: 'Holds'
      },
      requirement: {
        name: 'Requirement',
        tab: 'Reqs'
      }
    },
    isTimelineLoading: true,
    messages: undefined,
    openMessages: [],
    now: new Date(),
    isShowingAll: false,
    screenReaderAlert: undefined
  }),
  computed: {
    activeTab() {
      return this.filter || 'all';
    },
    countPerActiveTab() {
      return this.filter
        ? this.countsPerType[this.filter]
        : this.size(this.messages);
    },
    messagesInView() {
      const filtered = this.messagesPerType(this.filter);
      return this.isShowingAll
        ? filtered
        : this.slice(filtered, 0, this.defaultShowPerTab);
    }
  },
  watch: {
    filter() {
      this.screenReaderAlert = this.describeTheActiveTab();
      this.openMessages = [];
    },
    isShowingAll() {
      this.screenReaderAlert = this.describeTheActiveTab();
    }
  },
  created() {
    this.messages = [];
    this.countsPerType = {};
    this.each(this.keys(this.filterTypes), (type, typeIndex) => {
      let notifications = this.student.notifications[type];
      this.countsPerType[type] = this.size(notifications);
      this.each(notifications, (message, index) => {
        this.messages.push(message);
        // Unique message ids are not guaranteed. Here we generate a (transient) primary key.
        message.transientId = typeIndex * 1000 + index;
      });
    });
    this.messages.sort((m1, m2) => {
      let d1 = m1.updatedAt || m1.createdAt;
      let d2 = m2.updatedAt || m2.createdAt;
      if (d1 && d2) {
        return d2.localeCompare(d1);
      } else if (!d1 && !d2) {
        return m2.transientId - m1.transientId;
      } else {
        return d1 ? -1 : 1;
      }
    });
    this.screenReaderAlert = 'Academic Timeline has loaded';
    this.isTimelineLoading = false;
  },
  methods: {
    describeTheActiveTab() {
      const inViewCount =
        this.isShowAll || this.countPerActiveTab <= this.defaultShowPerTab
          ? this.countPerActiveTab
          : this.defaultShowPerTab;
      let noun = this.filter
        ? this.filterTypes[this.filter].name.toLowerCase()
        : 'message';
      const pluralize = this.$options.filters.pluralize(noun, inViewCount);
      return this.isShowingAll && inViewCount > this.defaultShowPerTab
        ? `Showing all ${pluralize}`
        : `Showing ${pluralize}`;
    },
    id(rowIndex) {
      return `timeline-tab-${this.activeTab}-message-${rowIndex}`;
    },
    messagesPerType(type) {
      return type
        ? this.filterList(this.messages, ['type', type])
        : this.messages;
    },
    parseDatetime(datetime) {
      let date = datetime && parseDate(datetime);
      if (date) {
        const dateFormat =
          date.getFullYear() === this.now.getFullYear()
            ? 'MMM DD'
            : 'MMM DD, YYYY';
        date = formatDate(date, dateFormat);
      }
      return date;
    },
    toggle(message) {
      if (this.includes(this.openMessages, message.transientId)) {
        this.openMessages = this.remove(
          this.openMessages,
          id => id !== message.transientId
        );
      } else {
        this.openMessages.push(message.transientId);
      }
      if (!message.read) {
        message.read = true;
        if (this.includes(['alert', 'hold'], message.type)) {
          dismissStudentAlert(message.id);
        } else if (message.type === 'note') {
          markRead(message.id);
        }
      }
    }
  }
};
</script>

<style scoped>
.message-date {
  text-align: right;
  width: 1%;
}
.column-message {
  max-width: 1px;
  padding: 10px;
  vertical-align: middle;
}
.column-pill {
  white-space: nowrap;
  width: 130px;
}
.messages-none {
  font-size: 18px;
  font-weight: 500;
}
.message-open {
  min-height: 40px;
}
.message-row:active,
.message-row:focus,
.message-row:hover {
  background-color: #e3f5ff;
}
.message-row-read {
  background-color: #f9f9f9;
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
.pill-hold {
  width: 60px;
  background-color: #bc74fe;
}
.pill-note {
  width: 120px;
  background-color: #999;
}
.pill-requirement {
  width: 120px;
  background-color: #93c165;
}
.requirements-icon {
  width: 20px;
}
.tab {
  border-radius: 5px;
  font-size: 10px;
  height: 22px;
}
.tab-active {
  background-color: #555;
}
.tab-active:active,
.tab-active:focus,
.tab-active:hover {
  background-color: #444;
}
.tab-disabled {
  background-color: #ccc;
}
.tab-inactive {
  background-color: #eee;
}
.tab-inactive:hover,
.tab-inactive:hover,
.tab-inactive:hover {
  background-color: #ddd;
}
.text-icon-clock {
  color: #8bbdda;
}
.text-icon-exclamation {
  color: #f0ad4e;
}
.truncate {
  height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
