<template>
  <div>
    <table
      v-if="size(notes)"
      id="notes-for-peer-advisor-view"
      class="mt-5 w-100"
    >
      <thead>
        <tr>
          <th class="border-b-md th-student">Student</th>
          <th class="border-b-md th-note">Note</th>
          <th class="border-b-md th-topics">Topic(s)</th>
          <th class="border-b-md th-created-date">
            <div class="float-right">Date Created</div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(note, index) in notes"
          :key="index"
          :class="index % 2 === 0 ? '' : 'bg-surface-light'"
        >
          <td :class="{'border-b-md': index === notes.length - 1}" class="td-student">
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
          <td :id="`note-body-in-row-${index}`" :class="{'border-b-md': index === notes.length - 1}" class="td-note">
            <router-link
              v-if="currentUser.isAdmin"
              :id="`link-to-student-${note.student.uid}`"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
              class="align-center d-flex font-weight-medium justify-space-between w-100"
              :to="`${studentRoutePath(note.student.uid, currentUser.inDemoMode)}#permalink-note-${note.id}`"
            >
              <span class="truncate-with-ellipsis">{{ stripHtmlAndTrim(note.body) }}</span>
            </router-link>
            <button
              v-if="isPeerAdvisor(currentUser)"
              :id="`open-peer-advising-${note.id}`"
              :aria-label="`Edit ${getStudentName(note)} note`"
              class="align-center d-flex justify-space-between text-primary w-100"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
              @click="() => openEditDialog(note)"
            >
              <span class="truncate-with-ellipsis">{{ stripHtmlAndTrim(note.body) }}</span>
            </button>
          </td>
          <td
            :id="`note-topics-in-row-${index}`"
            :class="{'border-b-md': index === notes.length - 1}"
            class="td-topics"
            :title="note.topics.join(', ')"
          >
            <div class="align-center d-flex font-weight-medium justify-space-between w-100">
              <span v-if="note.topics.length" class="truncate-with-ellipsis">{{ note.topics.join(', ') }}</span>
              <span v-if="!note.topics.length" class="text-medium-emphasis">&mdash;</span>
            </div>
          </td>
          <td
            :id="`note-created-date-in-row-${index}`"
            :class="{'border-b-md': index === notes.length - 1}"
            class="td-created-date"
          >
            <div class="float-right">
              {{ DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_MED) }}
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="!size(notes)" id="peer-advisor-no-notes" class="pt-3">
      No notes found.
    </div>
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
    <EditPeerAdvisingNoteModal
      v-model="isEditDialogOpen"
      :student="selectedStudent"
      :peer-advising-department-id="peerAdvisingDepartmentId"
    />
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {DateTime} from 'luxon'
import {size} from 'lodash'
import {ref} from 'vue'
import type {BasicStudent, Note} from '@/lib/types'
import EditPeerAdvisingNoteModal from '@/components/peer/note/EditPeerAdvisingNoteModal.vue'
import Pagination from '@/components/util/Pagination.vue'
import {isPeerAdvisor} from '@/lib/boa-user'
import {lastNameFirst, stripHtmlAndTrim, studentRoutePath} from '@/lib/utils'
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

const getStudentName = (note: Note) => note.student ? `${note.student.firstName} ${note.student.lastName}` : `SID: ${note.sid}`

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
  max-width: 120px !important;
  padding: 5px 0;
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
  padding: 5px 0;
  text-wrap: nowrap;
}
.th-note {
  padding: 5px;
}
.th-student {
  font-weight: bold;
  padding: 0 5px;
}
.th-topics {
  padding: 5px;
}
</style>
