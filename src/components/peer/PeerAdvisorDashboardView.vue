<template>
  <PeerAdvisingNotesDashboard
    v-if="peerAdvisingDepartment"
    :fetch-notes="fetchNotes"
    heading-tag="h2"
    hide-create-note-button
    hide-department-name
    hide-my-notes-toggle
    inline-notes-count
    :peer-advising-department="peerAdvisingDepartment"
  />
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import type {Note, PeerAdvisingDepartment} from '@/lib/types'
import PeerAdvisingNotesDashboard from '@/components/peer/note/PeerAdvisingNotesDashboard.vue'
import {getPeerAdvisingDepartmentNotes} from '@/api/peer-advising-notes'

const props = defineProps({
  peerAdvisingDepartment: {
    required: true,
    type: Object as PropType<PeerAdvisingDepartment>
  }
})

const fetchNotes = (offset: number, limit: number): Promise<{notes: Note[], totalNoteCount: number}> => {
  return getPeerAdvisingDepartmentNotes(props.peerAdvisingDepartment.id, offset, limit, true)
}
</script>
