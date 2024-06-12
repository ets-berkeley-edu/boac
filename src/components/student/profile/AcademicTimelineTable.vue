<template>
  <div v-if="isExpandAllAvailable" class="align-center d-flex flex-wrap font-size-14">
    <h3 class="sr-only">Quick Links</h3>
    <div class="ml-2">
      <v-btn
        :id="`toggle-expand-all-${filter}s`"
        class="px-0"
        density="compact"
        :disabled="!messagesVisible.length"
        variant="plain"
        @click.prevent="toggleExpandAll"
      >
        <v-icon :icon="allExpanded ? mdiMenuDown : mdiMenuRight" />
        <span class="text-no-wrap">{{ allExpanded ? 'Collapse' : 'Expand' }} all {{ filter }}s</span>
      </v-btn>
    </div>
    <div v-if="showDownloadNotesLink" class="ml-3">|</div>
    <div v-if="showDownloadNotesLink" class="ml-3">
      <a id="download-notes-link" :href="`${config.apiBaseUrl}/api/notes/${student.sid}/download?type=${filter}`">Download {{ filter }}s</a>
    </div>
    <div class="ml-3">|</div>
    <div class="align-center d-flex ml-3">
      <label
        :id="`timeline-${filter}s-query-label`"
        :for="`timeline-${filter}s-query-input`"
        class="font-weight-bold mb-0 mr-1 text-no-wrap v-btn--variant-plain"
      >
        Search {{ filter === 'eForm' ? 'eForm' : capitalize(filter) }}s:
      </label>
      <v-text-field
        :id="`timeline-${filter}s-query-input`"
        v-model="timelineQuery"
        :aria-labelledby="`timeline-${filter}s-query-label`"
        bg-color="pale-blue"
        class="academic-timeline-search-input"
        color="primary"
        density="compact"
        flat
        hide-details
        type="search"
        variant="outlined"
      />
    </div>
    <div v-if="showMyNotesToggle" class="ml-3">|</div>
    <div v-if="showMyNotesToggle" class="ml-3">
      <div class="align-center d-flex font-weight-bold">
        <label for="toggle-my-notes-button" class="mr-3" :class="showMyNotesOnly ? 'text-grey' : 'text-primary'">
          All {{ filter }}s
        </label>
        <div class="mr-3">
          <v-switch
            id="toggle-my-notes-button"
            v-model="showMyNotesOnly"
            density="compact"
            color="primary"
            hide-details
          />
        </div>
        <label for="toggle-my-notes-button" :class="showMyNotesOnly ? 'text-primary' : 'text-grey'">
          My {{ filter }}s
        </label>
      </div>
    </div>
  </div>

  <div
    v-if="!searchResults && !messagesVisible.length"
    id="zero-messages"
    class="font-size-16 font-weight-700 ml-6 my-4 text-grey-darken-1"
  >
    <span v-if="filter && showMyNotesOnly">No {{ filterTypes[filter].name.toLowerCase() }}s authored by you.</span>
    <span v-if="filter && !showMyNotesOnly">No {{ filterTypes[filter].name.toLowerCase() }}s</span>
    <span v-if="!filter">None</span>
  </div>

  <div v-if="searchResults" class="ml-3 my-2">
    <h3 id="search-results-header" class="messages-none">
      {{ pluralize(`advising ${filter}`, searchResults.length) }} for&nbsp;
      <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</span>
      with '{{ timelineQuery }}'
    </h3>
  </div>

  <div v-if="countPerActiveTab">
    <h3 class="sr-only">{{ activeTab === 'all' ? 'All Messages' : `${capitalize(activeTab)}s` }}</h3>
    <table id="timeline-messages" class="w-100">
      <tr class="sr-only">
        <th>Type</th>
        <th>Summary</th>
        <th>Details</th>
        <th>Date</th>
      </tr>
      <tr v-if="creatingNoteEvent" class="message-row border-t-sm border-b-sm">
        <td class="column-pill align-top p-2">
          <div class="pill text-center text-uppercase text-white pill-note">
            <span class="sr-only">Creating new</span> advising note
          </div>
        </td>
        <td class="column-message">
          <div class="d-flex">
            <div class="mr-2">
              <v-icon :icon="mdiSync" spin />
            </div>
            <div class="text-grey-darken-2">
              {{ creatingNoteEvent.subject }}
            </div>
          </div>
        </td>
        <td></td>
        <td>
          <div class="align-top pr-2 float-right text-no-wrap text-grey-darken-2">
            <TimelineDate
              :date="new Date()"
              :include-time-of-day="false"
            />
          </div>
        </td>
      </tr>
      <tr
        v-for="(message, index) in messagesVisible"
        :id="`permalink-${message.type}-${message.id}`"
        :key="index"
        class="message-row"
      >
        <td class="column-pill align-top p-2">
          <div
            :id="`timeline-tab-${activeTab}-pill-${index}`"
            :class="`pill-${message.type}`"
            class="pill text-center text-uppercase text-white"
            :role="message.type === 'requirement' ? 'cell' : 'button'"
            :tabindex="includes(openMessages, message.transientId) ? -1 : 0"
            @keyup.enter="open(message, true)"
            @click="open(message, true)"
          >
            <span class="sr-only">Message of type </span>{{ filterTypes[message.type].name }}
          </div>
          <div
            v-if="isEditable(message) && !editModeNoteId && includes(openMessages, message.transientId)"
            class="mt-2"
          >
            <div v-if="currentUser.uid === message.author.uid && (!message.isPrivate || currentUser.canAccessPrivateNotes)">
              <v-btn
                :id="`edit-note-${message.id}-button`"
                :disabled="disableNewNoteButton"
                variant="text"
                class="p-0 edit-note-button"
                @keypress.enter.stop="editNote(message)"
                @click.stop="editNote(message)"
              >
                Edit {{ message.isDraft ? 'Draft' : 'Note' }}
              </v-btn>
            </div>
            <div
              v-if="currentUser.isAdmin || (message.isDraft && message.author.uid === currentUser.uid)"
            >
              <v-btn
                :id="`delete-note-button-${message.id}`"
                :disabled="disableNewNoteButton"
                variant="text"
                class="p-0 edit-note-button"
                @keypress.enter.stop="deleteNote(message)"
                @click.stop="deleteNote(message)"
              >
                Delete {{ message.isDraft ? 'Draft' : 'Note' }}
              </v-btn>
            </div>
          </div>
        </td>
        <td
          :class="{'font-weight-bold': !message.read}"
          class="column-message align-top"
        >
          <div
            :id="`timeline-tab-${activeTab}-message-${index}`"
            :aria-pressed="includes(openMessages, message.transientId)"
            :class="{
              'align-top message-open': includes(openMessages, message.transientId) && message.type !== 'requirement' ,
              'truncate': !includes(openMessages, message.transientId),
              'img-blur': currentUser.inDemoMode && ['appointment', 'eForm', 'note'].includes(message.type)
            }"
            :role="message.type === 'requirement' ? '' : 'button'"
            :tabindex="includes(openMessages, message.transientId) ? -1 : 0"
            @keyup.enter="open(message, true)"
            @click="open(message, true)"
          >
            <span v-if="['appointment', 'eForm', 'note'].includes(message.type) && message.id !== editModeNoteId" class="when-message-closed sr-only">Open message</span>
            <v-icon v-if="message.status === 'Satisfied'" :icon="mdiCheckBold" class="requirements-icon text-success" />
            <v-icon v-if="message.status === 'Not Satisfied'" :icon="mdiExclamationThick" class="requirements-icon text-icon-exclamation" />
            <v-icon v-if="message.status === 'In Progress'" :icon="mdiClockOutline" class="requirements-icon text-icon-clock" />
            <span v-if="!includes(['appointment', 'eForm', 'note'] , message.type)">{{ message.message }}</span>
            <AdvisingNote
              v-if="['eForm', 'note'].includes(message.type) && message.id !== editModeNoteId"
              :after-saved="afterNoteEdit"
              :delete-note="deleteNote"
              :edit-note="editNote"
              :is-open="includes(openMessages, message.transientId)"
              :note="message"
            />
            <EditAdvisingNote
              v-if="['eForm', 'note'].includes(message.type) && message.id === editModeNoteId"
              :note-id="message.id"
              :after-cancel="afterNoteEditCancel"
              :after-saved="afterEditAdvisingNote"
            />
            <AdvisingAppointment
              v-if="message.type === 'appointment'"
              :appointment="message"
              :is-open="includes(openMessages, message.transientId)"
              :student="student"
            />
            <div
              v-if="includes(openMessages, message.transientId) && message.id !== editModeNoteId"
              class="mb-1 text-center close-message"
            >
              <v-btn
                :id="`${activeTab}-close-message-${message.id}`"
                color="primary"
                density="compact"
                variant="text"
                @keyup.enter.stop="close(message, true)"
                @click.stop="close(message, true)"
              >
                <div class="align-center d-flex">
                  <div class="mr-1">
                    <v-icon :icon="mdiCloseCircle" size="18" />
                  </div>
                  <div class="text-no-wrap">
                    Close Message
                  </div>
                </div>
              </v-btn>
            </div>
          </div>
        </td>
        <td class="column-right align-content-top pr-1">
          <div v-if="!includes(openMessages, message.transientId) && message.type === 'appointment'">
            <div
              v-if="message.createdBy === 'YCBM' && message.status === 'cancelled'"
              :id="`collapsed-${message.type}-${message.id}-status-cancelled`"
              class="collapsed-cancelled-icon text-red-lighten-2"
            >
              <v-icon :icon="mdiCalendarMinus" class="status-cancelled-icon" />
              Canceled
            </div>
          </div>
          <div v-if="['appointment', 'eForm', 'note'].includes(message.type)">
            <v-icon v-if="size(message.attachments)" color="info" :icon="mdiPaperclip" />
            <span class="sr-only">{{ size(message.attachments) ? 'Has attachments' : 'No attachments' }}</span>
          </div>
        </td>
        <td class="column-right align-content-start">
          <div
            :id="`timeline-tab-${activeTab}-date-${index}`"
            class="pt-2 pr-2 text-no-wrap"
          >
            <div v-if="!includes(openMessages, message.transientId) || !includes(['appointment', 'eForm', 'note'], message.type)">
              <TimelineDate
                :id="`collapsed-${message.type}-${message.id}-created-at`"
                :date="message.setDate || message.updatedAt || message.createdAt"
                :include-time-of-day="false"
                :sr-prefix="message.type === 'appointment' ? 'Appointment date' : 'Last updated on'"
              />
            </div>
            <div v-if="includes(openMessages, message.transientId) && ['appointment', 'eForm', 'note'].includes(message.type)">
              <div v-if="message.createdAt" :class="{'mb-2': !displayUpdatedAt(message)}">
                <div class="text-grey-darken-2">{{ message.type === 'appointment' ? 'Appt Date' : 'Created' }}:</div>
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
                <div class="mt-2 text-grey-darken-2">Updated:</div>
                <TimelineDate
                  :id="`expanded-${message.type}-${message.id}-updated-at`"
                  :date="message.updatedAt"
                  :include-time-of-day="message.updatedAt.length > 10"
                  class="mb-2"
                  sr-prefix="Last updated on"
                />
              </div>
              <div v-if="message.setDate">
                <div class="mt-2 text-grey-darken-2">Set Date:</div>
                <TimelineDate
                  :id="`expanded-${message.type}-${message.id}-set-date`"
                  :date="message.setDate"
                  class="mb-2"
                />
              </div>
              <div class="text-grey-darken-2">
                <router-link
                  v-if="['eForm', 'note'].includes(message.type) && message.id !== editModeNoteId"
                  :id="`advising-${message.type}-permalink-${message.id}`"
                  :to="`#${message.type}-${message.id}`"
                  @click.native="scrollToPermalink(message.type, message.id)"
                >
                  Permalink <v-icon :icon="mdiLinkVariant" />
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
      <v-btn
        :id="`timeline-tab-${activeTab}-previous-messages`"
        class="text-no-wrap pr-2 pt-0"
        color="primary"
        density="compact"
        variant="text"
        @click="isShowingAll = !isShowingAll"
      >
        <v-icon :icon="isShowingAll ? mdiMenuUp : mdiMenuRight" />
        {{ isShowingAll ? 'Hide' : 'Show' }} Previous Messages
      </v-btn>
    </div>
  </div>
  <AreYouSureModal
    v-model="showDeleteConfirmModal"
    button-label-confirm="Delete"
    :function-cancel="cancelTheDelete"
    :function-confirm="deleteConfirmed"
    modal-header="Delete note"
  >
    {{ deleteConfirmModalBody }}
  </AreYouSureModal>
</template>

<script setup>
import AdvisingAppointment from '@/components/appointment/AdvisingAppointment'
import AdvisingNote from '@/components/note/AdvisingNote'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import EditAdvisingNote from '@/components/note/EditAdvisingNote'
import TimelineDate from '@/components/student/profile/TimelineDate'
import {
  mdiCalendarMinus,
  mdiCheckBold,
  mdiClockOutline,
  mdiCloseCircle,
  mdiExclamationThick,
  mdiLinkVariant,
  mdiMenuDown,
  mdiMenuRight,
  mdiMenuUp,
  mdiPaperclip,
  mdiSync
} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {deleteNote, getNote, markNoteRead} from '@/api/notes'
import {dismissStudentAlert} from '@/api/student'
import {markAppointmentRead} from '@/api/appointments'
import {isDirector} from '@/berkeley'
import {alertScreenReader, scrollTo} from '@/lib/utils'
import {DateTime} from 'luxon'
import {capitalize, each, find, includes, map, remove, size, slice} from 'lodash'

export default {
  name: 'AcademicTimelineTable',
  mixins: [Context, Util],
  props: {
    countsPerType: {
      required: true,
      type: Object
    },
    filter: {
      default: undefined,
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
    eventHandlers: undefined,
    isShowingAll: false,
    messageForDelete: undefined,
    openMessages: [],
    searchIndex: undefined,
    searchResults: undefined,
    showMyNotesOnly: false,
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
      return this.filter ? this.countsPerType[this.filter] : size(this.messages)
    },
    deleteConfirmModalBody() {
      return this.messageForDelete ? `Are you sure you want to delete the "<b>${this.messageForDelete.subject}</b>" note?` : ''
    },
    isExpandAllAvailable() {
      return ['appointment', 'eForm', 'note'].includes(this.filter)
    },
    messagesVisible() {
      return (this.searchResults || (this.isShowingAll ? this.messagesPerType(this.filter) : slice(this.messagesPerType(this.filter), 0, this.defaultShowPerTab)))
    },
    offerShowAll() {
      return !this.searchResults && (this.countPerActiveTab > this.defaultShowPerTab)
    },
    showDeleteConfirmModal() {
      return !!this.messageForDelete
    },
    showDownloadNotesLink() {
      const hasNonDrafts = () => {
        const notes = this.messagesPerType('note')
        return find(notes, n => !n.isDraft)
      }
      return ['eForm', 'note'].includes(this.filter)
        && (this.currentUser.isAdmin || isDirector(this.currentUser))
        && hasNonDrafts()
    },
    showMyNotesToggle() {
      return ['appointment', 'note'].includes(this.filter)
    }
  },
  watch: {
    filter() {
      this.allExpanded = false
      this.openMessages = []
      this.searchResults = null
      this.timelineQuery = ''
      alertScreenReader(this.describeTheActiveTab())
      this.refreshSearchIndex()
    },
    isShowingAll() {
      alertScreenReader(this.describeTheActiveTab())
    },
    timelineQuery() {
      if (this.timelineQuery) {
        const query = this.timelineQuery.replace(/\s/g, '').toLowerCase()
        const results = []
        each(this.searchIndex, entry => {
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
    if (this.currentUser.canAccessAdvisingData) {
      this.eventHandlers = {
        'note-creation-is-starting': this.onNoteCreateStartEvent,
        'note-created': this.afterNoteCreated,
        'note-updated': this.afterNoteEdit,
        'notes-created': this.afterNotesCreated
      }
      each(this.eventHandlers, (handler, eventType) => {
        this.setEventHandler(eventType, handler)
      })
    }
    this.sortMessages()
    alertScreenReader(`${this.student.name} profile loaded.`)
  },
  mounted() {
    if (this.anchor) {
      const match = this.anchor.match(/^#(\w+)-([\d\w-]+)/)
      if (match && match.length > 2) {
        const messageType = match[1].toLowerCase()
        const messageId = match[2]
        const obj = find(this.messages, function(m) {
          // Legacy advising notes have string IDs; BOA-created advising notes have integer IDs.
          if (m.id && m.id.toString() === messageId && m.type.toLowerCase() === messageType) {
            return true
          }
        })
        if (obj) {
          this.isShowingAll = true
          const onNextTick = () => {
            this.open(obj, true)
            this.scrollToPermalink(messageType, messageId)
          }
          this.nextTick(onNextTick)
        }
      }
    }
  },
  destroyed() {
    each(this.eventHandlers || {}, (handler, eventType) => {
      this.removeEventHandler(eventType, handler)
    })
  },
  methods: {
    afterEditAdvisingNote(updatedNote) {
      this.editModeNoteId = null
      this.refreshNote(updatedNote)
    },
    afterNoteCreated(note) {
      this.creatingNoteEvent = null
      this.onCreateNewNote(note)
      this.refreshSearchIndex()
    },
    afterNotesCreated(noteIdsBySid) {
      const noteId = noteIdsBySid[this.student.sid]
      if (noteId) {
        getNote(noteId).then(this.afterNoteCreated)
      }
      this.refreshSearchIndex()
    },
    afterNoteEdit(updatedNote) {
      this.refreshNote(updatedNote)
    },
    afterNoteEditCancel() {
      this.editModeNoteId = null
    },
    cancelTheDelete() {
      alertScreenReader('Canceled')
      this.putFocusNextTick(`delete-note-button-${this.messageForDelete.id}`)
      this.messageForDelete = undefined
    },
    close(message, notifyScreenReader) {
      if (this.editModeNoteId) {
        return false
      }
      if (includes(this.openMessages, message.transientId)) {
        this.openMessages = remove(
          this.openMessages,
          id => id !== message.transientId
        )
      }
      if (this.openMessages.length === 0) {
        this.allExpanded = false
      }
      if (notifyScreenReader) {
        alertScreenReader(`${capitalize(message.type)} closed`)
      }
    },
    deleteNote(message) {
      // The following opens the "Are you sure?" modal
      alertScreenReader('Please confirm delete')
      this.messageForDelete = message
    },
    deleteConfirmed() {
      const transientId = this.messageForDelete.transientId
      const predicate = ['transientId', transientId]
      const note = find(this.messages, predicate)
      remove(this.messages, predicate)
      remove(this.openMessages, value => transientId === value)
      this.messageForDelete = undefined
      return deleteNote(note).then(() => {
        alertScreenReader('Note deleted')
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
      this.putFocusNextTick('edit-note-subject')
    },
    getSameDayDate(message) {
      const format = isoDate => DateTime.fromISO(isoDate).setZone(this.config.timezone).toFormat('h:mm a')
      return `${format(message.createdAt)} - ${format(message.endsAt)}`
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
        if (includes(['alert', 'hold'], message.type)) {
          dismissStudentAlert(message.id)
        } else if (['eForm', 'note'].includes(message.type)) {
          markNoteRead(message.id)
        } else if (message.type === 'appointment') {
          markAppointmentRead(message.id)
        }
      }
    },
    messagesPerType(type) {
      if (!type) {
        return this.messages
      } else if (this.showMyNotesToggle && this.showMyNotesOnly) {
        return this._filter(this.messages, m => {
          const uid = (m.author && m.author.uid) || (m.advisor && m.advisor.uid)
          return m.type === type && uid === this.currentUser.uid
        })
      } else {
        return this._filter(this.messages, ['type', type])
      }
    },
    onNoteCreateStartEvent(event) {
      if (includes(event.completeSidSet, this.student.sid)) {
        this.creatingNoteEvent = event
      }
    },
    open(message, notifyScreenReader) {
      if (['eForm', 'note'].includes(message.type) && message.id === this.editModeNoteId || message.type === 'requirement') {
        return false
      }
      if (!includes(this.openMessages, message.transientId)) {
        this.openMessages.push(message.transientId)
      }
      this.markRead(message)
      if (this.isExpandAllAvailable && this.openMessages.length === this.messagesPerType(this.filter).length) {
        this.allExpanded = true
      }
      if (notifyScreenReader) {
        alertScreenReader(`${capitalize(message.type)} opened`)
      }
    },
    refreshNote(updatedNote) {
      const note = find(this.messages, ['id', updatedNote.id])
      if (note) {
        note.attachments = updatedNote.attachments
        note.body = note.message = updatedNote.body
        note.contactType = updatedNote.contactType
        note.isDraft = updatedNote.isDraft
        note.isPrivate = updatedNote.isPrivate
        note.setDate = updatedNote.setDate
        note.subject = updatedNote.subject
        note.topics = updatedNote.topics
        note.updatedAt = updatedNote.updatedAt
        this.refreshSearchIndex()
      }
    },
    refreshSearchIndex() {
      this.searchIndex = []
      const messages = ['appointment', 'eForm', 'note'].includes(this.filter) ? this.messagesPerType(this.filter) : []
      each(messages, m => {
        const advisor = m.author || m.advisor
        const idx = [
          advisor.name,
          (map(advisor.departments || [], 'name')).join(),
          advisor.email,
          m.body,
          m.category,
          m.createdBy,
          JSON.stringify(m.eForm || {}),
          m.legacySource,
          m.message,
          m.subcategory,
          m.subject,
          (m.topics || []).join()
        ].join().replace(/\s/g, '').toLowerCase()
        this.searchIndex.push({idx: idx.toLowerCase(), message: m})
      })
    },
    scrollToPermalink(messageType, messageId) {
      scrollTo(`#permalink-${messageType}-${messageId}`)
      this.putFocusNextTick(`message-row-${messageId}`)
    },
    toggleExpandAll() {
      this.isShowingAll = true
      this.allExpanded = !this.allExpanded
      if (this.allExpanded) {
        each(this.messagesPerType(this.filter), this.open)
        alertScreenReader(`All ${this.filter}s expanded`)
      } else {
        each(this.messagesPerType(this.filter), this.close)
        alertScreenReader(`All ${this.filter}s collapsed`)
      }
    }
  }
}
</script>

<style>
.academic-timeline-search-input input {
  max-height: 30px !important;
  min-height: 30px !important;
  padding: 0 10px;
}
</style>

<style scoped>
.academic-timeline-search-input {
  width: 200px;
}
.close-message {
  width: 100%;
  order: -1;
}
.collapsed-cancelled-icon {
  font-size: 14px;
  min-width: 108px;
  padding-right: 8px;
  text-transform: uppercase;
}
.column-message {
  max-width: 1px;
  padding: 10px 10px 10px 5px;
  vertical-align: middle;
}
.column-pill {
  padding: 8px;
  vertical-align: top;
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
.pill-eForm {
  background-color: #5fbeb6;
  width: 60px;
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
  color: rgb(var(--v-theme-warning));
}
</style>
