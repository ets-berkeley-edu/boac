<template>
  <div v-if="!isTimelineLoading">
    <div class="d-flex justify-content-between flex-wrap mb-2">
      <div>
        <h2 class="student-section-header">Academic Timeline</h2>
        <div class="d-flex mt-1 mb-1">
          <div class="align-self-center mr-2">Filter Type:</div>
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
      </div>
      <div v-if="!user.isAdmin">
        <NewNoteModal
          :disable="!!editingNoteId || includes(['batch', 'minimized', 'open'], newNoteMode)"
          :student="student"
          :on-submit="onSubmitAdvisingNote"
          :on-successful-create="onCreateAdvisingNote" />
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
          <th>Has attachment?</th>
          <th>Date</th>
        </tr>
        <tr v-if="creatingNewNote">
          <td class="column-pill align-top p-2">
            <div class="pill text-center text-uppercase text-white pill-note" tabindex="0">
              <span class="sr-only">Creating new</span> advising note
            </div>
          </td>
          <td class="column-message">
            <font-awesome icon="sync" spin />
          </td>
        </tr>
        <tr
          v-for="(message, index) in (isShowingAll ? messagesPerType(filter) : slice(messagesPerType(filter), 0, defaultShowPerTab))"
          :id="`message-row-${message.id}`"
          :key="index"
          class="message-row border-top border-bottom"
          :class="{ 'message-row-read': message.read }"
          :tabindex="includes(openMessages, message.transientId) ? 0 : -1">
          <td class="column-pill align-top p-2">
            <div
              :id="`timeline-tab-${activeTab}-pill-${index}`"
              class="pill text-center text-uppercase text-white"
              :class="`pill-${message.type}`"
              tabindex="0">
              <span class="sr-only">Message of type </span>{{ filterTypes[message.type].name }}
            </div>
            <div
              v-if="isEditable(message) && !editingNoteId && isNil(newNoteMode) && includes(openMessages, message.transientId)"
              class="mt-2">
              <div v-if="user.uid === message.author.uid">
                <b-btn
                  :id="`edit-note-${message.id}-button`"
                  variant="link"
                  class="p-0 edit-note-button"
                  @keypress.enter.stop="editNote(message)"
                  @click.stop="editNote(message)">
                  Edit Note
                </b-btn>
              </div>
              <div v-if="user.isAdmin">
                <b-btn
                  id="delete-note-button"
                  variant="link"
                  class="p-0 edit-note-button"
                  @keypress.enter.stop="deleteNote(message)"
                  @click.stop="deleteNote(message)">
                  Delete Note
                </b-btn>
              </div>
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
              :tabindex="includes(openMessages, message.transientId) ? -1 : 0"
              @keyup.enter="open(message)"
              @click="open(message)">
              <span v-if="message.transientId !== editingNoteId" class="when-message-closed sr-only">Open message</span>
              <font-awesome v-if="message.status === 'Satisfied'" icon="check" class="requirements-icon text-success" />
              <font-awesome v-if="message.status === 'Not Satisfied'" icon="exclamation" class="requirements-icon text-icon-exclamation" />
              <font-awesome v-if="message.status === 'In Progress'" icon="clock" class="requirements-icon text-icon-clock" />
              <span v-if="message.type !== 'note'">{{ message.message }}</span>
              <AdvisingNote
                v-if="message.type === 'note' && message.transientId !== editingNoteId"
                :delete-note="deleteNote"
                :edit-note="editNote"
                :note="message"
                :after-saved="afterNoteUpdated"
                :is-open="includes(openMessages, message.transientId)" />
              <EditAdvisingNote
                v-if="message.type === 'note' && message.transientId === editingNoteId"
                :after-cancelled="afterEditCancel"
                :note="message"
                :after-saved="afterNoteUpdated" />
              <div v-if="includes(openMessages, message.transientId) && message.transientId !== editingNoteId" class="text-center close-message">
                <b-btn
                  :id="`timeline-tab-${activeTab}-close-message`"
                  class="no-wrap"
                  variant="link"
                  @keyup.enter.stop="close(message)"
                  @click.stop="close(message)">
                  <font-awesome icon="times-circle" class="font-size-24" />
                  Close Message
                </b-btn>
              </div>
            </div>
          </td>
          <td class="column-right align-top pt-1 pr-1">
            <font-awesome v-if="size(message.attachments)" icon="paperclip" class="mt-2" />
            <span class="sr-only">{{ size(message.attachments) ? 'Yes' : 'No' }}</span>
          </td>
          <td class="column-right align-top">
            <div
              :id="`timeline-tab-${activeTab}-date-${index}`"
              class="pt-2 pr-2 text-nowrap">
              <div v-if="!includes(openMessages, message.transientId) || message.type !== 'note'">
                <TimelineDate
                  :id="`collapsed-${message.type}-${message.id}-created-at`"
                  :date="message.updatedAt || message.createdAt"
                  :include-time-of-day="false"
                  sr-prefix="Last updated on" />
              </div>
              <div v-if="includes(openMessages, message.transientId) && message.type === 'note'">
                <div v-if="message.createdAt" :class="{'mb-2': !displayUpdatedAt(message)}">
                  <div class="text-muted">Created:</div>
                  <TimelineDate
                    :id="`expanded-${message.type}-${message.id}-created-at`"
                    :date="message.createdAt"
                    :include-time-of-day="message.createdAt.length > 10" />
                </div>
                <div v-if="displayUpdatedAt(message)">
                  <div class="mt-2 text-muted">Updated:</div>
                  <TimelineDate
                    :id="`expanded-${message.type}-${message.id}-updated-at`"
                    :date="message.updatedAt"
                    :include-time-of-day="message.updatedAt.length > 10"
                    class="mb-2" />
                </div>
                <div class="text-muted">
                  <router-link
                    v-if="editingNoteId !== message.transientId"
                    :id="`advising-note-permalink-${message.id}`"
                    :to="`#${message.id}`"
                    @click.native="scrollToPermalink(message.id)">
                    Permalink <font-awesome icon="link" />
                  </router-link>
                </div>
              </div>
              <span
                v-if="!message.updatedAt && !message.createdAt"
                class="sr-only"
                tabindex="0">No last-updated date</span>
            </div>
          </td>
        </tr>
      </table>
    </div>
    <div v-if="countPerActiveTab > defaultShowPerTab" class="text-center">
      <b-btn
        :id="`timeline-tab-${activeTab}-previous-messages`"
        class="no-wrap pr-2 pt-0"
        variant="link"
        :aria-label="isShowingAll ? 'Hide previous messages' : 'Show previous messages'"
        @click="isShowingAll = !isShowingAll">
        <font-awesome :icon="isShowingAll ? 'caret-up' : 'caret-right'" />
        {{ isShowingAll ? 'Hide' : 'Show' }} Previous Messages
      </b-btn>
    </div>
    <AreYouSureModal
      v-if="showDeleteConfirmModal"
      button-label-confirm="Delete"
      :function-cancel="cancelTheDelete"
      :function-confirm="deleteConfirmed"
      modal-header="Delete note"
      :modal-body="deleteConfirmModalBody"
      :show-modal="showDeleteConfirmModal" />
  </div>
</template>

<script>
import AdvisingNote from "@/components/note/AdvisingNote";
import AreYouSureModal from '@/components/util/AreYouSureModal';
import Context from '@/mixins/Context';
import EditAdvisingNote from '@/components/note/EditAdvisingNote';
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import NewNoteModal from "@/components/note/NewNoteModal";
import NoteEditSession from "@/mixins/NoteEditSession";
import Scrollable from '@/mixins/Scrollable';
import TimelineDate from '@/components/student/profile/TimelineDate';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { dismissStudentAlert } from '@/api/student';
import { deleteNote, markRead } from '@/api/notes';

export default {
  name: 'AcademicTimeline',
  components: {AdvisingNote, AreYouSureModal, EditAdvisingNote, NewNoteModal, TimelineDate},
  mixins: [Context, GoogleAnalytics, NoteEditSession, Scrollable, UserMetadata, Util],
  props: {
    student: Object
  },
  data: () => ({
    creatingNewNote: false,
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
    isShowingAll: false,
    isTimelineLoading: true,
    messageForDelete: undefined,
    messages: undefined,
    openMessages: []
  }),
  computed: {
    activeTab() {
      return this.filter || 'all';
    },
    anchor() {
      return location.hash;
    },
    countPerActiveTab() {
      return this.filter
        ? this.countsPerType[this.filter]
        : this.size(this.messages);
    },
    deleteConfirmModalBody() {
      return this.messageForDelete ? `Are you sure you want to delete the "<b>${this.messageForDelete.subject}</b>" note?` : '';
    },
    showDeleteConfirmModal() {
      return !!this.messageForDelete;
    }
  },
  watch: {
    filter() {
      this.alertScreenReader(this.describeTheActiveTab());
      this.openMessages = [];
    },
    isShowingAll() {
      this.alertScreenReader(this.describeTheActiveTab());
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
        // Unique message ids are not guaranteed. Here we generate a transient and non-zero primary key.
        message.transientId = (typeIndex + 1) * 1000 + index;
      });
    });
    this.sortMessages();
    this.alertScreenReader('Academic Timeline has loaded');
    this.isTimelineLoading = false;
  },
  mounted() {
    if (this.anchor) {
      const match = this.anchor.match(/#([0-9-]+)/);
      if (match) {
        const messageId = match[1];
        const note = this.find(this.messages, function(m) {
          // Legacy advising notes have string IDs; BOA-created advising notes have integer IDs.
          if (m.id && m.id.toString() === messageId) {
            return true;
          }
        });
        if (note) {
          this.isShowingAll = true;
          this.$nextTick(function() {
            this.open(note);
            this.scrollToPermalink(messageId);
          });
        }
      }
    }
  },
  methods: {
    afterEditCancel() {
      this.editExistingNoteId(null);
    },
    afterNoteUpdated(updatedNote) {
      const note = this.find(this.messages, ['id', updatedNote.id]);
      note.subject = updatedNote.subject;
      note.body = note.message = updatedNote.body;
      note.topics = updatedNote.topics;
      note.attachments = updatedNote.attachments;
      note.updatedAt = updatedNote.updatedAt;
      this.editExistingNoteId(null);
    },
    cancelTheDelete() {
      this.alertScreenReader('Cancelled');
      this.messageForDelete = undefined;
    },
    close(message) {
      if (message.transientId === this.editingNoteId) {
        return false;
      }
      if (this.includes(this.openMessages, message.transientId)) {
        this.openMessages = this.remove(
          this.openMessages,
          id => id !== message.transientId
        );
      }
      this.alertScreenReader('Message closed');
    },
    deleteNote(message) {
      // The following opens the "Are you sure?" modal
      this.alertScreenReader('Please confirm delete');
      this.messageForDelete = message;
    },
    deleteConfirmed() {
      const predicate = ['transientId', this.messageForDelete.transientId];
      const note = this.find(this.messages, predicate);
      this.remove(this.messages, predicate);
      this.openMessages = this.remove(this.openMessages, predicate);
      this.messageForDelete = undefined;
      deleteNote(note.id).then(() => {
        this.alertScreenReader('Note deleted');
      });
    },
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
    displayUpdatedAt(message) {
      return message.updatedAt && (message.updatedAt !== message.createdAt);
    },
    editNote(message) {
      this.editExistingNoteId(message.transientId);
      this.putFocusNextTick('edit-note-subject');
    },
    id(rowIndex) {
      return `timeline-tab-${this.activeTab}-message-${rowIndex}`;
    },
    isEditable(message) {
      return message.type === 'note' && !message.isLegacy;
    },
    markRead(message) {
      if (!message.read) {
        message.read = true;
        if (this.includes(['alert', 'hold'], message.type)) {
          dismissStudentAlert(message.id);
          this.gaStudentAlert(message.id, `Advisor ${this.user.uid} dismissed alert`, 'view')
        } else if (message.type === 'note') {
          markRead(message.id);
          this.gaNoteEvent(message.id, `Advisor ${this.user.uid} read note`, 'view');
        }
      }
    },
    messagesPerType(type) {
      return type
        ? this.filterList(this.messages, ['type', type])
        : this.messages;
    },
    onCreateAdvisingNote(note) {
      this.creatingNewNote = false;
      note.type = 'note';
      note.message = note.body;
      note.transientId = new Date().getTime();
      this.messages.push(note);
      this.countsPerType.note++;
      this.sortMessages();
      this.openMessages.push(note.transientId);
      this.gaNoteEvent(note.id, `Advisor ${this.user.uid} created note`, 'create');
    },
    onSubmitAdvisingNote() {
      this.creatingNewNote = true;
    },
    open(message) {
      if (message.transientId === this.editingNoteId) {
        return false;
      }
      if (!this.includes(this.openMessages, message.transientId)) {
        this.openMessages.push(message.transientId);
      }
      this.markRead(message);
      this.alertScreenReader('Message opened');
    },
    scrollToPermalink(messageId) {
      this.scrollTo(`#message-row-${messageId}`);
      this.putFocusNextTick(`message-row-${messageId}`);
    },
    sortMessages() {
      this.messages.sort((m1, m2) => {
        let d1 = m1.updatedAt || m1.createdAt;
        let d2 = m2.updatedAt || m2.createdAt;
        if (d1 && d2 && d1 != d2) {
          return d2.localeCompare(d1);
        } else if (d1 === d2 && m1.id && m2.id) {
          return m2.id < m1.id ? -1 : 1;
        } else if (!d1 && !d2) {
          return m2.transientId - m1.transientId;
        } else {
          return d1 ? -1 : 1;
        }
      });
    }
  }
};
</script>

<style>
.pill {
  background-color: #fff;
  border: 1px solid #999;
  border-radius: 5px;
  color: #666;
  font-size: 12px;
  height: 24px;
  padding-top: 1px;
  width: auto;
}
.pill-attachment {
  height: 26px;
  padding: 6px;
}
.pill-list {
  list-style-type: none;
}
.pill-list-header {
  font-size: 16px;
  font-weight: 800;
}
</style>

<style scoped>
.close-message {
  width: 100%;
  order: -1;
}
.column-message {
  max-width: 1px;
  padding: 10px 10px 10px 5px;
  vertical-align: middle;
}
.column-pill {
  white-space: nowrap;
  width: 100px;
}
.column-right {
  text-align: right;
  width: 1%;
}
.edit-note-button {
  font-size: 15px;
}
.messages-none {
  font-size: 18px;
  font-weight: 500;
}
.message-open {
  flex-flow: row wrap;
  display: flex;
  min-height: 40px;
}
.message-open > .when-message-closed {
  display: none;
}
.message-row:active,
.message-row:focus,
.message-row:hover {
  background-color: #e3f5ff;
}
.message-row-read {
  background-color: #f9f9f9;
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
  width: 100px;
  background-color: #999;
}
.pill-requirement {
  width: 100px;
  background-color: #93c165;
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
