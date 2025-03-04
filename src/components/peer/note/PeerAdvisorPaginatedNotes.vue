<template>
  <div>
    <table
      v-if="!isEmpty(notes)"
      id="cohort-history-table"
      class="mt-5 w-100"
    >
      <thead>
        <tr>
          <th class="th-student">Student</th>
          <th class="th-note">Note</th>
          <th class="th-topics">Topics</th>
          <th class="th-created-date">Date Created</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(note, index) in notes"
          :key="index"
          :class="index % 2 === 0 ? 'white-row' : 'grey-row'"
        >
          <td class="td-student">
            <div
              v-if="note.student"
              :id="`note-student-${note.student.sid}`"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
            >
              <router-link
                v-if="currentUser.isAdmin"
                :id="`link-to-student-${note.sid}`"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
                :to="studentRoutePath(note.student.uid, currentUser.inDemoMode)"
              >
                <span v-html="lastNameFirst(note.student)" />
              </router-link>
              <div v-if="!currentUser.isAdmin">
                <span v-html="`${getStudentName(note)}`" />
              </div>
            </div>
            <div v-if="!note.student">
              SID: {{ note.sid }}
            </div>
          </td>
          <td :id="`note-body-in-row-${index}`" class="td-note truncate-with-ellipsis">
            <router-link
              v-if="currentUser.isAdmin"
              :id="`link-to-student-${note.student.uid}`"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
              :to="`${studentRoutePath(note.student.uid, currentUser.inDemoMode)}#permalink-note-${note.id}`"
            >
              <TruncatedButtonText :text="note.body" />
            </router-link>
            <v-btn
              v-if="isPeerAdvisor(currentUser)"
              :id="`open-peer-advising-${note.id}`"
              :aria-label="`Edit ${getStudentName(note)} note`"
              class="mr-1 px-0 py-2 text-left text-primary"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
              size="lg"
              variant="text"
              @click="() => openEditDialog(note)"
            >
              <TruncatedButtonText :text="note.body" />
            </v-btn>
          </td>
          <td :id="`note-topics-in-row-${index}`" class="td-topics">
            <div class="truncate-with-ellipsis">
              {{ note.topics.join(', ') }}
            </div>
          </td>
          <td :id="`note-created-date-in-row-${index}`" class="td-created-date">
            {{ DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_MED) }}
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="totalNoteCount > itemsPerPage" class="pa-3">
      <hr />
      <Pagination
        :click-handler="goToPage"
        id-prefix="auxiliary-pagination"
        :init-page-number="currentPage"
        :is-widget-at-bottom-of-page="true"
        :limit="10"
        :per-page="itemsPerPage"
        :total-rows="totalNoteCount"
      />
    </div>
    <div v-if="isEmpty(notes)" id="peer-advisor-no-notes" class="pt-3">
      This cohort has no history available.
    </div>
    <EditPeerAdvisingNoteModal
      v-model="isEditDialogOpen"
      :student="selectedStudent"
    />
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {DateTime} from 'luxon'
import {isEmpty} from 'lodash'
import {ref} from 'vue'
import type {BasicStudent, Note} from '@/lib/types'
import EditPeerAdvisingNoteModal from '@/components/peer/note/EditPeerAdvisingNoteModal.vue'
import Pagination from '@/components/util/Pagination.vue'
import TruncatedButtonText from '@/components/peer/note/TruncatedButtonText.vue'
import {isPeerAdvisor} from '@/lib/boa-user'
import {lastNameFirst, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

defineProps({
  currentPage: {
    required: true,
    type: Number
  },
  goToPage: {
    required: true,
    type: Function
  },
  itemsPerPage: {
    required: true,
    type: Number
  },
  notes: {
    required: true,
    type: Array as PropType<Note[]>
  },
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  },
  totalNoteCount: {
    required: true,
    type: Number
  },
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const isEditDialogOpen = ref(false)
const noteStore = useNoteStore()
const selectedStudent = ref<BasicStudent | undefined>()

const getStudentName = (note: Note) => {
  return note.student ? `${note.student.firstName} ${note.student.lastName}` : `SID: ${note.sid}`
}

const openEditDialog = (note: Note) => {
  selectedStudent.value = note.student
  noteStore.setMode('editPeerAdvisorNote')
  noteStore.setModel(note)
  noteStore.setCompleteSidSet([note.student.sid])
  noteStore.setIsCreateNoteModalOpen(true)
  isEditDialogOpen.value = true
}
</script>

<style scoped>
.td-created-date {
  float: right;
  max-width: 120px !important;
  padding: 5px;
  text-wrap: nowrap;
  vertical-align: top;
  width: 120px !important;
}
.td-note {
  max-width: 300px !important;
  padding: 5px;
  vertical-align: top;
}
.td-student {
  font-weight: bold;
  max-width: 200px !important;
  padding: 5px;
  vertical-align: top;
}
.td-topics {
  max-width: 100px !important;
  padding: 5px;
  vertical-align: top;
}
.th-created-date {
  float: right;
  padding: 5px;
  text-wrap: nowrap;
}
.th-note {
  padding: 5px;
}
.th-student {
  font-weight: bold;
}
.th-topics {
  padding: 5px;
}
</style>
