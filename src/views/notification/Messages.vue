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
          <div class="d-flex">
            <span class="font-weight-bold ml-auto">{{ size(unreadMessages) }} new</span>
          </div>
          <ul class="border-t-md">
            <li
              v-for="message in messages"
              :key="message.id"
              class="border-b-sm list-no-bullets mb-2 py-2"
            >
              <div
                :id="`${message.objectType}-${message.id}-select-btn`"
                role="button"
                @click="() => selectedMessage = message"
              >
                <div class="d-flex align-baseline justify-space-between">
                  <div class="font-weight-bold mr-1 text-truncate">{{ get(message, 'object.author.name') || get(message, 'object.authorName') }}</div>
                  <div>{{ dateOrTime(message.createdAt) }}</div>
                </div>
                <div class="d-flex align-center">
                  <AcademicTimelineCategory
                    class="mr-2"
                    :label="filterTypes[message.objectType].name"
                    :message="message"
                  />
                  <div
                    v-if="get(message, 'student')"
                    :id="`${message.objectType}-${message.id}-student`"
                    class="text-medium-emphasis"
                  >
                    {{ get(message, 'student.name') }} ({{ get(message, 'object.sid') }})
                  </div>
                </div>
                <div :id="`${message.objectType}-${message.id}-subject`" class="font-weight-bold">
                  {{ get(message, 'object.subject') }}
                </div>
                <div :id="`${message.objectType}-${message.id}-body`" class="overflow-x-hidden w-100">
                  <span
                    class="d-inline-block text-truncate text-wrap"
                    v-html="get(message, 'object.body')"
                  />
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
          <h2 v-if="!selectedMessage" id="detail-header" class="font-weight-regular text-medium-emphasis">
            No messages {{ size(messages) ? 'selected' : '' }}
          </h2>
          <div v-if="selectedMessage && 'note' === selectedMessage.objectType">
            <div class="message-title">
              <h2>{{ selectedMessage.object.subject }}</h2>
            </div>
            <div class="d-flex align-center">
              <AcademicTimelineCategory
                class="mr-2 mr-md-3"
                :label="filterTypes[selectedMessage.objectType].name"
                :message="selectedMessage"
              />
              <router-link
                v-if="get(selectedMessage, 'student')"
                :id="`link-to-${selectedMessage.objectType}-${selectedMessage.object.id}`"
                class="d-inline-block"
                :to="`${studentRoutePath(selectedMessage.student.uid, currentUser.inDemoMode)}#${timelineAnchor(selectedMessage.object)}`"
              >
                <v-icon class="account-icon mr-1" :icon="mdiAccountCircle" size="1.25rem" />
                <span :id="`student-name-${selectedMessage.objectType}-${selectedMessage.object.id}`">{{ get(selectedMessage, 'student.name') }}</span>
              </router-link>
              <span v-if="get(selectedMessage, 'student.sid')" :id="`student-sid-${selectedMessage.objectType}-${selectedMessage.object.id}`">
                &ThickSpace;({{ selectedMessage.student.sid }})
              </span>
            </div>
            <div class="d-flex">
              <AdvisingNote
                :key="`message-${selectedMessage.object.id}`"
                :is-open="true"
                :note="selectedMessage.object"
              />
              <footer
                class="pl-4 pl-md-6"
              >
                <div class="pb-1 pl-2">
                  <span v-if="'note' === selectedMessage.objectType" class="font-size-14 text-medium-emphasis">Created by:</span>
                  <AuthorDetails
                    :key="`author-${selectedMessage.object.id}`"
                    activator-class="font-size-14"
                    :author="selectedMessageAuthor"
                    :id-prefix="`note-${selectedMessage.object.id}`"
                    :peer-advising-department-id="selectedMessage.object.peerAdvisingDepartmentId"
                  />
                </div>
                <div
                  class="text-no-wrap py-2 pl-2"
                >
                  <div>
                    <div v-if="selectedMessage.object.createdAt" :class="{'pb-2': !shouldDisplayUpdatedAt(selectedMessage.object)}">
                      <div :aria-hidden="true" class="text-medium-emphasis font-size-14">{{ selectedMessage.objectType === 'appointment' ? 'Appt Date' : 'Created' }}:</div>
                      <TimelineDate
                        :id="`expanded-${selectedMessage.objectType}-${selectedMessage.object.id}-created-at`"
                        :date="selectedMessage.object.startsAt || selectedMessage.object.createdAt"
                        :sr-prefix="selectedMessage.objectType === 'appointment' ? 'Appointment date' : 'Created on'"
                        :include-time-of-day="(selectedMessage.object.createdAt.length > 10) && (selectedMessage.objectType !== 'appointment')"
                      />
                    </div>
                    <div v-if="shouldDisplayUpdatedAt(selectedMessage.object)">
                      <div :aria-hidden="true" class="pt-2 text-medium-emphasis font-size-14">Updated:</div>
                      <TimelineDate
                        :id="`expanded-${selectedMessage.objectType}-${selectedMessage.object.id}-updated-at`"
                        :date="selectedMessage.object.updatedAt"
                        :include-time-of-day="selectedMessage.object.updatedAt.length > 10"
                        class="mb-2"
                        sr-prefix="Last updated on"
                      />
                    </div>
                    <div v-if="selectedMessage.object.setDate">
                      <div class="pt-2 text-medium-emphasis font-size-14">Set Date:</div>
                      <TimelineDate
                        :id="`expanded-${selectedMessage.objectType}-${selectedMessage.object.id}-set-date`"
                        :date="selectedMessage.object.setDate"
                        class="mb-2"
                      />
                    </div>
                    <span v-if="!selectedMessage.object.updatedAt && !selectedMessage.object.createdAt" class="sr-only">No last-updated date</span>
                  </div>
                </div>
              </footer>
            </div>
            <AdvisingComments class="pt-2" :parent="selectedMessage.object" />
          </div>
        </section>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import {computed, onMounted, ref} from 'vue'
import {DateTime} from 'luxon'
import {filter, get, size} from 'lodash'
import {mdiAccountCircle} from '@mdi/js'
import AcademicTimelineCategory from '@/components/student/profile/academic-timeline/AcademicTimelineCategory.vue'
import AdvisingNote from '@/components/note/AdvisingNote'
import AdvisingComments from '@/components/comment/AdvisingComments'
import AuthorDetails from '@/components/note/AuthorDetails'
import TimelineDate from '@/components/student/profile/TimelineDate'
import {listUserTags} from '@/api/user-tag.ts'
import {shouldDisplayUpdatedAt, timelineAnchor} from '@/lib/note.ts'
import {studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser

const filterTypes = {
  comment: {name: 'Comment'},
  note: {name: 'Note'}
}
const messages = ref(undefined)
const selectedMessage = ref(undefined)
const selectedMessageAuthor = computed(() => {
  if (!get(selectedMessage.value, 'object')) {
    return null
  }
  return {
    name: selectedMessage.value.object.authorName,
    role: selectedMessage.value.object.authorRole,
  }
})
const today = DateTime.now()
const unreadMessages = ref(undefined)

contextStore.loadingStart()

onMounted(() => {
  listUserTags().then(data => {
    messages.value = data.notifications
    unreadMessages.value = filter(data.notifications, {'readByUser': false})
    contextStore.loadingComplete()
  })
})

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
</script>

<style scoped>
.account-icon {
  margin-top: -2px;
}
.message-title {
  min-height: 2.25rem;
}
</style>

<style>
.message-detail .edit-note-comment {
  margin-left: -8px;
  width: 100% !important;
}
</style>
