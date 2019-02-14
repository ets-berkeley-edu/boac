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
        <b-btn :id="`timeline-tab-${type}`"
               class="tab ml-2 pl-2 pr-2 text-center"
               :class="{ 'tab-active text-white': type === filter, 'tab-inactive text-dark': type !== filter }"
               :aria-label="`${filterTypes[type].name}s tab`"
               variant="link"
               @click="filter = type">{{ filterTypes[type].tab }}</b-btn>
      </div>
    </div>
    <div class="pb-4 pl-2" v-if="!countPerActiveTab">
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
        <tr class="message-row border-top border-bottom"
            :class="{ 'message-row-read': message.read }"
            v-for="(message, index) in messagesInView"
            :key="index">
          <td class="column-pill align-top p-2">
            <div :id="`timeline-tab-${activeTab}-pill-${index}`"
                 class="pill text-center text-uppercase text-white"
                 :class="`pill-${message.type}`"
                 tabindex="0">
              <span class="sr-only">Message of type </span>{{ filterTypes[message.type].name }}
            </div>
          </td>
          <td class="column-message align-top"
              :class="{ 'font-weight-bold': !message.read }">
            <div :id="`timeline-tab-${activeTab}-message-${index}`"
                  :class="{
                    'align-top': includes(openMessages, message.transientId),
                    'message-ellipsis': !includes(openMessages, message.transientId)
                  }"
                  tabindex="0"
                  @keyup.enter="toggle(message)"
                  @click="toggle(message)">
              <i class="requirements-icon fas fa-check text-success" v-if="message.status === 'Satisfied'"></i>
              <i class="requirements-icon fas fa-exclamation text-icon-exclamation" v-if="message.status === 'Not Satisfied'"></i>
              <i class="requirements-icon fas fa-clock text-icon-clock" v-if="message.status === 'In Progress'"></i>
              {{ message.message }}
            </div>
          </td>
          <td class="message-date align-top">
            <div :id="`timeline-tab-${activeTab}-date-${index}`"
                 class="pt-2 pr-2 text-nowrap">
              <span v-if="message.updatedAt || message.createdAt"><span class="sr-only">Last updated on </span>{{ parseDatetime(message.updatedAt || message.createdAt) }}</span>
              <span class="sr-only"
                    tabindex="0"
                    v-if="!message.updatedAt && !message.createdAt">No last-updated date</span>
            </div>
          </td>
        </tr>
      </table>
    </div>
    <div class="text-center pt-2" v-if="countPerActiveTab > defaultShowPerTab">
      <b-btn :id="`timeline-tab-${activeTab}-previous-messages`"
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
import { dismissStudentAlert } from '@/api/student';
import { format as formatDate, parse as parseDate } from 'date-fns';

export default {
  name: 'AcademicTimeline',
  mixins: [Util],
  props: {
    student: Object
  },
  data: () => ({
    defaultShowPerTab: 5,
    distinctTypes: undefined,
    filter: undefined,
    filterTypes: {
      alert: {
        name: 'Alert',
        tab: 'Alerts'
      },
      requirement: {
        name: 'Requirement',
        tab: 'Reqs'
      },
      hold: {
        name: 'Hold',
        tab: 'Holds'
      }
    },
    isTimelineLoading: true,
    messages: undefined,
    openMessages: [],
    now: new Date(),
    isShowingAll: false,
    screenReaderAlert: undefined
  }),
  created() {
    this.messages = [];
    this.each(this.keys(this.filterTypes), (type, typeIndex) => {
      this.each(this.student.notifications[type], (message, index) => {
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
    this.distinctTypes = this.uniq(this.map(this.messages, 'type'));
    this.screenReaderAlert = 'Academic Timeline has loaded';
    this.isTimelineLoading = false;
  },
  computed: {
    activeTab() {
      return this.filter || 'all';
    },
    countPerActiveTab() {
      return this.size(this.messagesPerActiveTab());
    },
    messagesInView() {
      const filtered = this.messagesPerActiveTab();
      return this.isShowingAll
        ? filtered
        : this.slice(filtered, 0, this.defaultShowPerTab);
    }
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
    messagesPerActiveTab() {
      return this.filter
        ? this.filterList(this.messages, ['type', this.filter])
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
        }
      }
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
.message-row-read {
  background-color: #f9f9f9;
}
.message-ellipsis {
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
.pill-requirement {
  width: 130px;
  background-color: #93c165;
}
.pill-hold {
  width: 60px;
  background-color: #bc74fe;
}
.requirements-icon {
  width: 20px;
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
.text-icon-clock {
  color: #8bbdda;
}
.text-icon-exclamation {
  color: #f0ad4e;
}
</style>
