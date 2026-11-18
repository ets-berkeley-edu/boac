<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" lg="3" md="4">
        <section aria-labelledby="page-header">
          <h1 id="page-header">Messages</h1>
          <ul class="border-t-md">
            <li
              v-for="message in notifications"
              :key="message.id"
              class="border-b-sm list-no-bullets mb-2 py-2"
            >
              <div class="d-flex align-baseline justify-space-between">
                <div class="font-weight-bold">{{ get(message, 'object.author.name') || get(message, 'object.authorName') }}</div>
                <TimelineDate
                  :date="message.createdAt"
                />
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
                  class="truncate-with-ellipsis"
                  v-html="get(message, 'object.body')"
                />
              </div>
            </li>
          </ul>
        </section>
      </v-col>
      <v-col cols="12" lg="9" md="8">
        <section id="message-detail" aria-labelledby="detail-header">
          <h2 id="detail-header" class="font-weight-regular text-medium-emphasis">No messages selected</h2>
        </section>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import {get} from 'lodash'
import {onMounted, ref} from 'vue'
import AcademicTimelineCategory from '@/components/student/profile/academic-timeline/AcademicTimelineCategory.vue'
import TimelineDate from '@/components/student/profile/TimelineDate'
import {listUserTags} from '@/api/user-tag.ts'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()

const filterTypes = {
  comment: {name: 'Comment'},
  note: {name: 'Note'}
}
const notifications = ref(undefined)

contextStore.loadingStart()

onMounted(() => {
  listUserTags().then(data => {
    notifications.value = data.notifications
    contextStore.loadingComplete()
  })
})
</script>
