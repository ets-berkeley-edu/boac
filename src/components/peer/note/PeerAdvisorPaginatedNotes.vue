<template>
  <div class="table-container">
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
            <div class="float-right pr-2">Date Created</div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(note, index) in notes"
          :id="`tr-peer-advisor-${note.id}`"
          :key="index"
          :class="expandedNoteIds.includes(note.id) ? 'bg-sky-blue' : (index % 2 === 0 ? '' : 'bg-surface-light')"
        >
          <td
            :class="{
              'border-b-md': index === notes.length - 1,
              'pl-3 pt-3': smAndDown,
              'pl-2 pt-2': expandedNoteIds.includes(note.id)
            }"
            class="font-weight-bold text-medium-emphasis td-student"
          >
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
          <td
            :id="`td-note-${note.id}-body`"
            :class="{
              'border-b-md': index === notes.length - 1,
              'pl-3': smAndDown,
              'py-2': expandedNoteIds.includes(note.id)
            }"
            class="td-note"
            :colspan="expandedNoteIds.includes(note.id) ? 2 : 1"
          >
            <v-expand-transition>
              <div v-if="!expandedNoteIds.includes(note.id)">
                <button
                  :id="`open-peer-advising-${note.id}`"
                  :aria-label="`Edit ${getStudentName(note)} note`"
                  class="align-center d-flex text-primary w-100"
                  :class="{'demo-mode-blur': currentUser.inDemoMode}"
                  @click="() => toggleShowHide(note)"
                >
                  <span class="truncate-with-ellipsis" v-html="stripHtmlAndTrim(note.body)" />
                  <span v-if="note.attachments.length" class="ml-2">
                    <span class="sr-only">Has attachment(s)</span>
                    <v-icon class="mb-1" :icon="mdiPaperclip" size="small" />
                  </span>
                </button>
              </div>
            </v-expand-transition>
            <v-expand-transition>
              <div v-if="expandedNoteIds.includes(note.id)">
                <div class="margins-of-hide-note-btn">
                  <v-btn
                    :id="`show-note-${note.id}-details`"
                    :aria-expanded="true"
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
            v-if="!expandedNoteIds.includes(note.id)"
            :id="`note-topics-in-row-${index}`"
            :class="{
              'border-b-md': index === notes.length - 1,
              'pl-3': smAndDown,
              'td-topics': !smAndDown
            }"
            :title="note.topics.join(', ')"
          >
            <div class="align-center d-flex font-weight-medium justify-space-between w-100">
              <span
                v-if="note.topics.length"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
                class="truncate-with-ellipsis"
              >
                {{ note.topics.join(', ') }}
              </span>
              <span v-if="!note.topics.length && !smAndDown" class="text-medium-emphasis">&mdash;</span>
            </div>
          </td>
          <td
            :id="`td-note-${note.id}-created-at`"
            :class="{
              'border-b-md': index === notes.length - 1,
              'demo-mode-blur': currentUser.inDemoMode,
              'pl-3': smAndDown,
              'pr-2 pt-2': expandedNoteIds.includes(note.id)
            }"
            class="td-created-date"
          >
            <div
              :class="{'pb-3': smAndDown, 'float-right': !smAndDown}"
              class="pr-2"
            >
              {{ DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_MED) }}
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="!size(notes)" id="peer-advisor-no-notes" class="align-center d-flex pt-3">
      <div>
        There currently are no student notes. Would you like to
      </div>
      <v-btn
        id="peer-advisor-create-note-link"
        class="font-size-15 px-1"
        color="anchor"
        variant="text"
        @click="onClickCreateNote"
      >
        make your first note<span class="text-black text-decoration-none">?</span>
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import {mdiCloseCircle, mdiPaperclip} from '@mdi/js'
import {ref} from 'vue'
import {size} from 'lodash'
import {useDisplay} from 'vuetify'
import type {Note} from '@/lib/types'
import {lastNameFirst, stripHtmlAndTrim, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import PeerAdvisingNoteDetails from '@/components/peer/note/PeerAdvisingNoteDetails.vue'

defineProps({
  notes: {
    required: true,
    type: Array
  },
  onClickCreateNote: {
    required: true,
    type: Function
  },
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  }
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const expandedNoteIds = ref<number[]>([])
const {smAndDown} = useDisplay()

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
@media (max-width: 773px) {
  .table-container {
    overflow: hidden; /* Prevent horizontal scrollbar */
  }
  table {
    border-collapse: collapse;
    display: block; /* Allow table to stack vertically */
    width: 100%;
  }
  thead {
    display: none;
  }
  th, td {
    display: block; /* Allow cells to stack vertically */
    width: 100%;
  }
  th {
    font-weight: bold; /* Make headers bold */
  }
}
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
  max-width: 230px !important;
  padding: 5px;
  vertical-align: top;
  width: 230px !important;
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
