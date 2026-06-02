<template>
  <div
    :id="`advising-note-search-result-${note.id}`"
    :class="{'demo-mode-blur': currentUser.inDemoMode}"
    class="mt-3"
  >
    <h3 class="advising-note-search-result-header">
      <router-link
        v-if="note.studentUid"
        :id="`link-to-student-${note.studentUid}`"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        :to="`${studentRoutePath(note.studentUid, currentUser.inDemoMode)}#${timelineAnchor}`"
        class="advising-note-search-result-header-link"
        v-html="note.studentName"
      />
      <span
        v-if="!note.studentUid"
        :id="`student-${note.studentSid}-has-no-uid`"
        class="font-weight-500"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        v-html="note.studentName"
      />
      ({{ note.studentSid }})
    </h3>
    <div>
      <div v-if="note.parentNoteId" class="font-size-14 font-weight-bold text-medium-emphasis mb-1">
        Comment on advising note
      </div>
      <div
        :id="`advising-note-search-result-snippet-${note.id}`"
        class="advising-note-search-result-snippet"
        v-html="note.noteSnippet"
      />
      <div
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        class="advising-note-search-result-footer font-size-15 font-weight-bold text-medium-emphasis"
      >
        <span v-if="note.advisorName" :id="`advising-note-search-result-advisor-${note.id}`">
          {{ note.advisorName }} -
        </span>
        <span v-if="timestamp" :id="`advising-note-last-modified-${note.id}`">
          <Date :date="timestamp" :timezone="timezone" />
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import {get} from 'lodash'
import Date from '@/components/util/Date.vue'
import {studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  note: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const timestamp = get(props.note, 'updatedAt') || get(props.note, 'createdAt')
const timezone = contextStore.config.timezone

const timelineAnchor = computed(() => {
  if (props.note.parentNoteId) {
    return `timeline-note-${props.note.parentNoteId}_comment-${props.note.id}`
  }
  return `timeline-note-${props.note.id}`
})
</script>
