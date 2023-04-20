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

export default {
  name: 'AcademicTimeline',
  mixins: [Context],
  components: {
    AcademicTimelineTable,
    AcademicTimelineHeader
  },
  props: {
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    countsPerType: {},
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
    if (this.$currentUser.canAccessAdvisingData) {
      this.filterTypes.eForm = {name: 'EForm', tab: 'eForms'}
      this.filterTypes.note = {name: 'Advising Note', tab: 'Notes'}
      this.filterTypes.appointment = {name: 'Appointment', tab: 'Appointments'}
    }
    this.$_.each(this.$_.keys(this.filterTypes), (type, typeIndex) => {
      let notifications = this.student.notifications[type]
      this.countsPerType[type] = this.$_.size(notifications)
      this.$_.each(notifications, (message, index) => {
        this.messages.push(message)
        // If object is not a BOA advising note then generate a transient and non-zero primary key.
        message.transientId = (typeIndex + 1) * 1000 + index
      })
    })
    this.isTimelineLoading = false
    this.$eventHub.on('note-deleted', this.onDeleteNoteEvent)
  },
  destroyed() {
    this.$eventHub.off('note-deleted', this.onDeleteNoteEvent)
  },
  methods: {
    onCreateNewNote(note) {
      if (note.sid === this.student.sid) {
        const currentNoteIds = this.$_.map(this.$_.filter(this.messages, ['type', 'note']), 'id')
        const isNotInView = !this.$_.includes(currentNoteIds, note.id)
        if (isNotInView) {
          note.transientId = note.id
          this.messages.push(note)
          this.updateCountsPerType('note', this.countsPerType.note + 1)
          this.sortMessages()
          this.$announcer.polite(`New advising note created for student ${this.student.name}.`)
        }
      }
    },
    onDeleteNoteEvent(noteId) {
      const removed = this.$_.remove(this.messages, m => m.type === 'note' && m.id === noteId)
      if (removed) {
        this.updateCountsPerType('note', this.countsPerType.note - 1)
        this.sortMessages()
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
          return this.$moment(message.setDate).tz(this.$config.timezone).utc().format()
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
