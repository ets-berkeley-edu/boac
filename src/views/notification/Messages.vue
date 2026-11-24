<template>
  <v-container class="pa-6" fluid>
    <v-row class="mr-0">
      <v-col
        cols="12"
        lg="3"
        md="4"
        sm="5"
      >
        <section aria-labelledby="page-header">
          <h1 id="page-header">Messages</h1>
          <div class="d-flex align-center justify-space-between pb-1">
            <MessageFilters v-model="filtersApplied" />
            <span :aria-hidden="true" class="text-disabled">|</span>
            <span class="font-weight-bold pl-4">{{ size(unreadNotifications) }} new</span>
          </div>
          <p
            v-if="size(notifications) && !size(filteredNotifications)"
            id="no-messages-match-filters"
            class="border-t-md py-2 text-medium-emphasis"
          >
            No messages match the selected filters.
          </p>
          <ul v-else class="border-t-md">
            <li
              v-for="notification in filteredNotifications"
              :key="notification.id"
              class="border-b-sm list-no-bullets"
              :class="{'bg-pale-blue': get(selectedNotification, 'id') === notification.id}"
            >
              <button
                :id="`${notification.objectType}-${notification.id}-select-btn`"
                :aria-current="get(selectedNotification, 'id') === notification ? 'true' : undefined"
                class="d-block message-select-btn pa-1 my-2"
                type="button"
                @click="() => selectedNotification = notification"
              >
                <span class="d-flex align-baseline justify-space-between">
                  <span class="d-block font-weight-bold mr-1 text-truncate">{{ authorName(notification) }}</span>
                  <span class="d-block">{{ dateOrTime(notification.createdAt) }}</span>
                </span>
                <span class="d-flex align-center">
                  <AcademicTimelineCategory
                    class="mr-2"
                    :label="messageLabel(notification.object)"
                    :message="notification.object"
                  />
                  <span
                    v-if="get(notification.object, 'student')"
                    :id="`${notification.objectType}-${notification.id}-student`"
                    class="d-block text-medium-emphasis"
                  >
                    {{ notification.object.student.name }} ({{ notification.object.student.sid }})
                  </span>
                </span>
                <span :id="`${notification.objectType}-${notification.id}-subject`" class="d-block font-weight-bold">
                  {{ messageTitle(notification.object) }}
                </span>
                <div :id="`${notification.objectType}-${notification.id}-body`" class="w-100">
                  <div
                    class="line-clamp-2"
                    v-html="stripHtmlAndSummarize(get(taggedItem(notification), 'body') || '')"
                  />
                </div>
              </button>
            </li>
          </ul>
        </section>
      </v-col>
      <v-col
        cols="12"
        lg="9"
        md="8"
        sm="7"
      >
        <section id="message-detail" aria-labelledby="detail-header" class="message-detail pl-md-6">
          <h2 v-if="!selectedNotification" id="detail-header" class="font-weight-regular text-medium-emphasis">
            No messages {{ size(filteredNotifications) ? 'selected' : '' }}
          </h2>
          <div v-if="selectedMessage">
            <div class="message-title">
              <h2 id="detail-header">{{ messageTitle(selectedMessage) }}</h2>
            </div>
            <div class="d-flex align-center">
              <AcademicTimelineCategory
                class="mr-2 mr-md-3"
                :label="messageLabel(selectedMessage)"
                :message="selectedMessage"
              />
              <router-link
                v-if="get(selectedNotification, 'student')"
                :id="`link-to-${selectedMessage.type}-${selectedMessage.id}`"
                class="d-inline-block"
                :to="`${studentRoutePath(selectedNotification.student.uid, currentUser.inDemoMode)}#${permalinkAnchor(selectedNotification)}`"
              >
                <v-icon class="account-icon mr-1" :icon="mdiAccountCircle" size="1.25rem" />
                <span :id="`student-name-${selectedMessage.type}-${selectedMessage.id}`">{{ selectedNotification.student.name }}</span>
              </router-link>
              <span v-if="get(selectedNotification, 'student.sid')" :id="`student-sid-${selectedMessage.type}-${selectedMessage.id}`">
                &ThickSpace;({{ selectedNotification.student.sid }})
              </span>
            </div>
            <div class="d-flex">
              <AdvisingNote
                v-if="includes(['eForm', 'note'], selectedMessage.type)"
                :key="`message-${selectedMessage.type}-${selectedMessage.id}`"
                :is-open="true"
                :note="selectedMessage"
              />
              <AdvisingAppointment
                v-if="selectedMessage.type === 'appointment'"
                :key="`message-${selectedMessage.type}-${selectedMessage.id}`"
                :appointment="selectedMessage"
                :is-open="true"
                :on-click-open="noop"
                :student="selectedNotification.student || {}"
              />
              <footer
                class="pl-4 pl-md-6"
              >
                <div v-if="selectedMessageAuthor && 'eForm' !== selectedMessage.type" class="pb-2 pl-2">
                  <span v-if="'note' === selectedMessage.type" class="font-size-14 text-medium-emphasis">Created by:</span>
                  <AuthorDetails
                    :key="`author-${selectedMessage.type}-${selectedMessage.id}`"
                    activator-class="font-size-14"
                    :author="selectedMessageAuthor"
                    :id-prefix="`${selectedMessage.type}-${selectedMessage.id}`"
                    :peer-advising-department-id="selectedMessage.peerAdvisingDepartmentId"
                  />
                </div>
                <div
                  class="text-no-wrap pb-2 pl-2"
                >
                  <div>
                    <div v-if="selectedMessage.createdAt" :class="{'pb-2': !shouldDisplayUpdatedAt(selectedMessage)}">
                      <div :aria-hidden="true" class="text-medium-emphasis font-size-14">{{ selectedMessage.type === 'appointment' ? 'Appt Date' : 'Created' }}:</div>
                      <TimelineDate
                        :id="`expanded-${selectedMessage.type}-${selectedMessage.id}-created-at`"
                        :date="selectedMessage.startsAt || selectedMessage.createdAt"
                        :sr-prefix="selectedMessage.type === 'appointment' ? 'Appointment date' : 'Created on'"
                        :include-time-of-day="(selectedMessage.createdAt.length > 10) && (selectedMessage.type !== 'appointment')"
                      />
                    </div>
                    <div v-if="shouldDisplayUpdatedAt(selectedMessage)">
                      <div :aria-hidden="true" class="pt-2 text-medium-emphasis font-size-14">Updated:</div>
                      <TimelineDate
                        :id="`expanded-${selectedMessage.type}-${selectedMessage.id}-updated-at`"
                        :date="selectedMessage.updatedAt"
                        :include-time-of-day="selectedMessage.updatedAt.length > 10"
                        class="mb-2"
                        sr-prefix="Last updated on"
                      />
                    </div>
                    <div v-if="selectedMessage.setDate">
                      <div class="pt-2 text-medium-emphasis font-size-14">Set Date:</div>
                      <TimelineDate
                        :id="`expanded-${selectedMessage.type}-${selectedMessage.id}-set-date`"
                        :date="selectedMessage.setDate"
                        class="mb-2"
                      />
                    </div>
                    <span v-if="!selectedMessage.updatedAt && !selectedMessage.createdAt" class="sr-only">No last-updated date</span>
                  </div>
                </div>
              </footer>
            </div>
            <AdvisingComments v-if="commentsEnabled(selectedMessage)" class="pt-2" :parent="selectedMessage" />
          </div>
        </section>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import {computed, onMounted, ref, watch} from 'vue'
import {DateTime} from 'luxon'
import {filter, find, get, includes, intersection, isEmpty, noop, size} from 'lodash'
import {mdiAccountCircle} from '@mdi/js'
import AcademicTimelineCategory from '@/components/student/profile/academic-timeline/AcademicTimelineCategory.vue'
import AdvisingAppointment from '@/components/appointment/AdvisingAppointment'
import AdvisingNote from '@/components/note/AdvisingNote'
import AdvisingComments from '@/components/comment/AdvisingComments'
import AuthorDetails from '@/components/note/AuthorDetails'
import MessageFilters from '@/components/notification/MessageFilters'
import TimelineDate from '@/components/student/profile/TimelineDate'
import {listUserTags} from '@/api/user-tags.ts'
import {shouldDisplayUpdatedAt, stripHtmlAndSummarize, summarizeNoteForAcademicTimeline} from '@/lib/note.ts'
import {alertScreenReader, pluralize, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser

const filtersApplied = ref<string[]>(['all'])
const filteredNotifications = computed(() => filter(notifications.value, message => matchesFilters(message, filtersApplied.value)))
const notifications = ref(undefined)
const messageTypes = {
  appointment: {name: 'Appointment'},
  eForm: {name: 'eForm'},
  note: {name: 'Note'}
}
const selectedNotification = ref(undefined)
const selectedMessage = computed(() => get(selectedNotification.value, 'object'))
const selectedMessageAuthor = computed(() => get(selectedMessage.value, 'author') || get(selectedMessage.value, 'advisor'))
const today = DateTime.now()
const unreadNotifications = ref(undefined)

contextStore.loadingStart()

onMounted(() => {
  refreshList().then(() => {
    contextStore.setEventHandler('note-updated', refreshList)
    contextStore.loadingComplete()
  })
})

watch(filtersApplied, () => {
  if (selectedNotification.value && !includes(filteredNotifications.value, selectedNotification.value)) {
    selectedNotification.value = undefined
  }
  alertScreenReader(`Showing ${pluralize('message', size(filteredNotifications.value))}`)
})

const TYPE_FILTERS = ['note', 'appointment', 'eForm']

const matchesFilters = (message, filters: string[]) => {
  if (includes(filters, 'all')) {
    return true
  }
  if (includes(filters, 'read') && !message.readByUser) {
    return false
  }
  if (includes(filters, 'unread') && message.readByUser) {
    return false
  }
  const typeFilters = intersection(filters, TYPE_FILTERS)
  return isEmpty(typeFilters) || includes(typeFilters, message.object.type)
}

const taggedItem = notification => {
  // The note or comment that mentions the user.
  const message = notification.object
  if (notification.objectType === 'note' && notification.objectId === message.id) {
    return message
  }
  return find(message.comments, {id: notification.objectId}) || message
}

const authorName = message => {
  const item = taggedItem(message)
  return get(item, 'author.name') || get(item, 'advisor.name')
}

const messageLabel = message => {
  return message.type === 'note' && message.peerAdvisingDepartmentId ? 'Peer Note' : messageTypes[message.type].name
}

const messageTitle = message => {
  if (message.type === 'note') {
    return message.subject
  }
  if (message.type === 'appointment') {
    return message.appointmentTitle ? stripHtmlAndSummarize(message.appointmentTitle) : messageTypes.appointment.name
  }
  return summarizeNoteForAcademicTimeline(message, true)
}

const permalinkAnchor = notification => {
  // Matches the element ids on the student timeline: the message's row, or the comment's row inside it.
  const message = notification.object
  const messageAnchor = `timeline-${message.type}-${message.id}`
  const isTagInNote = notification.objectType === 'note' && notification.objectId === message.id
  return isTagInNote ? messageAnchor : `${messageAnchor}_comment-${notification.objectId}`
}

// Loch notes have no BOA comments. Same rule as the student timeline.
const commentsEnabled = message => {
  return includes(['appointment', 'eForm'], message.type) || (message.type === 'note' && !message.legacySource)
}

const dateOrTime = isoDate => {
  const localDate = DateTime.fromISO(isoDate).setZone(contextStore.config.timezone)
  let format
  if (localDate.hasSame(today, 'day')) {
    format = 'h:mma'
  } else if (localDate.hasSame(today, 'year')) {
    format = 'MMM d'
  } else {
    format = 'MMM d, yyyy'
  }
  return localDate.toFormat(format)
}

const refreshList = () => {
  return listUserTags().then(data => {
    notifications.value = filter(data.notifications, 'object')
    unreadNotifications.value = filter(notifications.value, {'readByUser': false})
  })
}
</script>

<style scoped>
.account-icon {
  margin-top: -2px;
}
.message-select-btn {
  color: inherit;
  font: inherit;
  letter-spacing: inherit;
  text-align: start;
  width: 100%;
}
.message-title {
  min-height: 2.25rem;
}
</style>

<style>
/* Truncate to two lines with an ellipsis. Vuetify's text-truncate only handles a single line. */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
  overflow-wrap: anywhere;
}
.message-detail .edit-note-comment {
  margin-left: -8px;
  width: 100% !important;
}
</style>
