<template>
  <div v-if="!isTimelineLoading">
    <AcademicTimelineHeader
      :counts-per-type="countsPerType"
      :filter="selectedFilter"
      :filter-types="filterTypes"
      :set-filter="setFilter"
      :student="student"
    />
    <div class="pt-3">
      <AcademicTimelineTable
        :count-per-active-tab="selectedFilter ? countsPerType[selectedFilter] : size(messages)"
        :filter="selectedFilter"
        :filter-types="filterTypes"
        :messages="messages"
        :on-create-new-note="onCreateNewNote"
        :sort-messages="sortMessages"
        :student="student"
      />
    </div>
  </div>
</template>

<script setup>
import AcademicTimelineHeader from '@/components/student/profile/AcademicTimelineHeader'
import AcademicTimelineTable from '@/components/student/profile/AcademicTimelineTable'
import {alertScreenReader} from '@/lib/utils'
import {get, each, findIndex, keys, remove, size} from 'lodash'
import {getNote} from '@/api/notes'
import {DateTime} from 'luxon'
import {onUnmounted, reactive, ref} from 'vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  student: {
    required: true,
    type: Object
  }
})

const countsPerType = ref({})
const currentUser = reactive(useContextStore().currentUser)
const eventHandlers = ref(undefined)
const filterTypes = ref(undefined)
const isTimelineLoading = ref(true)
const messages = ref(undefined)
const selectedFilter = ref(undefined)

const init = () => {
  messages.value = []
  filterTypes.value = {
    alert: {name: 'Alert', tab: 'Alerts', tabWidth: 65},
    hold: {name: 'Hold', tab: 'Holds', tabWidth: 62},
    requirement: {name: 'Requirement', tab: 'Reqs', tabWidth: 58}
  }
  if (currentUser.canAccessAdvisingData) {
    filterTypes.value.eForm = {name: 'EForm', tab: 'eForms', tabWidth: 76}
    filterTypes.value.note = {name: 'Advising Note', tab: 'Notes', tabWidth: 64}
    filterTypes.value.appointment = {name: 'Appointment', tab: 'Appointments', tabWidth: 126}
  }
  each(keys(filterTypes.value), (type, typeIndex) => {
    let notifications = props.student.notifications[type]
    countsPerType.value[type] = size(notifications)
    each(notifications, (message, index) => {
      messages.value.push(message)
      // If object is not a BOA advising note then generate a transient and non-zero primary key.
      message.transientId = (typeIndex + 1) * 1000 + index
    })
  })
  isTimelineLoading.value = false
  eventHandlers.value = {
    'note-deleted': onDeleteNoteEvent,
    'note-updated': onNoteUpdated,
    'notes-batch-published': onPublishBatchNotes
  }
  each(eventHandlers.value, (handler, eventType) => {
    useContextStore().setEventHandler(eventType, handler)
  })
}

const onCreateNewNote = note => {
  if (note.sid === props.student.sid) {
    const existingNoteIndex = findIndex(messages.value, {'id': note.id})
    if (existingNoteIndex < 0) {
      note.transientId = note.id
      messages.value.push(note)
      updateCountsPerType('note', countsPerType.value.note + 1)
      sortMessages()
      alertScreenReader(`New advising note created for student ${props.student.name}.`)
    } else {
      messages.value.splice(existingNoteIndex, 1, note)
    }
  }
}

const onDeleteNoteEvent = noteId => {
  const removed = remove(messages.value, m => m.type === 'note' && m.id === noteId)
  if (removed) {
    updateCountsPerType('note', countsPerType.value.note - 1)
    sortMessages()
  }
}

const onNoteUpdated = note => {
  if (note.sid === props.student.sid) {
    getNote(note.id).then(note => {
      onCreateNewNote(note)
    })
  }
}

const onPublishBatchNotes = noteIdsBySid => {
  const noteId = get(noteIdsBySid, props.student.sid)
  if (noteId) {
    getNote(noteId).then(note => {
      onCreateNewNote(note)
    })
  }
}

const setFilter = filter => {
  if (selectedFilter.value !== filter) {
    selectedFilter.value = filter
  }
}

const sortDate = message => {
  if (message.type === 'appointment' || message.type === 'note') {
    if (message.setDate) {
      return DateTime.fromJSDate(message.setDate).setZone(useContextStore().config.timezone).toUTC().toString()
    } else {
      return message.createdAt
    }
  } else {
    return message.updatedAt || message.createdAt
  }
}

const sortMessages = () => {
  messages.value.sort((m1, m2) => {
    let d1 = sortDate(m1)
    let d2 = sortDate(m2)
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
}

const updateCountsPerType = (type, count) => {
  countsPerType.value[type] = count
}

onUnmounted(() => {
  each(eventHandlers.value || {}, (handler, eventType) => {
    useContextStore().removeEventHandler(eventType, handler)
  })
})

init()

</script>
