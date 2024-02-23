<template>
  <div v-if="!isTimelineLoading">
    <div class="mb-2">
      <AcademicTimelineHeader
        :counts-per-type="countsPerType"
        :filter="filter"
        :filter-types="filterTypes"
        :set-filter="setFilter"
        :student="student"
      />
    </div>
    <div>
      <AcademicTimelineTable
        :counts-per-type="countsPerType"
        :filter="filter"
        :filter-types="filterTypes"
        :messages="messages"
        :on-create-new-note="onCreateNewNote"
        :sort-messages="sortMessages"
        :student="student"
      />
    </div>
  </div>
</template>

<script>
import AcademicTimelineHeader from '@/components/student/profile/AcademicTimelineHeader'
import AcademicTimelineTable from '@/components/student/profile/AcademicTimelineTable'
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {getNote} from '@/api/notes'

export default {
  name: 'AcademicTimeline',
  components: {
    AcademicTimelineTable,
    AcademicTimelineHeader
  },
  mixins: [Context, Util],
  props: {
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    countsPerType: {},
    eventHandlers: undefined,
    filter: undefined,
    filterTypes: undefined,
    isTimelineLoading: true,
    messages: undefined
  }),
  created() {
    this.messages = []
    this.filterTypes = {
      alert: {name: 'Alert', tab: 'Alerts'},
      hold: {name: 'Hold', tab: 'Holds'},
      requirement: {name: 'Requirement', tab: 'Reqs'}
    }
    if (this.currentUser.canAccessAdvisingData) {
      this.filterTypes.eForm = {name: 'EForm', tab: 'eForms'}
      this.filterTypes.note = {name: 'Advising Note', tab: 'Notes'}
      this.filterTypes.appointment = {name: 'Appointment', tab: 'Appointments'}
    }
    this._each(this._keys(this.filterTypes), (type, typeIndex) => {
      let notifications = this.student.notifications[type]
      this.countsPerType[type] = this._size(notifications)
      this._each(notifications, (message, index) => {
        this.messages.push(message)
        // If object is not a BOA advising note then generate a transient and non-zero primary key.
        message.transientId = (typeIndex + 1) * 1000 + index
      })
    })
    this.isTimelineLoading = false
    this.eventHandlers = {
      'note-deleted': this.onDeleteNoteEvent,
      'notes-batch-published': this.onPublishBatchNotes
    }
    this._each(this.eventHandlers, (handler, eventType) => {
      this.setEventHandler(eventType, handler)
    })
  },
  destroyed() {
    this._each(this.eventHandlers || {}, (handler, eventType) => {
      this.removeEventHandler(eventType, handler)
    })
  },
  methods: {
    onCreateNewNote(note) {
      if (note.sid === this.student.sid) {
        const currentNoteIds = this._map(this._filter(this.messages, ['type', 'note']), 'id')
        const isNotInView = !this._includes(currentNoteIds, note.id)
        if (isNotInView) {
          note.transientId = note.id
          this.messages.push(note)
          this.updateCountsPerType('note', this.countsPerType.note + 1)
          this.sortMessages()
          this.alertScreenReader(`New advising note created for student ${this.student.name}.`)
        }
      }
    },
    onDeleteNoteEvent(noteId) {
      const removed = this._remove(this.messages, m => m.type === 'note' && m.id === noteId)
      if (removed) {
        this.updateCountsPerType('note', this.countsPerType.note - 1)
        this.sortMessages()
      }
    },
    onPublishBatchNotes(noteIdsBySid) {
      const noteId = this._get(noteIdsBySid, this.student.sid)
      if (noteId) {
        getNote(noteId).then(note => {
          this.onCreateNewNote(note)
        })
      }
    },
    setFilter(filter) {
      this.lastTimelineQuery = null
      this.searchResults = null
      this.timelineQuery = null
      if (filter !== this.filter) {
        this.filter = filter
        this.allExpanded = false
      }
    },
    sortDate(message) {
      if (message.type === 'appointment' || message.type === 'note') {
        if (message.setDate) {
          return this.moment(message.setDate).tz(this.config.timezone).utc().format()
        } else {
          return message.createdAt
        }
      } else {
        return message.updatedAt || message.createdAt
      }
    },
    sortMessages() {
      this.messages.sort((m1, m2) => {
        let d1 = this.sortDate(m1)
        let d2 = this.sortDate(m2)
        if (d1 && d2 && d1 !== d2) {
          return d2.localeCompare(d1)
        } else if (d1 === d2 && m1.id && m2.id) {
          return m2.id < m1.id ? -1 : 1
        } else if (!d1 && !d2) {
          return m2.transientId - m1.transientId
        } else {
          return d1 ? -1 : 1
        }
      })
    },
    updateCountsPerType(type, count) {
      this.countsPerType[type] = count
    }
  }
}
</script>
