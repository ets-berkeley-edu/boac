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
          <div class="d-flex align-center border-b-md flex-wrap pb-1">
            <MessageFilters v-model="filtersApplied" />
            <span :aria-hidden="true" class="text-disabled mx-1">|</span>
            <v-btn
              id="toggle-archive-btn"
              class="opacity-100"
              color="primary"
              density="compact"
              slim
              variant="plain"
              @click="onToggleArchive"
            >
              {{ `${showingArchive ? 'Hide' : 'Show'} Archive` }}
            </v-btn>
            <span :aria-hidden="true" class="text-disabled mx-1">|</span>
            <span
              v-if="!showingArchive"
              id="notifications-unread-count"
              class="pl-3"
              :class="{'font-weight-bold': currentUser.myUnreadMessageCount}"
            >
              {{ currentUser.myUnreadMessageCount }} New
            </span>
            <span
              v-if="showingArchive"
              id="notifications-archived-count"
              class="font-weight-bold pl-3"
            >
              {{ pluralize('Msg', size(archivedNotifications)) }}.
            </span>
          </div>
          <v-progress-linear
            v-if="isLoading"
            color="primary"
            height="2"
            indeterminate
            size="x-small"
          />
          <p
            v-if="!isLoading && size(notifications) && !size(filteredNotifications)"
            id="no-messages-match-filters"
            class="py-2 text-medium-emphasis"
          >
            No messages match the selected filters.
          </p>
          <ul v-if="!isLoading && size(filteredNotifications)">
            <li
              v-for="notification in filteredNotifications"
              :key="notification.id"
              class="border-b-sm list-no-bullets"
              :class="{'bg-pale-blue': get(selectedNotification, 'id') === notification.id}"
            >
              <div class="d-flex align-start justify-space-between py-2">
                <button
                  :id="`${notification.objectType}-${notification.id}-select-btn`"
                  :aria-current="get(selectedNotification, 'id') === notification ? 'true' : undefined"
                  class="d-block message-select-btn px-1 px-lg-2"
                  type="button"
                  @click="() => showDetail(notification)"
                >
                  <div class="d-flex align-baseline justify-space-between">
                    <div :id="`${notification.objectType}-${notification.id}-tag-created-by`" class="font-weight-bold mr-1 text-truncate">
                      {{ authorName(notification) }}
                    </div>
                    <div :id="`${notification.objectType}-${notification.id}-tag-created-at`">{{ dateOrTime(notification.createdAt) }}</div>
                  </div>
                  <div class="d-flex align-center justify-space-between">
                    <AcademicTimelineCategory
                      class="mr-2"
                      id-prefix="notifications"
                      :label="messageLabel(notification.object)"
                      :message="notification.object"
                    />
                    <span
                      v-if="get(notification.object, 'student')"
                      :id="`${notification.objectType}-${notification.id}-student`"
                      class="d-block text-medium-emphasis text-truncate"
                    >
                      {{ notification.object.student.name }} ({{ notification.object.student.sid }})
                    </span>
                  </div>
                  <div :id="`${notification.objectType}-${notification.id}-subject`" class="d-block font-weight-bold">
                    {{ messageTitle(notification.object) }}
                  </div>
                  <div :id="`${notification.objectType}-${notification.id}-body`" class="w-100">
                    <div
                      class="line-clamp-2"
                      v-html="stripHtmlAndSummarize(get(taggedItem(notification), 'body') || '')"
                    />
                  </div>
                </button>
                <div class="px-2 context-menu-btn">
                  <v-menu eager>
                    <template #activator="{ props }">
                      <v-btn
                        :id="`${notification.objectType}-${notification.id}-context-menu-btn`"
                        height="1.5rem"
                        width="1.5rem"
                        :icon="mdiDotsHorizontalCircleOutline"
                        variant="plain"
                        v-bind="props"
                      />
                    </template>
                    <v-list
                      color="primary"
                      density="compact"
                      item-props
                      :items="getAllowedActions(notification)"
                      menu
                      @click:select="action => updateNotification(action, notification)"
                    />
                  </v-menu>
                </div>
              </div>
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
                :key="`${selectedMessage.type}-${selectedMessage.id}`"
                class="mr-2 mr-md-3"
                id-prefix="message-detail"
                :label="messageLabel(selectedMessage)"
                :message="selectedMessage"
              />
              <router-link
                v-if="get(selectedMessage, 'student')"
                id="link-to-timeline-message"
                class="d-inline-block"
                :to="`${studentRoutePath(selectedMessage.student.uid, currentUser.inDemoMode)}#${permalinkAnchor(selectedNotification)}`"
              >
                <v-icon class="account-icon mr-1" :icon="mdiAccountCircle" size="1.25rem" />
                <span :id="`student-name-${selectedMessage.type}-${selectedMessage.id}`">{{ selectedMessage.student.name }}</span>
              </router-link>
              <span v-if="get(selectedMessage, 'student.sid')" :id="`student-sid-${selectedMessage.type}-${selectedMessage.id}`">
                &ThickSpace;({{ selectedMessage.student.sid }})
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
                :student="selectedMessage.student || {}"
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
import {filter, find, findIndex, get, includes, intersection, isEmpty, noop, orderBy, reject, size} from 'lodash'
import {mdiAccountCircle, mdiDotsHorizontalCircleOutline} from '@mdi/js'
import AcademicTimelineCategory from '@/components/student/profile/academic-timeline/AcademicTimelineCategory.vue'
import AdvisingAppointment from '@/components/appointment/AdvisingAppointment'
import AdvisingNote from '@/components/note/AdvisingNote'
import AdvisingComments from '@/components/comment/AdvisingComments'
import AuthorDetails from '@/components/note/AuthorDetails'
import MessageFilters from '@/components/notification/MessageFilters'
import TimelineDate from '@/components/student/profile/TimelineDate'
import {archiveUserTag, getArchivedUserTags, listUserTags, markUserTagRead, markUserTagUnread, unarchiveUserTag} from '@/api/user-tags.ts'
import {shouldDisplayUpdatedAt, stripHtmlAndSummarize, summarizeNoteForAcademicTimeline} from '@/lib/note.ts'
import {alertScreenReader, pluralize, putFocusNextTick, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser

const archivedNotifications = ref(undefined)
const filtersApplied = ref<string[]>(['all'])
const filteredNotifications = computed(() => {
  const visibleNotifications = showingArchive.value ? archivedNotifications.value : notifications.value
  return filter(visibleNotifications, matchesFilters)
})
const isLoading = ref(false)
const notifications = ref(undefined)
const selectedNotification = ref(undefined)
const selectedMessage = computed(() => get(selectedNotification.value, 'object'))
const selectedMessageAuthor = computed(() => get(selectedMessage.value, 'author') || get(selectedMessage.value, 'advisor'))
const showingArchive = ref(false)

const MESSAGE_TYPES = {
  appointment: {name: 'Appointment'},
  eForm: {name: 'eForm'},
  note: {name: 'Advising Note'}
}
const NOTIFICATION_ACTIONS = {
  archive: {execute: archiveUserTag, announcement: 'Message archived'},
  read: {execute: markUserTagRead, announcement: 'Message marked read'},
  unarchive: {execute: unarchiveUserTag, announcement: 'Message moved out of the archive'},
  unread: {execute: markUserTagUnread, announcement: 'Message marked unread'}
}
const TODAY = DateTime.now()

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

const authorName = message => {
  const item = taggedItem(message)
  return get(item, 'author.name') || get(item, 'advisor.name')
}

const commentsEnabled = message => {
  return includes(['appointment', 'eForm'], message.type) || (message.type === 'note' && !message.legacySource)
}

const dateOrTime = isoDate => {
  const localDate = DateTime.fromISO(isoDate).setZone(contextStore.config.timezone)
  let format
  if (localDate.hasSame(TODAY, 'day')) {
    format = 'h:mma'
  } else if (localDate.hasSame(TODAY, 'year')) {
    format = 'MMM d'
  } else {
    format = 'MMM d, yyyy'
  }
  return localDate.toFormat(format)
}

const getAllowedActions = notification => {
  return [
    notification.readByUser ? {title: 'Mark Unread', value: 'unread'} : {title: 'Mark Read', value: 'read'},
    notification.archivedByUser ? {title: 'Unarchive', value: 'unarchive'} : {title: 'Archive', value: 'archive'}
  ]
}

const matchesFilters = message => {
  if (includes(filtersApplied.value, 'all')) {
    return true
  }
  if (includes(filtersApplied.value, 'read') && !message.readByUser) {
    return false
  }
  if (includes(filtersApplied.value, 'unread') && message.readByUser) {
    return false
  }
  const typeFilters = intersection(filtersApplied.value, Object.keys(MESSAGE_TYPES))
  return isEmpty(typeFilters) || includes(typeFilters, message.object.type)
}

const messageLabel = message => {
  return message.type === 'note' && message.peerAdvisingDepartmentId ? 'Peer Note' : MESSAGE_TYPES[message.type].name
}

const messageTitle = message => {
  if (message.type === 'note') {
    return message.subject
  }
  if (message.type === 'appointment') {
    return message.appointmentTitle ? stripHtmlAndSummarize(message.appointmentTitle) : MESSAGE_TYPES.appointment.name
  }
  return summarizeNoteForAcademicTimeline(message, true)
}

const moveBetweenLists = notification => {
  // Archiving moves a notification from the inbox to the archive, and unarchiving moves it back.
  const index = findIndex(filteredNotifications.value, {id: notification.id})
  const [fromList, toList] = notification.archivedByUser ? [notifications, archivedNotifications] : [archivedNotifications, notifications]
  fromList.value = reject(fromList.value, {id: notification.id})
  if (toList.value) {
    toList.value = orderBy([...toList.value, notification], ['createdAt', 'id'], ['desc', 'desc'])
  }
  if (get(selectedNotification.value, 'id') === notification.id) {
    selectedNotification.value = undefined
  }
  const neighbor = filteredNotifications.value[index] || filteredNotifications.value[index - 1]
  putFocusNextTick(neighbor ? `${neighbor.objectType}-${neighbor.id}-select-btn` : 'toggle-archive-btn')
}

const onToggleArchive = () => {
  showingArchive.value = !showingArchive.value
  if (showingArchive.value && !archivedNotifications.value) {
    isLoading.value = true
    getArchivedUserTags().then(data => {
      archivedNotifications.value = data.archived
    }).finally(() => isLoading.value = false)
  }
}

const permalinkAnchor = notification => {
  // Matches the element ids on the student timeline: the message's row, or the comment's row inside it.
  const message = notification.object
  const messageAnchor = `timeline-${message.type}-${message.id}`
  const isTagInNote = notification.objectType === 'note' && notification.objectId === message.id
  return isTagInNote ? messageAnchor : `${messageAnchor}_comment-${notification.objectId}`
}

const refreshList = () => {
  isLoading.value = true
  return listUserTags().then(data => {
    notifications.value = filter(data.notifications, 'object')
  }).finally(() => isLoading.value = false)
}

const showDetail = notification => {
  selectedNotification.value = notification
  markUserTagRead(notification.id).then(data => {
    notification.readByUser = data.readByUser
    currentUser.myUnreadMessageCount = data.myUnreadMessageCount
  })
}

const taggedItem = notification => {
  // The note or comment that mentions the user.
  const message = notification.object
  if (notification.objectType === 'note' && notification.objectId === message.id) {
    return message
  }
  return find(message.comments, {id: notification.objectId}) || message
}

const updateNotification = (actionOption, notification) => {
  if (actionOption.value) {
    const action = NOTIFICATION_ACTIONS[actionOption.id]
    if (action && action.execute) {
      action.execute(notification.id).then(data => {
        const previouslyArchived = notification.archivedByUser
        notification.archivedByUser = data.archivedByUser
        notification.readByUser = data.readByUser
        currentUser.myUnreadMessageCount = data.myUnreadMessageCount
        if (previouslyArchived !== data.archivedByUser) {
          moveBetweenLists(notification)
        }
        alertScreenReader(action.announcement)
      })
    }
  }
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
  width: calc(100% - 2.5rem);
}
.message-title {
  min-height: 2.25rem;
}
</style>

<style>
.context-menu-btn {
  margin-top: -0.125rem
}
/* Truncate to two lines with an ellipsis. */
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
