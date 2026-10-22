<template>
  <div
    :id="`appointment-search-result-${appointment.id}`"
    :class="{'demo-mode-blur': currentUser.inDemoMode}"
    class="advising-note-search-result mt-3"
  >
    <h3 v-if="studentName.length" class="advising-note-search-result-header">
      <router-link
        v-if="appointment.student.uid"
        :id="`appointment-link-to-student-${appointment.student.uid}`"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        :to="`${studentRoutePath(appointment.student.uid, currentUser.inDemoMode)}#timeline-appointment-${appointment.id}`"
        class="advising-note-search-result-header-link"
        v-html="studentName"
      />
      <span
        v-if="!appointment.student.uid"
        :id="`student-${appointment.student.sid}-has-no-uid`"
        class="font-weight-500"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        v-html="studentName"
      />
      ({{ appointment.student.sid }})
    </h3>
    <div v-if="!studentName.length">
      <h3 class="advising-note-search-result-header">
        <span aria-hidden="true">SID</span><span class="sr-only">S I D</span>
        {{ appointment.student.sid }}
      </h3>
      <div class="font-weight-500 text-medium-emphasis">
        No student record found.
      </div>
    </div>
    <div>
      <div
        :id="`appointment-search-result-snippet-${appointment.id}`"
        class="advising-note-search-result-snippet"
        v-html="appointment.detailsSnippet"
      />
      <div
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        class="advising-note-search-result-footer font-size-15 font-weight-bold text-medium-emphasis"
      >
        <span v-if="get(appointment, 'advisor.name')" :id="`appointment-search-result-advisor-${appointment.id}`">
          {{ appointment.advisor.name }} -
        </span>
        <span v-if="createdAt" :id="`appointment-created-at-date-${appointment.id}`">
          <Date :date="createdAt" :timezone="timezone" />
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import {get, trim} from 'lodash'
import Date from '@/components/util/Date.vue'
import {studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  appointment: {
    required: true,
    type: Object
  }
})
const currentUser = useContextStore().currentUser
const createdAt = get(props.appointment, 'createdAt')
const timezone = useContextStore().config.timezone
const studentName = computed(() => trim(`${get(props.appointment, 'student.firstName', '')} ${get(props.appointment, 'student.lastName', '')}`))
</script>
