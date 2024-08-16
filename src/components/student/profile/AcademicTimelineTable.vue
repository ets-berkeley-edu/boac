<template>
  <div v-if="isExpandAllAvailable" class="align-center d-flex flex-wrap font-size-14">
    <h3 class="sr-only">Quick Links</h3>
    <div class="pl-2 pb-2">
      <v-btn
        :id="`toggle-expand-all-${selectedFilter}s`"
        class="px-1"
        color="primary"
        density="compact"
        :disabled="!messagesVisible.length"
        variant="text"
        @click.prevent="toggleExpandAll"
      >
        <v-icon :icon="allExpanded ? mdiMenuDown : mdiMenuRight" />
        <span class="text-no-wrap">{{ allExpanded ? 'Collapse' : 'Expand' }} all {{ selectedFilter }}s</span>
      </v-btn>
    </div>
    <div v-if="showDownloadNotesLink" class="pl-3 pb-2" role="separator">|</div>
    <div v-if="showDownloadNotesLink" class="pl-3 pb-2">
      <a id="download-notes-link" :href="`${config.apiBaseUrl}/api/notes/${student.sid}/download?type=${selectedFilter}`">Download {{ selectedFilter }}s</a>
    </div>
    <div class="pl-3 pb-2" role="separator">|</div>
    <div class="align-center d-flex pl-3 pb-2">
      <label
        :id="`timeline-${selectedFilter}s-query-label`"
        :for="`timeline-${selectedFilter}s-query-input`"
        class="font-weight-bold mb-0 mr-1 text-no-wrap v-btn--variant-plain"
      >
        Search {{ selectedFilter === 'eForm' ? 'eForm' : capitalize(selectedFilter) }}s:
      </label>
      <v-text-field
        :id="`timeline-${selectedFilter}s-query-input`"
        v-model="timelineQuery"
        :aria-labelledby="`timeline-${selectedFilter}s-query-label`"
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
    <div v-if="showMyNotesToggle" class="pl-3 pb-2" role="separator">|</div>
    <div v-if="showMyNotesToggle" class="pl-3 pb-2">
      <div class="align-center d-flex font-weight-bold">
        <label for="toggle-my-notes-button" class="mr-3" :class="showMyNotesOnly ? 'text-grey' : 'text-primary'">
          All {{ selectedFilter }}s
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
          My {{ selectedFilter }}s
        </label>
      </div>
    </div>
  </div>
  <div
    v-if="!searchResults && !messagesVisible.length"
    id="zero-messages"
    class="font-size-16 font-weight-700 ml-6 my-4 text-grey-darken-1"
  >
    <span v-if="selectedFilter && showMyNotesOnly">No {{ filterTypes[selectedFilter].name.toLowerCase() }}s authored by you.</span>
    <span v-if="selectedFilter && !showMyNotesOnly">No {{ filterTypes[selectedFilter].name.toLowerCase() }}s</span>
    <span v-if="!selectedFilter">None</span>
  </div>
  <div v-if="searchResults" class="ml-3 my-2">
    <h3 id="search-results-header" class="messages-none">
      {{ pluralize(`advising ${selectedFilter}`, searchResults.length) }} for&nbsp;
      <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</span>
      with '{{ timelineQuery }}'
    </h3>
  </div>
  <div v-if="countPerActiveTab">
    <h3 class="sr-only">{{ activeTab === 'all' ? 'All Messages' : `${capitalize(activeTab)}s` }}</h3>
    <table id="timeline-messages" class="w-100">
      <tr class="sr-only">
        <th class="column-pill">Type</th>
        <th class="column-message">Summary</th>
        <th class="column-right">Details</th>
        <th class="column-right">Date</th>
      </tr>
      <tr v-if="creatingNoteEvent" class="message-row-read message-row border-t-sm border-b-sm">
        <td class="column-pill">
          <div class="pill text-center text-uppercase text-white pill-note pa-2">
            <span class="sr-only">Creating new</span> advising note
          </div>
        </td>
        <td class="column-message">
          <div class="d-flex px-2">
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
          <div class="pr-2 float-right text-no-wrap text-grey-darken-2">
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
        :class="{'message-row-read': message.read}"
        class="message-row border-t-sm border-b-sm"
      >
        <td class="column-pill">
          <div class="pa-2">
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
              v-if="isEditable(message) && includes(openMessages, message.transientId)"
              aria-hidden="true"
              class="d-flex flex-column mt-2"
            >
              <v-btn
                v-if="currentUser.uid === message.author.uid && (!message.isPrivate || currentUser.canAccessPrivateNotes)"
                :id="`edit-note-${message.id}-button`"
                class="font-size-14 my-1 px-1"
                color="primary"
                density="compact"
                :disabled="!!editModeNoteId || useNoteStore().disableNewNoteButton"
                variant="text"
                @keypress.enter.stop="editNote(message)"
                @click.stop="editNote(message)"
              >
                Edit {{ message.isDraft ? 'Draft' : 'Note' }}
              </v-btn>
              <v-btn
                v-if="currentUser.isAdmin || (message.isDraft && message.author.uid === currentUser.uid)"
                :id="`delete-note-button-${message.id}`"
                class="font-size-14 my-1 px-1"
                color="primary"
                density="compact"
                :disabled="!!editModeNoteId || useNoteStore().disableNewNoteButton"
                variant="text"
                @keydown.enter.stop="onClickDeleteNote(message)"
                @click.stop="onClickDeleteNote(message)"
              >
                Delete {{ message.isDraft ? 'Draft' : 'Note' }}
              </v-btn>
            </div>
          </div>
        </td>
        <td
          :class="{'font-weight-bold': !message.read}"
          class="column-message"
        >
          <div
            :id="`timeline-tab-${activeTab}-message-${index}`"
            :aria-pressed="includes(openMessages, message.transientId)"
            class="pl-2"
            :class="{
              'message-open': includes(openMessages, message.transientId) && message.type !== 'requirement' ,
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
              :delete-note="onClickDeleteNote"
              :edit-note="editNote"
              :is-open="includes(openMessages, message.transientId)"
              :note="message"
            />
            <EditAdvisingNote
              v-if="['eForm', 'note'].includes(message.type) && message.id === editModeNoteId"
              :after-cancel="afterNoteEditCancel"
              :after-saved="afterEditAdvisingNote"
              class="pt-2"
              :note-id="message.id"
            />
            <AdvisingAppointment
              v-if="message.type === 'appointment'"
              :appointment="message"
              :is-open="includes(openMessages, message.transientId)"
              :student="student"
            />
            <div
              v-if="includes(openMessages, message.transientId) && message.id !== editModeNoteId"
              class="my-1 text-center close-message"
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
        <td class="column-right">
          <div v-if="!includes(openMessages, message.transientId) && message.type === 'appointment'" class="pa-2">
            <div
              v-if="message.createdBy === 'YCBM' && message.status === 'cancelled'"
              :id="`collapsed-${message.type}-${message.id}-status-cancelled`"
              class="collapsed-cancelled-icon text-error"
            >
              <v-icon :icon="mdiCalendarMinus" class="status-cancelled-icon" />
              Canceled
            </div>
          </div>
          <div v-if="['appointment', 'eForm', 'note'].includes(message.type)" class="pa-2">
            <v-icon v-if="size(message.attachments)" color="info" :icon="mdiPaperclip" />
            <span class="sr-only">{{ size(message.attachments) ? 'Has attachments' : 'No attachments' }}</span>
          </div>
        </td>
        <td class="column-right">
          <div
            :id="`timeline-tab-${activeTab}-date-${index}`"
            class="text-no-wrap py-2 pr-2"
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
                <div class="text-grey-darken-2 font-size-14">{{ message.type === 'appointment' ? 'Appt Date' : 'Created' }}:</div>
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
                <div class="mt-2 text-grey-darken-2 font-size-14">Updated:</div>
                <TimelineDate
                  :id="`expanded-${message.type}-${message.id}-updated-at`"
                  :date="message.updatedAt"
                  :include-time-of-day="message.updatedAt.length > 10"
                  class="mb-2"
                  sr-prefix="Last updated on"
                />
              </div>
              <div v-if="message.setDate">
                <div class="mt-2 text-grey-darken-2 font-size-14">Set Date:</div>
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
                  @click="scrollToPermalink(message.type, message.id)"
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
  <div v-if="offerShowAll" class="text-center pb-4">
    <v-btn
      :id="`timeline-tab-${activeTab}-previous-messages`"
      class="text-no-wrap"
      color="primary"
      density="comfortable"
      variant="text"
      @click="toggleShowAll"
    >
      <v-icon :icon="isShowingAll ? mdiMenuUp : mdiMenuRight" />
      {{ isShowingAll ? 'Hide' : 'Show' }} Previous Messages
    </v-btn>
  </div>
  <AreYouSureModal
    v-model="showDeleteConfirmModal"
    button-label-confirm="Delete"
    :function-cancel="cancelTheDelete"
    :function-confirm="deleteConfirmed"
    modal-header="Delete note"
  >
    Are you sure you want to delete the <span v-if="messageForDelete">"<b>{{ messageForDelete.subject }}</b>"</span> note?
  </AreYouSureModal>
</template>

<script setup>
import AdvisingAppointment from '@/components/appointment/AdvisingAppointment'
import AdvisingNote from '@/components/note/AdvisingNote'
import {alertScreenReader, pluralize, putFocusNextTick, scrollTo} from '@/lib/utils'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import {capitalize, each, filter, find, get, includes, map, remove, size, slice} from 'lodash'
import {computed, nextTick, onMounted, onUnmounted, ref, watch} from 'vue'
import {DateTime} from 'luxon'
import {deleteNote, getNote, markNoteRead} from '@/api/notes'
import {dismissStudentAlert} from '@/api/student'
import EditAdvisingNote from '@/components/note/EditAdvisingNote'
import {isDirector} from '@/berkeley'
import {markAppointmentRead} from '@/api/appointments'
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
import TimelineDate from '@/components/student/profile/TimelineDate'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session/index'

const props = defineProps({
  countPerActiveTab: {
    required: true,
    type: Number
  },
  selectedFilter: {
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
})

const allExpanded = ref(false)
const config = useContextStore().config
const creatingNoteEvent = ref(undefined)
const currentUser = useContextStore().currentUser
const defaultShowPerTab = ref(5)
const editModeNoteId = ref(undefined)
const eventHandlers = ref(undefined)
const isShowingAll = ref(false)
const messageForDelete = ref(undefined)
const openMessages = ref([])
const searchIndex = ref(undefined)
const searchResults = ref(undefined)
const showMyNotesOnly = ref(false)
const timelineQuery = ref('')

const activeTab = computed(() => props.selectedFilter || 'all')
const anchor = computed(() => location.hash)
const isExpandAllAvailable = computed(() => ['appointment', 'eForm', 'note'].includes(props.selectedFilter))
const messagesVisible = computed(() => {
  return (searchResults.value || (isShowingAll.value ? messagesPerType(props.selectedFilter) : slice(messagesPerType(props.selectedFilter), 0, defaultShowPerTab.value)))
})
const offerShowAll = computed(() => !searchResults.value && (props.countPerActiveTab > defaultShowPerTab.value))
const showDeleteConfirmModal = computed(() => !!messageForDelete.value)
const showDownloadNotesLink = computed(() => {
  const hasNonDrafts = () => {
    const notes = messagesPerType('note')
    return find(notes, n => !n.isDraft)
  }
  return ['eForm', 'note'].includes(props.selectedFilter)
    && (currentUser.isAdmin || isDirector(currentUser))
    && hasNonDrafts()
})
const showMyNotesToggle = computed(() => ['appointment', 'note'].includes(props.selectedFilter))

watch(() => props.selectedFilter, () => {
  allExpanded.value = false
  openMessages.value = []
  searchResults.value = null
  timelineQuery.value = ''
  alertScreenReader(describeTheActiveTab())
  refreshSearchIndex()
})

watch(timelineQuery, () => {
  if (timelineQuery.value) {
    const query = timelineQuery.value.replace(/\s/g, '').toLowerCase()
    const results = []
    each(searchIndex.value, entry => {
      if (entry.idx.indexOf(query) > -1) {
        results.push(entry.message)
      }
    })
    searchResults.value = results
  } else {
    searchResults.value = null
  }
})

const init = () => {
  refreshSearchIndex()
  if (currentUser.canAccessAdvisingData) {
    eventHandlers.value = {
      'note-creation-is-starting': onNoteCreateStartEvent,
      'note-created': afterNoteCreated,
      'note-updated': afterNoteEdit,
      'notes-created': afterNotesCreated
    }
    each(eventHandlers.value, (handler, eventType) => {
      useContextStore().setEventHandler(eventType, handler)
    })
  }
  props.sortMessages()
  alertScreenReader(`${props.student.name} profile loaded.`)
}

onMounted(() => {
  if (anchor.value) {
    const match = anchor.value.match(/^#(\w+)-([\d\w-]+)/)
    if (match && match.length > 2) {
      const messageType = match[1].toLowerCase()
      const messageId = match[2]
      const obj = find(props.messages, function(m) {
        // Legacy advising notes have string IDs; BOA-created advising notes have integer IDs.
        if (m.id && m.id.toString() === messageId && m.type.toLowerCase() === messageType) {
          return true
        }
      })
      if (obj) {
        isShowingAll.value = true
        const onNextTick = () => {
          open(obj, true)
          scrollToPermalink(messageType, messageId)
        }
        nextTick(onNextTick)
      }
    }
  }
})

onUnmounted(() => {
  each(eventHandlers.value || {}, (handler, eventType) => {
    useContextStore().removeEventHandler(eventType, handler)
  })
})

const afterEditAdvisingNote = updatedNote => {
  editModeNoteId.value = null
  refreshNote(updatedNote)
  putFocusNextTick(`edit-note-${updatedNote.id}-button`)
}

const afterNoteCreated = note => {
  creatingNoteEvent.value = null
  props.onCreateNewNote(note)
  refreshSearchIndex()
}

const afterNotesCreated = noteIdsBySid => {
  const noteId = noteIdsBySid[props.student.sid]
  if (noteId) {
    getNote(noteId).then(afterNoteCreated)
  }
  refreshSearchIndex()
}

const afterNoteEdit = updatedNote => {
  refreshNote(updatedNote)
}

const afterNoteEditCancel = () => {
  putFocusNextTick(`edit-note-${editModeNoteId.value}-button`)
  editModeNoteId.value = null
}

const cancelTheDelete = () => {
  alertScreenReader('Canceled')
  putFocusNextTick(`delete-note-button-${messageForDelete.value.id}`)
  messageForDelete.value = undefined
}

const close = (message, notifyScreenReader) => {
  if (editModeNoteId.value) {
    return false
  }
  if (includes(openMessages.value, message.transientId)) {
    openMessages.value = remove(
      openMessages.value,
      id => id !== message.transientId
    )
  }
  if (openMessages.value.length === 0) {
    allExpanded.value = false
  }
  if (notifyScreenReader) {
    alertScreenReader(`${capitalize(message.type)} closed`)
  }
}

const deleteConfirmed = () => {
  const transientId = messageForDelete.value.transientId
  const predicate = ['transientId', transientId]
  const note = find(props.messages, predicate)
  remove(props.messages, predicate)
  remove(openMessages.value, value => transientId === value)
  messageForDelete.value = undefined
  return deleteNote(note).then(() => {
    alertScreenReader('Note deleted')
    refreshSearchIndex()
  })
}

const describeTheActiveTab = () => {
  const inViewCount = isShowingAll.value || props.countPerActiveTab <= defaultShowPerTab.value ? props.countPerActiveTab : defaultShowPerTab.value
  const noun = props.selectedFilter ? props.filterTypes[props.selectedFilter].name.toLowerCase() : 'message'
  const pluralized = pluralize(noun, inViewCount)
  return isShowingAll.value && inViewCount > defaultShowPerTab.value
    ? `Showing all ${pluralized}`
    : `Showing ${props.countPerActiveTab > defaultShowPerTab.value ? 'the first' : ''} ${pluralized}`
}

const displayUpdatedAt = message => {
  return message.updatedAt && (message.updatedAt !== message.createdAt) && (message.type !== 'appointment')
}

const editNote = note => {
  editModeNoteId.value = note.id
  putFocusNextTick('edit-note-subject')
}

const formatDate = (isoDate, format) => DateTime.fromISO(isoDate).setZone(config.timezone).toFormat(format)

const getSameDayDate = message => {
  const format = 'h:mm a'
  return `${formatDate(message.createdAt, format)} - ${formatDate(message.endsAt, format)}`
}

const isEditable = message => {
  return message.type === 'note' && !message.legacySource
}

const markRead = message => {
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
}

const messagesPerType = type => {
  if (!type) {
    return props.messages
  } else if (showMyNotesToggle.value && showMyNotesOnly.value) {
    return filter(props.messages, m => {
      const uid = (m.author && m.author.uid) || (m.advisor && m.advisor.uid)
      return m.type === type && uid === currentUser.uid
    })
  } else {
    return filter(props.messages, ['type', type])
  }
}

const onClickDeleteNote = message => {
  // The following opens the "Are you sure?" modal
  alertScreenReader('Please confirm delete')
  messageForDelete.value = message
}

const onNoteCreateStartEvent = event => {
  if (includes(event.completeSidSet, props.student.sid)) {
    creatingNoteEvent.value = event
  }
}

const open = (message, notifyScreenReader) => {
  if (['eForm', 'note'].includes(message.type) && message.id === editModeNoteId.value || message.type === 'requirement') {
    return false
  }
  if (!includes(openMessages.value, message.transientId)) {
    openMessages.value.push(message.transientId)
  }
  markRead(message)
  if (isExpandAllAvailable.value && openMessages.value.length === messagesPerType(props.selectedFilter).length) {
    allExpanded.value = true
  }
  if (notifyScreenReader) {
    alertScreenReader(`${capitalize(message.type)} opened`)
  }
}

const refreshNote = updatedNote => {
  const note = get(updatedNote, 'id') ? find(props.messages, ['id', updatedNote.id]) : null
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
    refreshSearchIndex()
  }
}

const refreshSearchIndex = () => {
  searchIndex.value = []
  const messages = ['appointment', 'eForm', 'note'].includes(props.selectedFilter) ? messagesPerType(props.selectedFilter) : []
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
    searchIndex.value.push({idx: idx.toLowerCase(), message: m})
  })
}

const scrollToPermalink = (messageType, messageId) => {
  scrollTo(`permalink-${messageType}-${messageId}`)
  putFocusNextTick(`message-row-${messageId}`)
}

const toggleExpandAll = () => {
  isShowingAll.value = true
  allExpanded.value = !allExpanded.value
  if (allExpanded.value) {
    each(messagesPerType(props.selectedFilter), open)
    alertScreenReader(`All ${props.selectedFilter}s expanded`)
  } else {
    each(messagesPerType(props.selectedFilter), close)
    alertScreenReader(`All ${props.selectedFilter}s collapsed`)
  }
}

const toggleShowAll = () => {
  isShowingAll.value = !isShowingAll.value
  alertScreenReader(describeTheActiveTab())
}

init()

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
  vertical-align: middle;
  max-width: 1px;
}
.column-pill {
  max-width: 115px;
  vertical-align: top;
  white-space: nowrap;
  width: 115px;
}
.column-right {
  align-content: start;
  text-align: right;
  width: 1%;
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
  background-color: rgb(var(--v-theme-light-grey));
}
.pill-alert {
  /* used by dynamic class attribute  */
  background-color: #eb9d3e;
  width: 60px;
}
.pill-appointment {
  /* used by dynamic class attribute  */
  background-color: #eee;
  color: #666 !important;
  font-weight: bolder;
  width: 100px;
}
.pill-eForm {
  /* used by dynamic class attribute  */
  background-color: #5fbeb6;
  width: 60px;
}
.pill-hold {
  /* used by dynamic class attribute  */
  background-color: #bc74fe;
  width: 60px;
}
.pill-note {
  background-color: #999;
  width: 100px;
}
.pill-requirement {
  /* used by dynamic class attribute  */
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
table {
  border-collapse: collapse;
  border-spacing: 0 0.05em;
  min-width: 500px;
}
</style>
