<template>
  <div
    v-if="!isTimelineLoading"
    aria-labelledby="student-academic-timeline-header"
    role="region"
  >
    <AcademicTimelineHeader
      :counts-per-type="countsPerType"
      :filter="selectedFilter"
      :filter-types="filterTypes"
      :set-filter="setFilter"
      :student="student"
    />
    <div
      :class="{
        'border-sm': !!messages.length,
        'pt-3': ['appointment', 'eForm', 'note'].includes(selectedFilter) && countsPerType[selectedFilter]
      }"
    >
      <AcademicTimelineTable
        :count-per-active-tab="selectedFilter ? countsPerType[selectedFilter] : size(messages)"
        :selected-filter="selectedFilter"
        :filter-types="filterTypes"
        :messages="messages"
        :on-note-updated="onCreateOrUpdateNote"
        :student="student"
      />
    </div>
  </div>
</template>

<script setup>
import {DateTime} from 'luxon'
import {cloneDeep, each, find, findIndex, get, keys, remove, size} from 'lodash'
import {onMounted, onUnmounted, ref} from 'vue'
import AcademicTimelineHeader from '@/components/student/profile/academic-timeline/AcademicTimelineHeader'
import AcademicTimelineTable from '@/components/student/profile/academic-timeline/AcademicTimelineTable'
import {getNote} from '@/api/notes'
import {updateNoteComments} from '@/lib/note'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  student: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()

const countsPerType = ref({})
const currentUser = contextStore.currentUser
const eventHandlers = ref(undefined)
const filterTypes = ref(undefined)
const isTimelineLoading = ref(true)
const messages = ref([])
const selectedFilter = ref(undefined)

onMounted(() => {
  filterTypes.value = {
    alert: {name: 'Alert', tab: 'Alerts', tabWidth: 65},
    hold: {name: 'Hold', tab: 'Holds', tabWidth: 62},
    requirement: {ariaLabel: 'requirements', name: 'Requirement', tab: 'Reqs', tabWidth: 58}
  }
  if (currentUser.canAccessAdvisingData) {
    filterTypes.value.eForm = {name: 'eForm', tab: 'eForms', tabWidth: 76}
    filterTypes.value.note = {name: 'Advising Note', tab: 'Notes', tabWidth: 64}
    filterTypes.value.appointment = {name: 'Appointment', tab: 'Appointments', tabWidth: 126}
  }
  each(keys(filterTypes.value), (type, typeIndex) => {
    const notifications = props.student.notifications[type] || []
    countsPerType.value[type] = size(notifications)
    each(notifications, (notification, index) => {
      const message = cloneDeep(notification)
      // If object is not a BOA advising note then generate a transient and non-zero primary key.
      message.transientId = (typeIndex + 1) * 1000 + index
      if (!message.id) {
        message.id = message.transientId
      }
      messages.value.push(message)
    })
  })
  countsPerType.value['all'] = messages.value.length
  sortMessages()
  isTimelineLoading.value = false
  eventHandlers.value = {
    'note-deleted': onDeleteNoteEvent,
    'notes-batch-published': onPublishBatchNotes
  }
  each(eventHandlers.value, (handler, eventType) => {
    contextStore.setEventHandler(eventType, handler)
  })
})

const onCreateOrUpdateNote = note => {
  return new Promise(resolve => {
    if (note.sid === props.student.sid) {
      const noteId = note.parentNoteId || note.id
      const message = find(messages.value, ['id', noteId])
      note.transientId = message ? message.transientId : noteId
      if (message) {
        const existingNoteIndex = findIndex(messages.value, {'id': noteId})
        if (note.parentNoteId) {
          updateNoteComments(message, note)
        } else {
          messages.value.splice(existingNoteIndex, 1, note)
        }
      } else {
        messages.value.push(note)
        updateCountsPerType('note', countsPerType.value.note + 1)
      }
      sortMessages()
      resolve()
    } else {
      resolve()
    }
  })
}

const onDeleteNoteEvent = noteId => {
  const removed = remove(messages.value, m => m.type === 'note' && m.id === noteId)
  if (removed) {
    updateCountsPerType('note', countsPerType.value.note - 1)
    sortMessages()
  }
}

const onPublishBatchNotes = noteIdsBySid => {
  const noteId = get(noteIdsBySid, props.student.sid)
  if (noteId) {
    getNote(noteId).then(note => {
      onCreateOrUpdateNote(note)
    })
  }
}

const setFilter = filter => {
  if (selectedFilter.value !== filter) {
    selectedFilter.value = filter
  }
}

const sortDate = message => {
  let date
  if (message.type === 'appointment' || message.type === 'note') {
    date = message.startsAt || message.setDate || message.createdAt
  } else {
    date = message.updatedAt || message.createdAt
  }
  return date ? DateTime.fromISO(date).setZone(contextStore.config.timezone).toString() : date
}

const sortMessages = () => {
  messages.value.sort((m1, m2) => {
    const d1 = sortDate(m1)
    const d2 = sortDate(m2)
    let result
    if (d1 && d2 && d1 !== d2) {
      result = d2.localeCompare(d1)
    } else if (d1 === d2 && m1.id && m2.id) {
      result = m2.id < m1.id ? -1 : 1
    } else if (!d1 && !d2) {
      result = m2.transientId - m1.transientId
    } else {
      result = d1 ? -1 : 1
    }
    return result
  })
}

const updateCountsPerType = (type, count) => {
  countsPerType.value[type] = count
}

onUnmounted(() => {
  each(eventHandlers.value || {}, (handler, eventType) => {
    contextStore.removeEventHandler(eventType, handler)
  })
})
</script>
