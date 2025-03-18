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
          <th class="border-b-md th-created-date">
            <div class="float-right pr-2">Date Created</div>
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
              v-if="note.studentName"
              :id="`note-student-${note.studentSid}`"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
            >
              <router-link
                v-if="currentUser.isAdmin"
                :id="`link-to-student-${note.studentSid}`"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
                :to="studentRoutePath(note.studentSid, currentUser.inDemoMode)"
              >
                <span v-html="lastNameFirst(note.studentName)" />
              </router-link>
              <div
                v-if="!currentUser.isAdmin"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
              >
                <span v-html="`${note.studentName}`" />
              </div>
            </div>
            <div
              v-if="!note.studentName"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
            >
              SID: {{ note.studentSid }}
            </div>
          </td>
          <td
            :id="`note-body-in-row-${index}`"
            :class="{'border-b-md': index === notes.length - 1}"
            class="td-note"
          >
            <v-expand-transition>
              <button
                v-if="!expandedNoteIds.includes(note.id)"
                :id="`open-peer-advising-${note.id}`"
                :aria-label="`Edit ${getStudentName(note)} note`"
                class="align-center d-flex justify-space-between text-primary w-100"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
                @click="() => toggleShowHide(note)"
              >
                <span class="truncate-with-ellipsis">{{ stripHtmlAndTrim(note.noteSnippet) }}</span>
              </button>
            </v-expand-transition>
            <v-expand-transition>
              <div v-if="expandedNoteIds.includes(note.id)">
                <div class="margins-of-hide-note-btn text-center w-100">
                  <v-btn
                    :id="`hide-note-${note.id}-details`"
                    :aria-expanded="true"
                    class="w-100"
                    color="primary"
                    density="compact"
                    :prepend-icon="mdiCloseCircle"
                    text="Close Message"
                    variant="text"
                    @click="toggleShowHide(note)"
                  />
                </div>
                <PeerAdvisingNoteDetails class="my-3" :note="note" />
              </div>
            </v-expand-transition>
          </td>
          <td
            :id="`note-created-date-in-row-${index}`"
            :class="{'border-b-md': index === notes.length - 1}"
            class="td-created-date"
          >
            <div class="float-right pr-2">
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
  </div>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import {mdiCloseCircle} from '@mdi/js'
import {ref} from 'vue'
import {size} from 'lodash'
import type {Note} from '@/lib/types'
import Pagination from '@/components/util/Pagination.vue'
import {lastNameFirst, stripHtmlAndTrim, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import PeerAdvisingNoteDetails from '@/components/peer/note/PeerAdvisingNoteDetails.vue'

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
    type: Array
  },
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  },
  totalNoteCount: {
    required: true,
    type: Number
  }
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const expandedNoteIds = ref<number[]>([])

const getStudentName = (note: Note) => note.student ? `${note.student.firstName} ${note.student.lastName}` : `SID: ${note.sid}`

const toggleShowHide = (note: Note) => {
  const index = expandedNoteIds.value.indexOf(note.id)
  if (index > -1) {
    expandedNoteIds.value.splice(index, 1)
  } else {
    expandedNoteIds.value.push(note.id)
  }
}
</script>

<style scoped>
.margins-of-hide-note-btn {
  margin-left: -15px;
}
.td-created-date {
  max-width: 120px !important;
  padding: 5px 0;
  text-wrap: nowrap;
  vertical-align: top;
  width: 120px !important;
}
.td-note {
  width: 600px !important;
  max-width: 600px !important;
  padding: 5px;
  vertical-align: top;
}
.td-student {
  font-weight: bold;
  max-width: 200px !important;
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
</style>
