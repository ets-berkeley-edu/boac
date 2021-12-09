<template>
  <div>
    <div v-if="isExpandAllAvailable" class="mt-1 mb-1 timeline-submenu">
      <h3 class="sr-only">Quick Links</h3>
      <b-btn
        :id="`toggle-expand-all-${filter}s`"
        variant="link"
        @click.prevent="toggleExpandAll"
      >
        <font-awesome
          :icon="allExpanded ? 'caret-down' : 'caret-right'"
          class="toggle-expand-all-caret"
        />
        <span class="no-wrap pl-1">{{ allExpanded ? 'Collapse' : 'Expand' }} all {{ filter }}s</span>
      </b-btn>
      <div v-if="filter === 'note' && ($currentUser.isAdmin || isDirector($currentUser))">
        | <a id="download-notes-link" class="p-2" :href="`${$config.apiBaseUrl}/api/notes/download_for_sid/${student.sid}`">Download notes</a>
      </div>
      |
      <div>
        <label
          :id="`timeline-${filter}s-query-label`"
          :for="`timeline-${filter}s-query-input`"
          class="mb-0 ml-2 mr-1 text-nowrap"
        >
          Search {{ $_.capitalize(filter) }}s:
        </label>
      </div>
      <div>
        <b-input
          :id="`timeline-${filter}s-query-input`"
          v-model="timelineQuery"
          :aria-labelledby="`timeline-${filter}s-query-label`"
          class="pl-2 pr-2 timeline-query-input"
          trim
          type="search"
        />
      </div>
    </div>

    <div v-if="!countPerActiveTab" class="pb-4 pl-2">
      <h3 id="zero-messages" class="messages-none">
        <span v-if="filter">No {{ filterTypes[filter].name.toLowerCase() }}s</span>
        <span v-if="!filter">None</span>
      </h3>
    </div>

    <div v-if="searchResults" class="ml-3 my-2">
      <h3 id="search-results-header" class="messages-none">
        {{ pluralize(`advising ${filter}`, searchResults.length) }} for&nbsp;
        <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.name }}</span>
        with '{{ timelineQuery }}'
      </h3>
    </div>

    <div v-if="countPerActiveTab">
      <h3 class="sr-only">{{ activeTab === 'all' ? 'All Messages' : `${$_.capitalize(activeTab)}s` }}</h3>
      <table id="timeline-messages" class="w-100">
        <tr class="sr-only">
          <th>Type</th>
          <th>Summary</th>
          <th>Details</th>
          <th>Date</th>
        </tr>
        <tr v-if="creatingNoteEvent" class="message-row-read message-row border-top border-bottom">
          <td class="column-pill align-top p-2">
            <div class="pill text-center text-uppercase text-white pill-note">
              <span class="sr-only">Creating new</span> advising note
            </div>
          </td>
          <td class="column-message">
            <div class="d-flex">
              <div class="mr-2">
                <font-awesome icon="sync" spin />
              </div>
              <div class="text-muted">
                {{ creatingNoteEvent.subject }}
              </div>
            </div>
          </td>
          <td></td>
          <td>
            <div class="align-top pr-2 float-right text-nowrap text-muted">
              <TimelineDate
                :date="new Date()"
                :include-time-of-day="false"
              />
            </div>
          </td>
        </tr>
        <tr
          v-for="(message, index) in (searchResults || (isShowingAll ? messagesPerType(filter) : $_.slice(messagesPerType(filter), 0, defaultShowPerTab)))"
          :id="`permalink-${message.type}-${message.id}`"
          :key="index"
          :class="{'message-row-read': message.read}"
          class="message-row border-top border-bottom"
        >
          <td class="column-pill align-top p-2">
            <div
              :id="`timeline-tab-${activeTab}-pill-${index}`"
              :class="`pill-${message.type}`"
              class="pill text-center text-uppercase text-white"
              :role="message.type === 'requirement' ? 'cell' : 'button'"
              :tabindex="$_.includes(openMessages, message.transientId) ? -1 : 0"
              @keyup.enter="open(message, true)"
              @click="open(message, true)"
            >
              <span class="sr-only">Message of type </span>{{ filterTypes[message.type].name }}
            </div>
            <div
              v-if="isEditable(message) && !editModeNoteId && $_.includes(openMessages, message.transientId)"
              class="mt-2"
            >
              <div v-if="$currentUser.uid === message.author.uid && (!message.isPrivate || $currentUser.canAccessPrivateNotes)">
                <b-btn
                  :id="`edit-note-${message.id}-button`"
                  :disabled="disableNewNoteButton"
                  variant="link"
                  class="p-0 edit-note-button"
                  @keypress.enter.stop="editNote(message)"
                  @click.stop="editNote(message)"
                >
                  Edit Note
                </b-btn>
              </div>
              <div v-if="$currentUser.isAdmin">
                <b-btn
                  :id="`delete-note-button-${message.id}`"
                  :disabled="disableNewNoteButton"
                  variant="link"
                  class="p-0 edit-note-button"
                  @keypress.enter.stop="deleteNote(message)"
                  @click.stop="deleteNote(message)"
                >
                  Delete Note
                </b-btn>
              </div>
            </div>
          </td>
          <td
            :class="{'font-weight-bold': !message.read}"
            class="column-message align-top"
          >
            <div
              :id="`timeline-tab-${activeTab}-message-${index}`"
              :aria-pressed="$_.includes(openMessages, message.transientId)"
              :class="{
                'align-top message-open': $_.includes(openMessages, message.transientId) && message.type !== 'requirement' ,
                'truncate': !$_.includes(openMessages, message.transientId),
                'img-blur': $currentUser.inDemoMode && ['appointment', 'note'].includes(message.type)
              }"
              :role="message.type === 'requirement' ? '' : 'button'"
              :tabindex="$_.includes(openMessages, message.transientId) ? -1 : 0"
              @keyup.enter="open(message, true)"
              @click="open(message, true)"
            >
              <span v-if="['appointment', 'note'].includes(message.type) && message.id !== editModeNoteId" class="when-message-closed sr-only">Open message</span>
              <font-awesome v-if="message.status === 'Satisfied'" icon="check" class="requirements-icon text-success" />
              <font-awesome v-if="message.status === 'Not Satisfied'" icon="exclamation" class="requirements-icon text-icon-exclamation" />
              <font-awesome v-if="message.status === 'In Progress'" icon="clock" class="requirements-icon text-icon-clock" />
              <span v-if="!$_.includes(['appointment', 'note'] , message.type)">{{ message.message }}</span>
              <AdvisingNote
                v-if="message.type === 'note' && message.id !== editModeNoteId"
                :delete-note="deleteNote"
                :edit-note="editNote"
                :note="message"
                :after-saved="afterNoteEdit"
                :is-open="$_.includes(openMessages, message.transientId)"
              />
              <EditAdvisingNote
                v-if="message.type === 'note' && message.id === editModeNoteId"
                :note-id="message.id"
                :after-cancel="afterNoteEditCancel"
                :after-saved="afterNoteEdit"
              />
              <AdvisingAppointment
                v-if="message.type === 'appointment'"
                :appointment="message"
                :is-open="$_.includes(openMessages, message.transientId)"
                :on-appointment-status-change="onAppointmentStatusChange"
                :student="student"
              />
              <div v-if="$_.includes(openMessages, message.transientId) && message.id !== editModeNoteId" class="text-center close-message">
                <b-btn
                  :id="`${activeTab}-close-message-${message.id}`"
                  variant="link"
                  @keyup.enter.stop="close(message, true)"
                  @click.stop="close(message, true)"
                >
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
            <div v-if="!$_.includes(openMessages, message.transientId) && message.type === 'appointment'">
              <div
                v-if="message.appointmentType === 'Drop-in' && message.status === 'cancelled'"
                :id="`collapsed-${message.type}-${message.id}-status-cancelled`"
                class="pill-appointment-status pill-cancelled pl-2 pr-2 mr-2 text-nowrap"
              >
                Canceled
              </div>
              <div
                v-if="message.createdBy === 'YCBM' && message.status === 'cancelled'"
                :id="`collapsed-${message.type}-${message.id}-status-cancelled`"
                class="collapsed-cancelled-icon"
              >
                <font-awesome icon="calendar-minus" class="status-cancelled-icon " />
                Canceled
              </div>
              <div
                v-if="message.appointmentType === 'Drop-in' && message.status === 'checked_in'"
                :id="`collapsed-${message.type}-${message.id}-status-checked-in`"
                class="pill-appointment-status pill-checked-in pl-2 pr-2 mr-2 text-nowrap"
              >
                Checked In
              </div>
              <div
                v-if="message.appointmentType === 'Drop-in' && message.status === 'reserved'"
                :id="`collapsed-${message.type}-${message.id}-status-waiting`"
                class="pill-appointment-status pill-waiting pl-2 pr-2 mr-2 text-nowrap"
              >
                Assigned
              </div>
              <div
                v-if="message.appointmentType === 'Drop-in' && message.status === 'waiting'"
                :id="`collapsed-${message.type}-${message.id}-status-waiting`"
                class="pill-appointment-status pill-waiting pl-2 pr-2 mr-2 text-nowrap"
              >
                Waiting
              </div>
            </div>
            <div v-if="message.type === 'note' || message.type === 'appointment'">
              <font-awesome v-if="$_.size(message.attachments)" icon="paperclip" class="mt-2" />
              <span class="sr-only">{{ $_.size(message.attachments) ? 'Has attachments' : 'No attachments' }}</span>
            </div>
          </td>
          <td class="column-right align-top">
            <div
              :id="`timeline-tab-${activeTab}-date-${index}`"
              class="pt-2 pr-2 text-nowrap"
            >
              <div v-if="!$_.includes(openMessages, message.transientId) || !$_.includes(['note', 'appointment'], message.type)">
                <TimelineDate
                  :id="`collapsed-${message.type}-${message.id}-created-at`"
                  :date="message.updatedAt || message.createdAt"
                  :include-time-of-day="false"
                  :sr-prefix="message.type === 'appointment' ? 'Appointment date' : 'Last updated on'"
                />
              </div>
              <div v-if="$_.includes(openMessages, message.transientId) && ['appointment', 'note'].includes(message.type)">
                <div v-if="message.createdAt" :class="{'mb-2': !displayUpdatedAt(message)}">
                  <div class="text-muted">{{ message.type === 'appointment' ? 'Appt Date' : 'Created' }}:</div>
                  <TimelineDate
                    :id="`expanded-${message.type}-${message.id}-created-at`"
                    :date="message.createdAt"
                    :sr-prefix="message.type === 'appointment' ? 'Appointment date' : 'Created on'"
                    :include-time-of-day="(message.createdAt.length > 10) && (message.type !== 'appointment')"
                  />
                  <div
                    v-if="message.createdBy === 'YCBM' && message.endsAt"
                    :id="`expanded-${message.type}-${message.id}-appt-time-range`"
                  >
                    {{ getSameDayDate(message) }}
                  </div>
                </div>
                <div v-if="displayUpdatedAt(message)">
                  <div class="mt-2 text-muted">Updated:</div>
                  <TimelineDate
                    :id="`expanded-${message.type}-${message.id}-updated-at`"
                    :date="message.updatedAt"
                    :include-time-of-day="message.updatedAt.length > 10"
                    class="mb-2"
                    sr-prefix="Last updated on"
                  />
                </div>
                <div class="text-muted">
                  <router-link
                    v-if="message.type === 'note' && message.id !== editModeNoteId"
                    :id="`advising-note-permalink-${message.id}`"
                    :to="`#${message.type}-${message.id}`"
                    @click.native="scrollToPermalink(message.type, message.id)"
                  >
                    Permalink <font-awesome icon="link" />
                  </router-link>
                </div>
              </div>
              <span v-if="!message.updatedAt && !message.createdAt" class="sr-only">No last-updated date</span>
            </div>
          </td>
        </tr>
      </table>
    </div>
    <div :class="{'pb-4': !offerShowAll}">
      <div v-if="offerShowAll" class="text-center">
        <b-btn
          :id="`timeline-tab-${activeTab}-previous-messages`"
          class="no-wrap pr-2 pt-0"
          variant="link"
          @click="isShowingAll = !isShowingAll"
        >
          <font-awesome :icon="isShowingAll ? 'caret-up' : 'caret-right'" />
          {{ isShowingAll ? 'Hide' : 'Show' }} Previous Messages
        </b-btn>
      </div>
    </div>
    <AreYouSureModal
      v-if="showDeleteConfirmModal"
      :function-cancel="cancelTheDelete"
      :function-confirm="deleteConfirmed"
      :modal-body="deleteConfirmModalBody"
      :show-modal="showDeleteConfirmModal"
      button-label-confirm="Delete"
      modal-header="Delete note"
    />
  </div>
</template>

<script>
import AdvisingAppointment from '@/components/appointment/AdvisingAppointment'
import AdvisingNote from '@/components/note/AdvisingNote'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import EditAdvisingNote from '@/components/note/EditAdvisingNote'
import Scrollable from '@/mixins/Scrollable'
import TimelineDate from '@/components/student/profile/TimelineDate'
import Util from '@/mixins/Util'
import {deleteNote, getNote, markNoteRead} from '@/api/notes'
import {dismissStudentAlert} from '@/api/student'
import {getAppointment, markAppointmentRead} from '@/api/appointments'

export default {
  name: 'AcademicTimelineTable',
  mixins: [Berkeley, Context, Scrollable, Util],
  components: {
    AdvisingAppointment,
    AdvisingNote,
    AreYouSureModal,
    EditAdvisingNote,
    TimelineDate
  },
  props: {
    countsPerType: {
      required: true,
      type: Object
    },
    filter: {
      required: false,
      type: String
    },
    filterTypes: {
      required: true,
      type: Object
    },
    messages: {
      required: true,
      type: Array
    },
    onCreateNewNote: {
      required: true,
      type: Function
    },
    sortMessages: {
      required: true,
      type: Function
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    allExpanded: false,
    creatingNoteEvent: undefined,
    defaultShowPerTab: 5,
    editModeNoteId: undefined,
    isShowingAll: false,
    messageForDelete: undefined,
    openMessages: [],
    searchIndex: undefined,
    searchResults: undefined,
    timelineQuery: ''
  }),
  computed: {
    activeTab() {
      return this.filter || 'all'
    },
    anchor() {
      return location.hash
    },
    countPerActiveTab() {
      return this.filter ? this.countsPerType[this.filter] : this.$_.size(this.messages)
    },
    deleteConfirmModalBody() {
      return this.messageForDelete ? `Are you sure you want to delete the "<b>${this.messageForDelete.subject}</b>" note?` : ''
    },
    isExpandAllAvailable() {
      return this.$_.includes(['appointment', 'note'], this.filter)
    },
    offerShowAll() {
      return !this.searchResults && (this.countPerActiveTab > this.defaultShowPerTab)
    },
    showDeleteConfirmModal() {
      return !!this.messageForDelete
    }
  },
  watch: {
    filter() {
      this.allExpanded = false
      this.openMessages = []
      this.searchResults = null
      this.timelineQuery = ''
      this.alertScreenReader(this.describeTheActiveTab())
      this.refreshSearchIndex()
    },
    isShowingAll() {
      this.alertScreenReader(this.describeTheActiveTab())
    },
    timelineQuery() {
      if (this.timelineQuery) {
        const query = this.timelineQuery.replace(/\s/g, '').toLowerCase()
        const results = []
        this.$_.each(this.searchIndex, entry => {
          if (entry.idx.indexOf(query) > -1) {
            results.push(entry.message)
          }
        })
        this.searchResults = results
      } else {
        this.searchResults = null
      }
    }
  },
  created() {
    this.refreshSearchIndex()
    if (this.$currentUser.canAccessAdvisingData) {
      this.$eventHub.on('begin-note-creation', event => {
        if (this.$_.includes(event.completeSidSet, this.student.sid)) {
          this.creatingNoteEvent = event
        }
      })
      const afterCreateNote = note => {
        this.creatingNoteEvent = null
        this.onCreateNewNote(note)
        this.refreshSearchIndex()
      }
      this.$eventHub.on('advising-note-created', afterCreateNote)
      this.$eventHub.on('batch-of-notes-created', noteIdsBySid => {
        const noteId = noteIdsBySid[this.student.sid]
        if (noteId) {
          getNote(noteId).then(afterCreateNote)
        }
        this.refreshSearchIndex()
      })
    }
    this.sortMessages()
    this.alertScreenReader(`${this.student.name} profile loaded.`)
  },
  mounted() {
    if (this.anchor) {
      const match = this.anchor.match(/^#(\w+)-([\d\w-]+)/)
      if (match && match.length > 2) {
        const messageType = match[1].toLowerCase()
        const messageId = match[2]
        const obj = this.$_.find(this.messages, function(m) {
          // Legacy advising notes have string IDs; BOA-created advising notes have integer IDs.
          if (m.id && m.id.toString() === messageId && m.type.toLowerCase() === messageType) {
            return true
          }
        })
        if (obj) {
          this.isShowingAll = true
          this.$nextTick(function() {
            this.open(obj, true)
            this.scrollToPermalink(messageType, messageId)
          })
        }
      }
    }
  },
  methods: {
    afterNoteEdit(updatedNote) {
      this.editModeNoteId = null
      const note = this.$_.find(this.messages, ['id', updatedNote.id])
      note.attachments = updatedNote.attachments
      note.body = note.message = updatedNote.body
      note.isPrivate = updatedNote.isPrivate
      note.subject = updatedNote.subject
      note.topics = updatedNote.topics
      note.updatedAt = updatedNote.updatedAt
      this.refreshSearchIndex()
    },
    afterNoteEditCancel() {
      this.editModeNoteId = null
    },
    cancelTheDelete() {
      this.alertScreenReader('Canceled')
      this.$putFocusNextTick(`delete-note-button-${this.messageForDelete.id}`)
      this.messageForDelete = undefined
    },
    close(message, notifyScreenReader) {
      if (this.editModeNoteId) {
        return false
      }
      if (this.$_.includes(this.openMessages, message.transientId)) {
        this.openMessages = this.$_.remove(
          this.openMessages,
          id => id !== message.transientId
        )
      }
      if (this.openMessages.length === 0) {
        this.allExpanded = false
      }
      if (notifyScreenReader) {
        this.alertScreenReader(`${this.$_.capitalize(message.type)} closed`)
      }
    },
    deleteNote(message) {
      // The following opens the "Are you sure?" modal
      this.alertScreenReader('Please confirm delete')
      this.messageForDelete = message
    },
    deleteConfirmed() {
      const transientId = this.messageForDelete.transientId
      const predicate = ['transientId', transientId]
      const note = this.$_.find(this.messages, predicate)
      this.$_.remove(this.messages, predicate)
      this.$_.remove(this.openMessages, value => transientId === value)
      this.messageForDelete = undefined
      return deleteNote(note.id).then(() => {
        this.alertScreenReader('Note deleted')
        this.refreshSearchIndex()
      })
    },
    describeTheActiveTab() {
      const inViewCount = this.isShowingAll || this.countPerActiveTab <= this.defaultShowPerTab ? this.countPerActiveTab : this.defaultShowPerTab
      const noun = this.filter ? this.filterTypes[this.filter].name.toLowerCase() : 'message'
      const pluralize = this.pluralize(noun, inViewCount)
      return this.isShowingAll && inViewCount > this.defaultShowPerTab
        ? `Showing all ${pluralize}`
        : `Showing ${this.countPerActiveTab > this.defaultShowPerTab ? 'the first' : ''} ${pluralize}`
    },
    displayUpdatedAt(message) {
      return message.updatedAt && (message.updatedAt !== message.createdAt) && (message.type !== 'appointment')
    },
    editNote(note) {
      this.editModeNoteId = note.id
      this.$putFocusNextTick('edit-note-subject')
    },
    getSameDayDate(message) {
      let startsAt = this.$moment(message.createdAt).tz(this.$config.timezone).format('h:mma')
      let endsAt = this.$moment(message.endsAt).tz(this.$config.timezone).format('h:mma')

      return `${startsAt}-${endsAt}`
    },
    id(rowIndex) {
      return `timeline-tab-${this.activeTab}-message-${rowIndex}`
    },
    isEditable(message) {
      return message.type === 'note' && !message.legacySource
    },
    markRead(message) {
      if (!message.read) {
        message.read = true
        if (this.$_.includes(['alert', 'hold'], message.type)) {
          dismissStudentAlert(message.id)
          this.$ga.studentAlert(`Advisor ${this.$currentUser.uid} dismissed alert`)
        } else if (message.type === 'note') {
          markNoteRead(message.id)
          this.$ga.noteEvent(message.id, null, `Advisor ${this.$currentUser.uid} read note`)
        } else if (message.type === 'appointment') {
          markAppointmentRead(message.id)
          this.$ga.appointmentEvent(message.id, null, `Advisor ${this.$currentUser.uid} read appointment`)
        }
      }
    },
    messagesPerType(type) {
      return type ? this.$_.filter(this.messages, ['type', type]) : this.messages
    },
    onAppointmentStatusChange(appointmentId) {
      return new Promise(resolve => {
        getAppointment(appointmentId).then(appointment => {
          let timelineAppointment = this.messagesPerType('appointment').find(a => a.id === +appointment.id)
          Object.assign(timelineAppointment, appointment)
          resolve()
        })
      })
    },
    open(message, notifyScreenReader) {
      if (message.type === 'note' && message.id === this.editModeNoteId || message.type === 'requirement') {
        return false
      }
      if (!this.$_.includes(this.openMessages, message.transientId)) {
        this.openMessages.push(message.transientId)
      }
      this.markRead(message)
      if (this.isExpandAllAvailable && this.openMessages.length === this.messagesPerType(this.filter).length) {
        this.allExpanded = true
      }
      if (notifyScreenReader) {
        this.alertScreenReader(`${this.$_.capitalize(message.type)} opened`)
      }
    },
    scrollToPermalink(messageType, messageId) {
      this.scrollTo(`#permalink-${messageType}-${messageId}`)
      this.$putFocusNextTick(`message-row-${messageId}`)
    },
    refreshSearchIndex() {
      this.searchIndex = []
      const messages = ['appointment', 'note'].includes(this.filter) ? this.messagesPerType(this.filter) : []
      this.$_.each(messages, m => {
        const advisor = m.author || m.advisor
        const idx = [
          advisor.name,
          (this.$_.map(advisor.departments || [], 'name')).join(),
          advisor.email,
          m.body,
          m.category,
          m.createdBy,
          m.legacySource,
          m.message,
          m.subcategory,
          m.subject,
          (m.topics || []).join()
        ].join().replace(/\s/g, '').toLowerCase()
        this.searchIndex.push({idx: idx.toLowerCase(), message: m})
      })
    },
    toggleExpandAll() {
      this.isShowingAll = true
      this.allExpanded = !this.allExpanded
      if (this.allExpanded) {
        this.$_.each(this.messagesPerType(this.filter), this.open)
        this.alertScreenReader(`All ${this.filter}s expanded`)
      } else {
        this.$_.each(this.messagesPerType(this.filter), this.close)
        this.alertScreenReader(`All ${this.filter}s collapsed`)
      }
    }
  }
}
</script>
<style scoped>
.close-message {
  width: 100%;
  order: -1;
}
.collapsed-cancelled-icon {
  font-size: 14px;
  min-width: 108px;
  padding-top: 6px;
  padding-right: 6px;
  text-transform: uppercase;
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
  font-size: 16px;
  font-weight: bolder;
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
.pill-appointment {
  background-color: #eee;
  color: #666 !important;
  font-weight: bolder;
  width: 100px;
}
.pill-hold {
  background-color: #bc74fe;
  width: 60px;
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
