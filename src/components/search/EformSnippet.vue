<template>
  <div
    :id="`eform-search-result-${result.id}`"
    :class="{'demo-mode-blur': currentUser.inDemoMode}"
    class="advising-note-search-result mt-3"
  >
    <h3 v-if="studentName.length" class="advising-note-search-result-header">
      <router-link
        v-if="result.student.uid"
        :id="`eform-link-to-student-${result.student.uid}`"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        :to="`${studentRoutePath(result.student.uid, currentUser.inDemoMode)}#timeline-eForm-${result.id}`"
        class="advising-note-search-result-header-link"
        v-html="studentName"
      />
      <span
        v-if="!result.student.uid"
        :id="`student-${result.student.sid}-has-no-uid`"
        class="font-weight-500"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        v-html="studentName"
      />
      ({{ result.student.sid }})
    </h3>
    <div v-if="!studentName.length">
      <h3 class="advising-note-search-result-header">
        <span aria-hidden="true">SID</span><span class="sr-only">S I D</span>
        {{ result.student.sid }}
      </h3>
      <div class="font-weight-500 text-medium-emphasis">
        No student record found.
      </div>
    </div>
    <div>
      <div
        :id="`eform-search-result-snippet-${result.id}`"
        class="advising-note-search-result-snippet"
        v-html="result.snippet"
      />
      <div
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        class="advising-note-search-result-footer font-size-15 font-weight-bold text-medium-emphasis"
      >
        <span v-if="createdAt" :id="`eform-created-at-date-${result.id}`">
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
  result: {
    required: true,
    type: Object
  }
})

const currentUser = useContextStore().currentUser
const timezone = useContextStore().config.timezone
const createdAt = get(props.result, 'createdAt')
const studentName = computed(() => trim(`${get(props.result, 'student.firstName', '')} ${get(props.result, 'student.lastName', '')}`))
</script>
