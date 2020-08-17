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
              :class="{ 'tab-active text-white': !filter, 'tab-inactive text-dark': filter }"
              class="tab pl-2 pr-2"
              variant="link"
              @click="setFilter(null)">
              All
            </b-btn>
          </div>
          <div v-for="type in keys(filterTypes)" :key="type">
            <b-btn
              :id="`timeline-tab-${type}`"
              :class="{
                'tab-active text-white': type === filter && countsPerType[type],
                'tab-inactive text-dark': type !== filter && countsPerType[type],
                'tab-disabled text-muted': !countsPerType[type]
              }"
              :aria-label="`${filterTypes[type].name}s tab`"
              :disabled="!countsPerType[type]"
              class="tab ml-2 pl-2 pr-2 text-center"
              variant="link"
              @click="setFilter(type)">
              {{ filterTypes[type].tab }}
            </b-btn>
          </div>
        </div>
      </div>
      <div v-if="!$currentUser.isAdmin && $currentUser.canAccessAdvisingData">
        <CreateNoteModal :student="student" />
      </div>
    </div>

    <div v-if="isExpandAllAvailable" class="mt-1 mb-1 timeline-submenu">
      <b-btn
        :id="`toggle-expand-all-${filter}s`"
        variant="link"
        @click.prevent="toggleExpandAll()">
        <font-awesome
          :icon="allExpanded ? 'caret-down' : 'caret-right'"
          class="toggle-expand-all-caret" />
        <span class="no-wrap pl-1">{{ allExpanded ? 'Collapse' : 'Expand' }} all {{ filter }}s</span>
      </b-btn>
      <div v-if="filter === 'note' && ($currentUser.isAdmin || isDirector($currentUser))">
        |
        <a
          id="download-notes-link"
          class="p-2"
          :href="notesDownloadUrl">
          Download notes
        </a>
      </div>
      |
      <label
        :for="`timeline-${filter}s-query-input`"
        class="mb-0 ml-2 mr-2">
        Search {{ capitalize(filter) }}s:
      </label>
      <input
        :id="`timeline-${filter}s-query-input`"
        v-model="timelineQuery"
        class="pl-2 pr-2 timeline-query-input"
        @keypress.enter.stop="searchTimeline()" />
    </div>

    <div v-if="searchResultsLoading" id="timeline-notes-spinner" class="mt-4 text-center">
      <font-awesome icon="sync" size="3x" spin />
    </div>

    <div v-if="!searchResultsLoading && !countPerActiveTab" class="pb-4 pl-2">
      <span id="zero-messages" class="messages-none">
        <span v-if="filter">No {{ filterTypes[filter].name.toLowerCase() }}s</span>
        <span v-if="!filter">None</span>
      </span>
    </div>

    <div v-if="!searchResultsLoading && searchResults" class="mb-2">
      <strong>
        {{ pluralize(`advising ${filter}`, searchResults.length) }} for&nbsp;
        <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.name }}</span>
        &nbsp;with '{{ timelineQuery }}'
      </strong>
    </div>

    <div v-if="!searchResultsLoading && countPerActiveTab">
      <table class="w-100">
        <tr class="sr-only">
          <th>Type</th>
          <th>Summary</th>
          <th>Details</th>
          <th>Date</th>
        </tr>
        <tr v-if="creatingNoteWithSubject" class="message-row-read message-row border-top border-bottom">
          <td class="column-pill align-top p-2">
            <div class="pill text-center text-uppercase text-white pill-note" tabindex="0">
              <span class="sr-only">Creating new</span> advising note
            </div>
          </td>
          <td class="column-message">
            <div class="d-flex">
              <div class="mr-2">
                <font-awesome icon="sync" spin />
              </div>
              <div class="text-muted">
                {{ creatingNoteWithSubject }}
              </div>
            </div>
          </td>
          <td></td>
          <td>
            <div class="align-top pr-2 float-right text-nowrap text-muted">
              <TimelineDate
                :date="new Date()"
                :include-time-of-day="false" />
            </div>
          </td>
        </tr>
        <tr
          v-for="(message, index) in (searchResults ? filterSearchResults() : (isShowingAll ? messagesPerType(filter) : slice(messagesPerType(filter), 0, defaultShowPerTab)))"
          :id="`permalink-${message.type}-${message.id}`"
          :key="index"
          :class="{ 'message-row-read': message.read }"
          :tabindex="includes(openMessages, message.transientId) ? 0 : -1"
          class="message-row border-top border-bottom">
          <td class="column-pill align-top p-2">
            <div
              :id="`timeline-tab-${activeTab}-pill-${index}`"
              :class="`pill-${message.type}`"
              class="pill text-center text-uppercase text-white"
              tabindex="0">
              <span class="sr-only">Message of type </span>{{ filterTypes[message.type].name }}
            </div>
            <div
              v-if="isEditable(message) && !editModeNoteId && includes(openMessages, message.transientId)"
              class="mt-2">
              <div v-if="$currentUser.uid === message.author.uid">
                <b-btn
                  :id="`edit-note-${message.id}-button`"
                  :disabled="disableNewNoteButton"
                  variant="link"
                  class="p-0 edit-note-button"
                  @keypress.enter.stop="editNote(message)"
                  @click.stop="editNote(message)">
                  Edit Note
                </b-btn>
              </div>
              <div v-if="$currentUser.isAdmin">
                <b-btn
                  id="delete-note-button"
                  :disabled="disableNewNoteButton"
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
            :class="{ 'font-weight-bold': !message.read }"
            class="column-message align-top">
            <div
              :id="`timeline-tab-${activeTab}-message-${index}`"
              :class="{
                'align-top message-open': includes(openMessages, message.transientId),
                'truncate': !includes(openMessages, message.transientId),
                'img-blur': $currentUser.inDemoMode && ['appointment', 'note'].includes(message.type)
              }"
              :tabindex="includes(openMessages, message.transientId) ? -1 : 0"
              @keyup.enter="open(message, true)"
              @click="open(message, true)">
              <span v-if="['appointment', 'note'].includes(message.type) && message.id !== editModeNoteId" class="when-message-closed sr-only">Open message</span>
              <font-awesome v-if="message.status === 'Satisfied'" icon="check" class="requirements-icon text-success" />
              <font-awesome v-if="message.status === 'Not Satisfied'" icon="exclamation" class="requirements-icon text-icon-exclamation" />
              <font-awesome v-if="message.status === 'In Progress'" icon="clock" class="requirements-icon text-icon-clock" />
              <span v-if="!includes(['appointment', 'note'] , message.type)">{{ message.message }}</span>
              <AdvisingNote
                v-if="message.type === 'note' && message.id !== editModeNoteId"
                :delete-note="deleteNote"
                :edit-note="editNote"
                :note="message"
                :after-saved="afterNoteEdit"
                :is-open="includes(openMessages, message.transientId)" />
              <EditAdvisingNote
                v-if="message.type === 'note' && message.id === editModeNoteId"
                :note-id="message.id"
                :after-cancel="afterNoteEditCancel"
                :after-saved="afterNoteEdit" />
              <AdvisingAppointment
                v-if="message.type === 'appointment'"
                :appointment="message"
                :is-open="includes(openMessages, message.transientId)"
                :on-appointment-status-change="onAppointmentStatusChange"
                :student="student" />
              <div v-if="includes(openMessages, message.transientId) && message.id !== editModeNoteId" class="text-center close-message">
                <b-btn
                  :id="`timeline-tab-${activeTab}-close-message`"
                  variant="link"
                  @keyup.enter.stop="close(message, true)"
                  @click.stop="close(message, true)">
                  <div class="d-flex">
                    <div class="mr-1">
                      <font-awesome icon="times-circle" class="font-size-24" />
                    </div>
                    <div class="no-wrap">
                      Close Message
                    </div>
                  </div>
                </b-btn>
              </div>
            </div>
          </td>
          <td class="column-right align-top pt-1 pr-1">
            <div v-if="!includes(openMessages, message.transientId) && message.type === 'appointment'">
              <div
                v-if="message.appointmentType === 'Drop-in' && message.status === 'cancelled'"
                :id="`collapsed-${message.type}-${message.id}-status-cancelled`"
                class="pill-appointment-status pill-cancelled pl-2 pr-2 mr-2 text-nowrap">
                Cancelled
              </div>
              <div
                v-if="message.appointmentType === 'Drop-in' && message.status === 'checked_in'"
                :id="`collapsed-${message.type}-${message.id}-status-checked-in`"
                class="pill-appointment-status pill-checked-in pl-2 pr-2 mr-2 text-nowrap">
                Checked In
              </div>
              <div
                v-if="message.appointmentType === 'Drop-in' && message.status === 'reserved'"
                :id="`collapsed-${message.type}-${message.id}-status-waiting`"
                class="pill-appointment-status pill-waiting pl-2 pr-2 mr-2 text-nowrap">
                Assigned
              </div>
              <div
                v-if="message.appointmentType === 'Drop-in' && message.status === 'waiting'"
                :id="`collapsed-${message.type}-${message.id}-status-waiting`"
                class="pill-appointment-status pill-waiting pl-2 pr-2 mr-2 text-nowrap">
                Waiting
              </div>
            </div>
            <div v-if="message.type === 'note' || message.type === 'appointment'">
              <font-awesome v-if="size(message.attachments)" icon="paperclip" class="mt-2" />
              <span class="sr-only">{{ size(message.attachments) ? 'Has attachments' : 'No attachments' }}</span>
            </div>
          </td>
          <td class="column-right align-top">
            <div
              :id="`timeline-tab-${activeTab}-date-${index}`"
              class="pt-2 pr-2 text-nowrap">
              <div v-if="!includes(openMessages, message.transientId) || !includes(['note', 'appointment'], message.type)">
                <TimelineDate
                  :id="`collapsed-${message.type}-${message.id}-created-at`"
                  :date="message.updatedAt || message.createdAt"
                  :include-time-of-day="false"
                  :sr-prefix="message.type === 'appointment' ? 'Appointment date' : 'Last updated on'" />
              </div>
              <div v-if="includes(openMessages, message.transientId) && ['appointment', 'note'].includes(message.type)">
                <div v-if="message.createdAt" :class="{'mb-2': !displayUpdatedAt(message)}">
                  <div class="text-muted">{{ message.type === 'appointment' ? 'Appt Date' : 'Created' }}:</div>
                  <TimelineDate
                    :id="`expanded-${message.type}-${message.id}-created-at`"
                    :date="message.createdAt"
                    :sr-prefix="message.type === 'appointment' ? 'Appointment date' : 'Created on'"
                    :include-time-of-day="(message.createdAt.length > 10) && (message.type !== 'appointment')" />
                </div>
                <div v-if="displayUpdatedAt(message)">
                  <div class="mt-2 text-muted">Updated:</div>
                  <TimelineDate
                    :id="`expanded-${message.type}-${message.id}-updated-at`"
                    :date="message.updatedAt"
                    :include-time-of-day="message.updatedAt.length > 10"
                    class="mb-2"
                    sr-prefix="Last updated on" />
                </div>
                <div class="text-muted">
                  <router-link
                    v-if="message.type === 'note' && message.id !== editModeNoteId"
                    :id="`advising-note-permalink-${message.id}`"
                    :to="`#${message.type}-${message.id}`"
                    @click.native="scrollToPermalink(message.type, message.id)">
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
    <div v-if="!searchResults && !searchResultsLoading && (countPerActiveTab > defaultShowPerTab)" class="text-center">
      <b-btn
        :id="`timeline-tab-${activeTab}-previous-messages`"
        :aria-label="isShowingAll ? 'Hide previous messages' : 'Show previous messages'"
        class="no-wrap pr-2 pt-0"
        variant="link"
        @click="isShowingAll = !isShowingAll">
        <font-awesome :icon="isShowingAll ? 'caret-up' : 'caret-right'" />
        {{ isShowingAll ? 'Hide' : 'Show' }} Previous Messages
      </b-btn>
    </div>
    <AreYouSureModal
      v-if="showDeleteConfirmModal"
      :function-cancel="cancelTheDelete"
      :function-confirm="deleteConfirmed"
      :modal-body="deleteConfirmModalBody"
      :show-modal="showDeleteConfirmModal"
      button-label-confirm="Delete"
      modal-header="Delete note" />
  </div>
</template>

<script>
import AdvisingAppointment from "@/components/appointment/AdvisingAppointment";
import AdvisingNote from "@/components/note/AdvisingNote";
import AreYouSureModal from '@/components/util/AreYouSureModal';
import Berkeley from '@/mixins/Berkeley';
import Context from '@/mixins/Context';
import CreateNoteModal from "@/components/note/create/CreateNoteModal";
import EditAdvisingNote from '@/components/note/EditAdvisingNote';
import NoteEditSession from '@/mixins/NoteEditSession';
import Scrollable from '@/mixins/Scrollable';
import TimelineDate from '@/components/student/profile/TimelineDate';
import Util from '@/mixins/Util';
import { dismissStudentAlert } from '@/api/student';
import { getAppointment, markAppointmentRead } from '@/api/appointments';
import { deleteNote, getNote, markNoteRead } from '@/api/notes';
import { search } from '@/api/search';

export default {
  name: 'AcademicTimeline',
  components: {
    AdvisingAppointment,
    AdvisingNote,
    AreYouSureModal,
    CreateNoteModal,
    EditAdvisingNote,
    TimelineDate
  },
  mixins: [Berkeley, Context, NoteEditSession, Scrollable, Util],
  props: {
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    allExpanded: false,
    countsPerType: undefined,
    defaultShowPerTab: 5,
    editModeNoteId: undefined,
    filter: undefined,
    isShowingAll: false,
    isTimelineLoading: true,
    messageForDelete: undefined,
    messages: undefined,
    timelineQuery: null,
    openMessages: [],
    searchResults: null,
    searchResultsLoading: false,
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
    filterTypes() {
      let filterTypes = {
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
      }
      if (this.$currentUser.canAccessAdvisingData) {
        filterTypes.note = {
          name: 'Advising Note',
          tab: 'Notes'
        }
        filterTypes.appointment = {
          name: 'Appointment',
          tab: 'Appointments'
        }
      }
      return filterTypes;
    },
    isExpandAllAvailable() {
      return this.includes(['appointment', 'note'], this.filter);
    },
    notesDownloadUrl() {
      return `${this.$config.apiBaseUrl}/api/notes/download_for_sid/${this.student.sid}`;
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
        // If object is not a BOA advising note then generate a transient and non-zero primary key.
        message.transientId = (typeIndex + 1) * 1000 + index;
      });
    });
    this.sortMessages();
    this.alertScreenReader(`${this.student.name} profile loaded.`);
    this.isTimelineLoading = false;
    const onCreateNewNote = note => {
      if (note.sid === this.student.sid) {
        const currentNoteIds = this.map(this.filterList(this.messages, ['type', 'note']), 'id');
        const isNotInView = !this.includes(currentNoteIds, note.id);
        if (isNotInView) {
          note.transientId = note.id;
          this.messages.push(note);
          this.countsPerType.note++;
          this.sortMessages();
          this.alertScreenReader(`New advising note created for student ${this.student.name}.`);
        }
      }
    };
    if (this.$currentUser.canAccessAdvisingData) {
      this.$eventHub.$on('advising-note-created', onCreateNewNote);
      this.$eventHub.$on('batch-of-notes-created', note_ids_per_sid => {
        const noteId = note_ids_per_sid[this.student.sid];
        if (noteId) {
          getNote(noteId).then(note => onCreateNewNote(note));
        }
      });
    }
  },
  mounted() {
    if (this.anchor) {
      const match = this.anchor.match(/^#(\w+)-([\d\w-]+)/);
      if (match && match.length > 2) {
        const messageType = match[1].toLowerCase();
        const messageId = match[2];
        const obj = this.find(this.messages, function(m) {
          // Legacy advising notes have string IDs; BOA-created advising notes have integer IDs.
          if (m.id && m.id.toString() === messageId && m.type.toLowerCase() === messageType) {
            return true;
          }
        });
        if (obj) {
          this.isShowingAll = true;
          this.$nextTick(function() {
            this.open(obj, true);
            this.scrollToPermalink(messageType, messageId);
          });
        }
      }
    }
  },
  methods: {
    afterNoteEdit(updatedNote) {
      this.editModeNoteId = null;
      const note = this.find(this.messages, ['id', updatedNote.id]);
      note.subject = updatedNote.subject;
      note.body = note.message = updatedNote.body;
      note.topics = updatedNote.topics;
      note.attachments = updatedNote.attachments;
      note.updatedAt = updatedNote.updatedAt;
    },
    afterNoteEditCancel() {
      this.editModeNoteId = null;
    },
    cancelTheDelete() {
      this.alertScreenReader('Cancelled');
      this.messageForDelete = undefined;
    },
    close(message, screenreaderAlert) {
      if (this.editModeNoteId) {
        return false;
      }
      if (this.includes(this.openMessages, message.transientId)) {
        this.openMessages = this.remove(
          this.openMessages,
          id => id !== message.transientId
        );
      }
      if (this.openMessages.length === 0) {
        this.allExpanded = false;
      }
      if (screenreaderAlert) {
        this.alertScreenReader(`${this.capitalize(message.type)} closed`);
      }
    },
    deleteNote(message) {
      // The following opens the "Are you sure?" modal
      this.alertScreenReader('Please confirm delete');
      this.messageForDelete = message;
    },
    deleteConfirmed() {
      const transientId = this.messageForDelete.transientId;
      const predicate = ['transientId', transientId];
      const note = this.find(this.messages, predicate);
      this.remove(this.messages, predicate);
      this.remove(this.openMessages, value => transientId === value);
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
      const pluralize = this.pluralize(noun, inViewCount);
      return this.isShowingAll && inViewCount > this.defaultShowPerTab
        ? `Showing all ${pluralize}`
        : `Showing ${pluralize}`;
    },
    displayUpdatedAt(message) {
      return message.updatedAt && (message.updatedAt !== message.createdAt) && (message.type !== 'appointment');
    },
    editNote(note) {
      this.editModeNoteId = note.id;
      this.putFocusNextTick('edit-note-subject');
    },
    filterSearchResults() {
      return this.filterList(this.messages, message => this.searchResults.includes(message.id));
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
          this.$ga.studentAlert(`Advisor ${this.$currentUser.uid} dismissed alert`);
        } else if (message.type === 'note') {
          markNoteRead(message.id);
          this.$ga.noteEvent(message.id, null, `Advisor ${this.$currentUser.uid} read note`);
        } else if (message.type === 'appointment') {
          markAppointmentRead(message.id);
          this.$ga.appointmentEvent(message.id, null, `Advisor ${this.$currentUser.uid} read appointment`);
        }
      }
    },
    messagesPerType(type) {
      return type
        ? this.filterList(this.messages, ['type', type])
        : this.messages;
    },
    onAppointmentStatusChange(appointmentId) {
      return new Promise(resolve => {
        getAppointment(appointmentId).then(appointment => {
          let timelineAppointment = this.messagesPerType('appointment').find(a => a.id === +appointment.id);
          Object.assign(timelineAppointment, appointment);
          resolve();
        });
      });
    },
    open(message, screenreaderAlert) {
      if (message.type === 'note' && message.id === this.editModeNoteId) {
        return false;
      }
      if (!this.includes(this.openMessages, message.transientId)) {
        this.openMessages.push(message.transientId);
      }
      this.markRead(message);
      if (this.isExpandAllAvailable && this.openMessages.length === this.messagesPerType(this.filter).length) {
        this.allExpanded = true;
      }
      if (screenreaderAlert) {
        this.alertScreenReader(`${this.capitalize(message.type)} opened`);
      }
    },
    scrollToPermalink(messageType, messageId) {
      this.scrollTo(`#permalink-${messageType}-${messageId}`);
      this.putFocusNextTick(`message-row-${messageId}`);
    },
    searchTimeline() {
      if (this.timelineQuery && this.timelineQuery.length) {
        this.searchResultsLoading = true;
        var includeAppointments = false;
        var includeNotes = false;
        var appointmentOptions = null;
        var noteOptions = null;
        if (this.filter === 'appointment') {
          includeAppointments = true;
          appointmentOptions = {studentCsid: this.student.sid};
        }
        if (this.filter === 'note') {
          includeNotes = true;
          noteOptions = {studentCsid: this.student.sid};
        }
        search(
          this.timelineQuery,
          includeAppointments,
          false,
          includeNotes,
          false,
          appointmentOptions,
          noteOptions
        ).then(data => {
          const items = this.filter === 'appointment' ? this.get(data, 'appointments') : this.get(data, 'notes');
          this.searchResults = this.map(items, 'id');
          this.isShowingAll = true;
          this.searchResultsLoading = false;
        });
      } else {
        this.searchResults = null;
      }
    },
    setFilter(filter) {
      this.searchResults = null;
      this.timelineQuery = null;
      if (filter !== this.filter) {
        this.filter = filter;
        this.allExpanded = false;
      }
    },
    sortDate(message) {
      if (message.type === 'appointment') {
        return message.createdAt;
      } else {
        return message.updatedAt || message.createdAt;
      }
    },
    sortMessages() {
      this.messages.sort((m1, m2) => {
        let d1 = this.sortDate(m1);
        let d2 = this.sortDate(m2);
        if (d1 && d2 && d1 !== d2) {
          return d2.localeCompare(d1);
        } else if (d1 === d2 && m1.id && m2.id) {
          return m2.id < m1.id ? -1 : 1;
        } else if (!d1 && !d2) {
          return m2.transientId - m1.transientId;
        } else {
          return d1 ? -1 : 1;
        }
      });
    },
    toggleExpandAll() {
      this.isShowingAll = true;
      this.allExpanded = !this.allExpanded;
      if (this.allExpanded) {
        this.each(this.messagesPerType(this.filter), this.open);
        this.alertScreenReader(`All ${this.filter}s expanded`);
      } else {
        this.each(this.messagesPerType(this.filter), this.close);
        this.alertScreenReader(`All ${this.filter}s collapsed`);
      }
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
  margin-top: 2px;
  padding-top: 2px;
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
.truncate {
  height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  background-color: #eb9d3e;
  width: 60px;
}
.pill-hold {
  background-color: #bc74fe;
  width: 60px;
}
.pill-appointment {
  background-color: #eee;
  color: #666 !important;
  font-weight: bolder;
  width: 100px;
}
.pill-note {
  background-color: #999;
  width: 100px;
}
.pill-requirement {
  background-color: #93c165;
  width: 100px;
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
.timeline-query-input {
  box-sizing: border-box;
  border: 2px solid #ccc;
  border-radius: 4px;
  height: 30px;
}
.timeline-submenu {
  align-items: center;
  display: flex;
}
.toggle-expand-all-caret {
  width: 15px;
}
</style>
