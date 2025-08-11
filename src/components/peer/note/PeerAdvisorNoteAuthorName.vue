<template>
  <div>
    <router-link
      v-if="currentUser.isAdmin || isPeerAdvisorManager(currentUser)"
      :id="`note-${note.id}-link-to-student`"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
      :to="studentRoutePath(student.uid, currentUser.inDemoMode)"
      v-html="studentName"
    />
    <div
      v-if="!currentUser.isAdmin && !isPeerAdvisorManager(currentUser)"
      class="text-medium-emphasis"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
      v-html="studentName"
    />
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import type {Note} from '@/lib/types'
import {isPeerAdvisorManager} from '@/lib/boa-user'
import {lastNameFirst, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  note: {
    required: true,
    type: Object as PropType<Note>
  },
  showStudentLastNameFirst: {
    required: false,
    type: Boolean
  }
})

const currentUser = useContextStore().currentUser
const student = props.note.student
const studentName = props.showStudentLastNameFirst ? lastNameFirst(student) : student ? `${student.firstName} ${student.lastName}` : `SID: ${props.note.sid}`
</script>

