<template>
  <div>
    <v-expand-transition>
      <div v-if="isExpandAllAvailable" class="align-center d-flex flex-wrap font-size-14">
        <div class="sr-only">Quick Links</div>
        <div class="pb-2 pl-2 toggle-expand-all-container">
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
            <span class="text-no-wrap">{{ allExpanded ? 'Collapse' : 'Expand' }} all<span class="sr-only"> {{ selectedFilter }}s</span></span>
          </v-btn>
        </div>
        <div v-if="showDownloadNotesLink" :aria-hidden="true" class="pl-3 pb-2">|</div>
        <div v-if="showDownloadNotesLink" class="pl-3 pb-2">
          <a
            id="download-notes-link"
            :href="`${config.apiBaseUrl}/api/notes/${student.sid}/download?type=${selectedFilter}`"
          >
            Download {{ selectedFilter }}s
          </a>
        </div>
        <div :aria-hidden="true" class="pl-3 pb-2">|</div>
        <div class="align-center d-flex pb-2 pl-4">
          <label
            :id="`timeline-${selectedFilter}s-query-input-label`"
            :for="`timeline-${selectedFilter}s-query-input`"
            :class="{'text-medium-emphasis': !messagesVisible.length}"
            class="font-weight-bold mb-0 mr-2 text-no-wrap v-btn--variant-plain"
          >
            Search<span class="sr-only"> {{ selectedFilter === 'eForm' ? 'eForm' : capitalize(selectedFilter) }}s</span>:
          </label>
          <v-text-field
            :id="`timeline-${selectedFilter}s-query-input`"
            v-model="timelineQuery"
            :aria-labelledby="undefined"
            autocomplete="on"
            bg-color="pale-blue"
            class="academic-timeline-search-input"
            color="primary"
            :disabled="!messagesVisible.length && !timelineQuery"
            flat
            hide-details
            type="search"
          />
        </div>
        <div v-if="['appointment', 'note'].includes(selectedFilter)" class="align-center d-flex pl-4">
          <div :aria-hidden="true" class="pb-2">|</div>
          <div class="align-center d-flex flex-wrap pb-2 pl-4">
            <span aria-hidden="true" class="font-weight-bold text-medium-emphasis mr-2">
              Show {{ selectedFilter }}s:
            </span>
            <v-btn-toggle
              v-model="filterWithinTheTab"
              class="border-sm btn-toggle-showing-subset"
              color="primary"
              density="compact"
              divided
              mandatory
              variant="flat"
            >
              <v-btn
                id="show-all-items"
                :aria-label="`Show all ${selectedFilter}s`"
                color="primary"
                density="compact"
                text="All "
                value="all"
              />
              <v-btn
                id="show-items-created-by-me"
                :aria-label="`Show ${selectedFilter}s created by me`"
                color="primary"
                density="compact"
                text="Mine"
                value="mine"
              />
              <v-btn
                v-if="selectedFilter === 'note'"
                id="show-items-created-by-my-department"
                :aria-label="`Show ${selectedFilter}s created by my department`"
                color="primary"
                density="compact"
                text="My Department"
                value="department"
              />
            </v-btn-toggle>
          </div>
        </div>
      </div>
    </v-expand-transition>
    <div
      v-if="!searchResults && !messagesVisible.length"
      id="zero-messages"
      aria-live="polite"
      :class="{'mb-6 mt-4': selectedFilter, 'mb-8': !selectedFilter}"
      class="font-size-16 ml-6 text-medium-emphasis"
    >
      <span v-if="selectedFilter">
        No {{ filterTypes[selectedFilter].name.toLowerCase() }}s
        <span v-if="filterWithinTheTab === 'mine'">authored by you.</span>
        <span v-if="filterWithinTheTab === 'department'">authored by your department.</span>
      </span>
      <span v-if="!selectedFilter">None</span>
    </div>
    <div v-if="searchResults" class="mb-4 ml-8 mt-2">
      <div id="search-results-header" class="font-size-16 font-weight-500" role="status">
        {{ pluralize(`advising ${selectedFilter}`, searchResults.length, {1: 'One'}) }} for
        <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</span>
        with '{{ trim(timelineQuery) }}'
      </div>
    </div>
    <div v-if="countPerActiveTab" id="timeline-messages" class="w-100">
      <article
        v-for="(message, index) in messagesVisible"
        :id="`timeline-${message.type}-${message.id}`"
        :key="index"
        class="message-row border-t-sm border-b-sm"
        :class="{
          'expanded': isExpanded(message),
          'message-row-read': message.read
        }"
        tabindex="-1"
      >
        <div class="d-flex">
          <div class="column-pill">
            <AcademicTimelineCategory
              :label="message.type === 'note' && message.peerAdvisingDepartmentId ? 'Peer Note' : filterTypes[message.type].name"
              :message="message"
            />
          </div>
          <div class="column-message" :class="{'font-weight-bold': !message.read}">
            <div class="d-flex flex-column">
              <v-btn
                v-if="isExpanded(message) && (!editModeNoteId || message.id !== editModeNoteId)"
                :id="`${activeTab}-close-message-${message.id}`"
                :aria-controls="`timeline-tab-${activeTab}-message-${message.type}-${message.id}`"
                :aria-expanded="true"
                :aria-label="`Close Message ${getButtonAriaLabel(message)}`"
                class="ma-2"
                color="primary"
                density="compact"
                :prepend-icon="mdiCloseCircle"
                text="Close Message"
                variant="text"
                @click.stop="onClickCloseMessage(message)"
              />
              <div
                v-if="message.type === 'requirement'"
                :id="`timeline-tab-${activeTab}-message-${message.type}-${message.id}`"
                class="w-100"
                :class="{'message-open pb-4 pt-2': isExpanded(message)}"
              >
                <div
                  :id="`requirement-${message.id}-is-${isExpanded(message) ? 'open' : 'closed'}`"
                  :aria-controls="isExpanded(message) ? undefined : `timeline-tab-${activeTab}-message-${message.type}-${message.id}`"
                  :aria-expanded="isExpanded(message) ? undefined : false"
                  class="timeline-requirement"
                  :class="{
                    'cursor-pointer': !isExpanded(message),
                    'timeline-message-full-width': isExpanded(message)
                  }"
                  :role="isExpanded(message) ? undefined : 'button'"
                  :tabindex="isExpanded(message) ? undefined : 0"
                  @click="onClickOpenMessage(message)"
                  @keyup.enter="onClickOpenMessage(message)"
                >
                  <div class="d-flex flex-nowrap">
                    <v-icon
                      v-if="message.status === 'Satisfied'"
                      :icon="mdiCheckBold"
                      class="requirements-icon"
                      color="success"
                    />
                    <v-icon
                      v-if="message.status === 'Not Satisfied'"
                      :icon="mdiExclamationThick"
                      class="requirements-icon"
                      color="warning"
                    />
                    <v-icon
                      v-if="message.status === 'In Progress'"
                      :icon="mdiClockOutline"
                      class="requirements-icon"
                      color="info"
                    />
                    <div :class="{'truncate-with-ellipsis': !isExpanded(message)}">
                      <span class="sr-only">{{ message.status }}: {{ message.name }}</span>
                      <span :aria-hidden="true">{{ message.message }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div
                v-if="message.type !== 'requirement'"
                :id="`timeline-tab-${activeTab}-message-${message.type}-${message.id}`"
                :class="{
                  'img-blur': currentUser.inDemoMode && ['appointment', 'eForm', 'note'].includes(message.type),
                  'message-open pt-2': isExpanded(message)
                }"
              >
                <div :id="`${message.type}-${message.id}-message`" class="d-flex align-center w-100">
                  <div
                    v-if="!includes(['appointment', 'eForm', 'note'] , message.type)"
                    :id="`${message.type}-${message.id}-is-${isExpanded(message) ? 'open' : 'closed'}`"
                    :aria-controls="isExpanded(message) ? undefined : `timeline-tab-${activeTab}-message-${message.type}-${message.id}`"
                    :aria-expanded="isExpanded(message) ? undefined : false"
                    :class="{
                      'pb-4': isExpanded(message),
                      'cursor-pointer truncate-with-ellipsis': !isExpanded(message),
                      'timeline-message-full-width': isExpanded(message)
                    }"
                    :role="isExpanded(message) ? undefined : 'button'"
                    :tabindex="isExpanded(message) ? undefined : 0"
                    @click="onClickOpenMessage(message)"
                    @keyup.enter="onClickOpenMessage(message)"
                  >
                    <span :aria-hidden="true">
                      {{ isExpanded(message) ? message.message : getMessageSummary(message, true) }}
                    </span>
                    <span class="sr-only">{{ message.message }}</span>
                  </div>
                  <AdvisingNote
                    v-if="['eForm', 'note'].includes(message.type) && message.id !== editModeNoteId"
                    :after-saved="afterEditAdvisingNote"
                    :class="{'timeline-message-full-width': isExpanded(message)}"
                    :edit-note="editNote"
                    :is-open="isExpanded(message)"
                    :note="message"
                    :on-click-open="() => onClickOpenMessage(message)"
                  />
                  <EditAdvisingNote
                    v-if="['eForm', 'note'].includes(message.type) && message.id === editModeNoteId"
                    :after-cancel="afterNoteEditCancel"
                    :after-saved="afterEditAdvisingNote"
                    class="timeline-message-full-width pt-8"
                    initial-mode="editDraft"
                    :note-id="message.id"
                  />
                  <AdvisingAppointment
                    v-if="message.type === 'appointment'"
                    :appointment="message"
                    :class="{'timeline-message-full-width': isExpanded(message)}"
                    :is-open="isExpanded(message)"
                    :on-click-open="() => onClickOpenMessage(message)"
                    :student="student"
                  />
                </div>
              </div>
            </div>
          </div>
          <footer
            class="academic-timeline-column-date"
            :class="{
              'text-right': !(isExpanded(message) && ['appointment', 'eForm', 'note'].includes(message.type)),
              'pt-2': isExpanded(message)
            }"
          >
            <v-btn
              v-if="!editModeNoteId && isEditable(message) && canUserEditNote(message, currentUser)"
              :id="`edit-note-${message.id}-button`"
              :aria-label="`Edit ${getButtonAriaLabel(message)}`"
              class="mb-2"
              :class="{'sr-only': !isExpanded(message)}"
              color="primary"
              density="compact"
              :disabled="noteStore.disableNewNoteButton"
              slim
              :text="`Edit ${message.isDraft ? 'Draft' : 'Note'}`"
              variant="text"
              @click.stop="editNote(message)"
            />
            <v-btn
              v-if="!editModeNoteId && isEditable(message) && userCanDelete(message)"
              :id="`delete-note-button-${message.id}`"
              :aria-label="`Delete ${getButtonAriaLabel(message)}`"
              class="my-2"
              :class="{'sr-only': !isExpanded(message)}"
              color="primary"
              density="compact"
              :disabled="noteStore.disableNewNoteButton"
              slim
              :text="`Delete ${message.isDraft ? 'Draft' : 'Note'}`"
              variant="text"
              @click.stop="onClickDeleteNote(message)"
            />
            <div
              v-if="(message.type === 'note' && message.author) || (message.type === 'appointment' && message.advisor)"
              class="pb-1 pl-2"
              :class="{'sr-only': !isExpanded(message)}"
            >
              <span v-if="message.type === 'note'" class="font-size-14 text-medium-emphasis">Created by:</span>
              <AuthorDetails
                activator-class="font-size-14 pl-2"
                :author="message.author || message.advisor"
                :id-prefix="`note-${message.id}`"
                :peer-advising-department-id="message.peerAdvisingDepartmentId"
              />
            </div>
            <div
              :id="`timeline-tab-${activeTab}-date-${index}`"
              class="text-no-wrap py-2 pl-2"
            >
              <TimelineDate
                v-if="!isExpanded(message) || !includes(['appointment', 'eForm', 'note'], message.type)"
                :id="`collapsed-${message.type}-${message.id}-created-at`"
                :aria-hidden="includes(['appointment', 'eForm', 'note'], message.type)"
                :date="message.startsAt || message.setDate || message.updatedAt || message.createdAt"
                :include-time-of-day="false"
                :sr-prefix="message.type === 'appointment' ? 'Appointment date' : 'Last updated on'"
              />
              <div
                v-if="['appointment', 'eForm', 'note'].includes(message.type)"
                :class="{'sr-only': !isExpanded(message)}"
              >
                <div v-if="message.createdAt" :class="{'pb-2': !displayUpdatedAt(message)}">
                  <div :aria-hidden="true" class="text-medium-emphasis font-size-14">{{ message.type === 'appointment' ? 'Appt Date' : 'Created' }}:</div>
                  <TimelineDate
                    :id="`expanded-${message.type}-${message.id}-created-at`"
                    :date="message.startsAt || message.createdAt"
                    :sr-prefix="message.type === 'appointment' ? 'Appointment date' : 'Created on'"
                    :include-time-of-day="(message.createdAt.length > 10) && (message.type !== 'appointment')"
                  />
                  <div
                    v-if="['Calendly', 'YCBM'].includes(message.createdBy) && message.endsAt"
                    :id="`expanded-${message.type}-${message.id}-appt-time-range`"
                  >
                    <span :aria-hidden="true">{{ getSameDayDate(message).visual }}</span>
                    <span class="sr-only">{{ getSameDayDate(message).screenReader }}</span>
                  </div>
                </div>
                <div v-if="displayUpdatedAt(message)">
                  <div :aria-hidden="true" class="pt-2 text-medium-emphasis font-size-14">Updated:</div>
                  <TimelineDate
                    :id="`expanded-${message.type}-${message.id}-updated-at`"
                    :date="message.updatedAt"
                    :include-time-of-day="message.updatedAt.length > 10"
                    class="mb-2"
                    sr-prefix="Last updated on"
                  />
                </div>
                <div v-if="message.setDate">
                  <div class="pt-2 text-medium-emphasis font-size-14">Set Date:</div>
                  <TimelineDate
                    :id="`expanded-${message.type}-${message.id}-set-date`"
                    :date="message.setDate"
                    class="mb-2"
                  />
                </div>
                <span v-if="!message.updatedAt && !message.createdAt" class="sr-only">No last-updated date</span>
                <router-link
                  v-if="['eForm', 'note'].includes(message.type) && message.id !== editModeNoteId"
                  :id="`advising-${message.type}-permalink-${message.id}`"
                  class="d-inline-block mt-2"
                  :to="`#timeline-${message.type}-${message.id}`"
                  @click.prevent="scrollToPermalink(message)"
                >
                  Permalink <span class="sr-only">{{ getButtonAriaLabel(message) }}</span><v-icon :icon="mdiLinkVariant" />
                </router-link>
              </div>
            </div>
          </footer>
        </div>
        <AdvisingNoteComments
          v-if="commentsEnabled(message)"
          class="pb-3 px-6"
          :class="{'sr-only': !isExpanded(message)}"
          :note="message"
        />
      </article>
    </div>
    <div v-if="offerShowAll" class="text-center mb-4 mt-2">
      <v-btn
        :id="`timeline-tab-${activeTab}-previous-messages`"
        aria-controls="timeline-messages"
        :aria-expanded="isShowingAll"
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
      Are you sure you want to delete the note
      <span v-if="get(messageForDelete, 'subject')">
        with subject "<span class="font-weight-bold text-medium-emphasis">{{ messageForDelete.subject }}</span>"?
      </span>
      <span v-if="messageForDelete && !get(messageForDelete, 'subject')">
        containing text "<span class="font-weight-bold text-medium-emphasis">{{ truncate(stripHtmlAndTrim(messageForDelete.body), {length: 30}) }}</span>"?</span>
    </AreYouSureModal>
  </div>
</template>

<script setup>
import {capitalize, each, filter, find, findIndex, get, includes, map, pull, remove, size, slice, trim, truncate} from 'lodash'
import {computed, nextTick, onMounted, onUnmounted, ref, watch} from 'vue'
import {DateTime} from 'luxon'
import {
  mdiCheckBold,
  mdiClockOutline,
  mdiCloseCircle,
  mdiExclamationThick,
  mdiLinkVariant,
  mdiMenuDown,
  mdiMenuRight,
  mdiMenuUp
} from '@mdi/js'
import AcademicTimelineCategory from '@/components/student/profile/academic-timeline/AcademicTimelineCategory.vue'
import AdvisingAppointment from '@/components/appointment/AdvisingAppointment'
import AdvisingNote from '@/components/note/AdvisingNote'
import AdvisingNoteComments from '@/components/note/comment/AdvisingNoteComments'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import AuthorDetails from '@/components/note/AuthorDetails'
import EditAdvisingNote from '@/components/note/EditAdvisingNote'
import TimelineDate from '@/components/student/profile/TimelineDate'
import {alertScreenReader, decodeStudentUriAnchor, pluralize, putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {canUserEditNote, summarizeNoteForAcademicTimeline as getMessageSummary} from '@/lib/note'
import {deleteNote, getNote, markNoteRead} from '@/api/notes'
import {dismissStudentAlert} from '@/api/student'
import {isDirector} from '@/lib/boa-user'
import {markAppointmentRead} from '@/api/appointments'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session/index'
import {getUserDepartmentsWithRoles} from '@/lib/berkeley-department'

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
  onNoteUpdated: {
    required: true,
    type: Function
  },
  student: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()
const noteStore = useNoteStore()

const allExpanded = ref(false)
const config = contextStore.config
const creatingNoteEvent = ref(undefined)
const currentUser = contextStore.currentUser
const defaultShowPerTab = ref(5)
const editModeNoteId = ref(undefined)
const eventHandlers = ref(undefined)
const filterWithinTheTab = ref('all')
const isShowingAll = ref(false)
const messageForDelete = ref(undefined)
const openMessages = ref([])
const searchIndex = ref(undefined)
const searchResults = ref(undefined)
const timelineQuery = ref('')

const activeTab = computed(() => props.selectedFilter || 'all')
const isExpandAllAvailable = computed(() => ['appointment', 'eForm', 'note'].includes(props.selectedFilter))
const messagesVisible = computed(() => {
  return (searchResults.value || (isShowingAll.value ? messagesPerType(props.selectedFilter) : slice(messagesPerType(props.selectedFilter), 0, defaultShowPerTab.value)))
})
const offerShowAll = computed(() => !searchResults.value && messagesVisible.value.length && (props.countPerActiveTab > defaultShowPerTab.value))
const showDeleteConfirmModal = computed(() => !!messageForDelete.value)
const showDownloadNotesLink = computed(() => {
  const hasNonDrafts = () => {
    const notes = messagesPerType('note')
    return find(notes, n => !n.isDraft)
  }
  return props.selectedFilter === 'note'
    && (currentUser.isAdmin || isDirector(currentUser))
    && hasNonDrafts()
})

watch(() => props.selectedFilter, () => {
  allExpanded.value = false
  filterWithinTheTab.value = 'all'
  openMessages.value = []
  searchResults.value = null
  timelineQuery.value = ''
  refreshSearchIndex()
})

watch(timelineQuery, () => {
  if (timelineQuery.value) {
    const query = normalizeForSearchIndex(timelineQuery.value)
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

onMounted(() => {
  refreshSearchIndex()
  if (currentUser.canAccessAdvisingData) {
    eventHandlers.value = {
      'note-creation-is-starting': onNoteCreateStartEvent,
      'note-created': afterNoteCreated,
      'note-updated': note => props.onNoteUpdated(note).then(refreshSearchIndex),
      'notes-created': noteIdsBySid => {
        const noteId = noteIdsBySid[props.student.sid]
        if (noteId) {
          getNote(noteId).then(afterNoteCreated)
          refreshSearchIndex()
        }
      }
    }
    each(eventHandlers.value, (handler, eventType) => {
      contextStore.setEventHandler(eventType, handler)
    })
  }
  const permalink = decodeStudentUriAnchor()
  if (permalink) {
    const obj = find(props.messages, function(m) {
      // Legacy advising notes have string IDs; BOA-created advising notes have integer IDs.
      if (m.id && m.id.toString() === permalink.messageId && m.type.toLowerCase() === permalink.messageType) {
        return true
      }
    })
    if (obj) {
      isShowingAll.value = true
      nextTick(() => {
        scrollToPermalink(obj)
      })
    }
  }
})

onUnmounted(() => {
  each(eventHandlers.value || {}, (handler, eventType) => {
    contextStore.removeEventHandler(eventType, handler)
  })
})

const afterEditAdvisingNote = (updatedNote, putFocusId) => {
  editModeNoteId.value = null
  putFocusNextTick(putFocusId || `edit-note-${updatedNote.id}-button`)
}

const afterNoteCreated = note => {
  creatingNoteEvent.value = null
  props.onNoteUpdated(note).then(refreshSearchIndex)
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

const close = message => {
  if (editModeNoteId.value) {
    return false
  }
  if (isExpanded(message)) {
    pull(openMessages.value, message.transientId)
  }
  if (openMessages.value.length === 0) {
    allExpanded.value = false
  }
}

const commentsEnabled = message => {
  return (!message.legacySource && includes(['appointment', 'note'], message.type)) || message.type === 'eForm'
}

const deleteConfirmed = () => {
  const transientId = messageForDelete.value.transientId
  const predicate = ['transientId', transientId]
  const indexOfNote = findIndex(messagesVisible.value, predicate)
  const note = messagesVisible.value[indexOfNote]
  remove(props.messages, predicate)
  remove(openMessages.value, value => transientId === value)
  messageForDelete.value = undefined
  deleteNote(note.id).then(() => {
    if (size(messagesVisible.value)) {
      const nextFocusMessage = indexOfNote < size(messagesVisible.value) ? messagesVisible.value[indexOfNote] : messagesVisible.value[indexOfNote - 1]
      putFocusNextTick(isExpanded(nextFocusMessage) ? `${activeTab.value}-close-message-${nextFocusMessage.id}` : `timeline-${nextFocusMessage.type}-${nextFocusMessage.id}`)
    } else {
      putFocusNextTick('new-note-button')
    }
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

const getButtonAriaLabel = message => {
  const messageType = `${message.isDraft ? 'draft ' : ''}${isCancelledAppointment(message) ? 'cancelled ' : ''}${'eForm' === message.type ? '' : message.type}`
  return `${messageType} ${truncate(getMessageSummary(message, true), {length: 100, separator: '.'})}`
}

const getSameDayDate = message => {
  const format = 'h:mma'
  const startTime = formatDate(message.startsAt || message.createdAt, format)
  const endTime = formatDate(message.endsAt, format)
  return {
    visual: `${startTime} - ${endTime}`,
    screenReader: `${startTime} to ${endTime}`
  }
}

const isCancelledAppointment = message => {
  return (message.type === 'appointment' && ['Calendly', 'YCBM'].includes(message.createdBy) && message.status === 'cancelled')
}

const isEditable = message => {
  return message.type === 'note' && !message.legacySource
}

const isExpanded = message => {
  return includes(openMessages.value, message.transientId)
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
  let messages
  if (!type) {
    // Show ALL items: appointments, eForms, notes, etc.
    messages = props.messages
  } else if (['appointment', 'note'].includes(props.selectedFilter)) {
    if (filterWithinTheTab.value === 'mine') {
      // Show appointments or notes authored by the current-user.
      messages = filter(props.messages, m => {
        const author = m.author || m.advisor
        return m.type === type && get(author, 'uid') === currentUser.uid
      })
    } else if (filterWithinTheTab.value === 'department') {
      // Show notes authored by the department(s) of current-user.
      const myDeptCodes = map(currentUser.departments.concat(currentUser.calNetDepartments), 'deptCode')
      messages = filter(props.messages, m => {
        const deptCodes = map(get(m.author || m.advisor, 'departments') || [], 'deptCode')
        return m.type === type && deptCodes.filter(x => myDeptCodes.includes(x)).length
      })
    } else {
      // Show ALL items of the active tab.
      messages = filter(props.messages, ['type', type])
    }
  } else {
    // Show ALL items of the active tab.
    messages = filter(props.messages, ['type', type])
  }
  return messages
}

const normalizeForSearchIndex = value => trim(value).replace(/\s+/g, ' ').toLowerCase()

const onClickDeleteNote = message => {
  // The following opens the "Are you sure?" modal
  messageForDelete.value = message
}

const onClickCloseMessage = (message) => {
  if (!isExpanded(message)) {
    return false
  }
  close(message)
  putFocusNextTick(`${message.type}-${message.id}-is-closed`, {scroll: false})
}

const onClickOpenMessage = message => {
  if (isExpanded(message)) {
    return false
  }
  open(message)
  putFocusNextTick(`${activeTab.value}-close-message-${message.id}`, {scroll: false})
}

const onNoteCreateStartEvent = event => {
  if (includes(event.completeSidSet, props.student.sid)) {
    creatingNoteEvent.value = event
  }
}

const open = message => {
  if ((['eForm', 'note'].includes(message.type) && message.id === editModeNoteId.value)) {
    return false
  }
  if (!isExpanded(message)) {
    openMessages.value.push(message.transientId)
  }
  markRead(message)
  if (isExpandAllAvailable.value && openMessages.value.length === messagesPerType(props.selectedFilter).length) {
    allExpanded.value = true
  }
}

const refreshSearchIndex = () => {
  searchIndex.value = []
  const messages = ['appointment', 'eForm', 'note'].includes(props.selectedFilter) ? messagesPerType(props.selectedFilter) : []
  each(messages, m => {
    const advisor = m.author || m.advisor
    let idx = [
      advisor.name,
      (map(advisor.departments || [], 'deptName')).join(),
      advisor.email,
      m.body,
      m.category,
      m.createdBy,
      m.legacySource,
      m.message,
      m.subcategory,
      m.subject,
      (m.topics || []).join()
    ]
    if (m.eForm) {
      const e = m.eForm
      idx = idx.concat([
        e.action,
        e.courseName,
        e.courseTitle,
        e.gradingBasis,
        e.id,
        e.requestedGradingBasis,
        e.section,
        e.sectionId,
        e.status,
        e.term
      ])
    }
    if (m.type === 'appointment') {
      idx = idx.concat([
        m.cancelReason,
        m.status
      ])
    }
    if (m.createdBy === 'Calendly') {
      idx = idx.concat([m.appointmentTitle])
    }
    if (m.type === 'note' && size(m.comments)) {
      each(m.comments, c => {
        const commentAuthor = c.author || {}
        idx = idx.concat([
          c.body,
          c.subject,
          commentAuthor.name,
          (map(commentAuthor.departments || [], 'deptName')).join(),
          commentAuthor.email,
          c.createdBy,
          c.message
        ])
      })
    }
    searchIndex.value.push({idx: normalizeForSearchIndex(idx.join()), message: m})
  })
}

const scrollToPermalink = message => {
  isShowingAll.value = true
  open(message)
  putFocusNextTick(`timeline-${message.type}-${message.id}`, {scrollBlock: 'start'})
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

const userCanDelete = message => {
  let canDelete = false
  if (isEditable(message)) {
    canDelete = currentUser.isAdmin || (message.isDraft && message.author.uid === currentUser.uid)
    if (!canDelete && message.peerAdvisingDepartmentId) {
      const departments = getUserDepartmentsWithRoles(currentUser, ['peer_advisor_manager'])
      each(departments, department => {
        // Peer Advisor Manager can delete note if author is a Peer Advisor in the same Peer Advising department.
        const membership = find(department.memberships, ['role', 'peer_advisor_manager'])
        canDelete = membership.peerAdvisingDepartmentId === message.peerAdvisingDepartmentId
        // Break out of loop if canDelete is true.
        return !canDelete
      })
    }
  }
  return canDelete
}
</script>

<style>
.academic-timeline-column-date {
  min-width: 8rem;
  padding-right: 12px;
  width: 8rem;
}
.academic-timeline-search-input input {
  max-height: 30px !important;
  min-height: 30px !important;
  padding: 0 10px;
}
.message-row ul, .message-row ul {
  padding-left: 25px;
}
.message-row.expanded .academic-timeline-column-date {
  min-width: 12rem;
  width: 12rem;
}
</style>

<style scoped>
.academic-timeline-search-input {
  width: 12.5rem;
}
.btn-toggle-showing-subset {
  height: 32px;
}
.column-message {
  align-content: center;
  min-width: 12.5rem;
  width: calc(100% - 17rem);
}
.column-pill {
  min-width: 8.75rem;
  padding: 0 8px;
  white-space: nowrap;
  width: 8.75rem;
}
.message-open {
  flex-flow: row wrap;
  display: flex;
  min-height: 3.5rem;
  scroll-margin-top: 110px !important;
}
.message-row.expanded .column-message {
  align-content: start;
}
.message-row:active, .message-row:focus, .message-row:focus-within, .message-row:hover {
  background-color: rgb(var(--v-theme-sky-blue));
}
.message-row-read {
  background-color: rgb(var(--v-theme-light-grey));
}
.requirements-icon {
  padding: 0 4px 0 0;
  width: 20px;
}
.timeline-message-full-width {
  margin: 0 -8.75rem;
  padding: 0 24px;
  width: calc(100% + 8.75rem) !important;
  &.timeline-requirement {
    width: calc(100% + 16rem) !important;
  }
}
.toggle-expand-all-container {
  width: 7.75rem;
}
</style>
