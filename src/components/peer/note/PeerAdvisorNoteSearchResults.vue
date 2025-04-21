<template>
  <div class="table-container">
    <table
      v-if="size(notes)"
      id="notes-for-peer-advisor-view"
      class="mt-5 w-100"
    >
      <thead :class="{'sr-only': !smAndUp}">
        <tr>
          <th class="border-b-md th-student">Student</th>
          <th class="border-b-md th-note">Note</th>
          <th class="border-b-md th-created-date text-right">Date Created</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(note, index) in notes"
          :id="`tr-peer-advisor-note-${note.id}`"
          :key="index"
          :class="{
            'bg-sky-blue': expandedNoteIds.includes(note.id),
            'bg-surface-light': (index % 2 === 0),
            'border-b-md': !smAndUp && index === notes.length - 1
          }"
        >
          <td
            :id="`td-note-${note.id}-student`"
            :class="{'border-b-md': smAndUp && index === notes.length - 1}"
            class="td-student"
          >
            <router-link
              v-if="currentUser.isAdmin"
              :id="`note-${note.id}-link-to-student`"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
              :to="studentRoutePath(note.studentUid, currentUser.inDemoMode)"
            >
              {{ getStudentName(note) }}
            </router-link>
            <div v-if="!currentUser.isAdmin" :class="{'demo-mode-blur': currentUser.inDemoMode}">
              {{ getStudentName(note) }}
            </div>
          </td>
          <td
            :id="`td-note-${note.id}-body`"
            :class="{'border-b-md': smAndUp && index === notes.length - 1}"
            class="td-note"
          >
            <v-expand-transition>
              <div v-if="!expandedNoteIds.includes(note.id)">
                <button
                  :id="`open-peer-advising-${note.id}`"
                  :aria-expanded="false"
                  :aria-label="`Expand message ${getNoteLabel(note, index)}`"
                  class="toggle-note-btn align-center d-flex px-3 text-capitalize text-primary v-btn"
                  :class="{'demo-mode-blur': currentUser.inDemoMode}"
                  @click="() => toggleShowHide(note)"
                >
                  <span class="v-btn__overlay" />
                  <span class="truncate-with-ellipsis">{{ stripHtmlAndTrim(note.noteSnippet) }}</span>
                  <span v-if="note.attachmentCount > 0" class="ml-2">
                    <span class="sr-only">Has attachment(s)</span>
                    <v-icon class="mb-1" :icon="mdiPaperclip" size="small" />
                  </span>
                </button>
              </div>
            </v-expand-transition>
            <v-expand-transition>
              <div v-if="expandedNoteIds.includes(note.id)">
                <v-btn
                  :id="`show-note-${note.id}-details`"
                  :aria-expanded="true"
                  :aria-label="`Close message ${getNoteLabel(note, index)}`"
                  class="toggle-note-btn px-4"
                  color="primary"
                  :prepend-icon="mdiCloseCircle"
                  text="Close Message"
                  variant="text"
                  @click="toggleShowHide(note)"
                />
                <PeerAdvisingNoteDetails class="my-3" :note-id="note.id" />
              </div>
            </v-expand-transition>
          </td>
          <td
            :id="`td-note-${note.id}-created-at`"
            :class="{
              'border-b-md': smAndUp && index === notes.length - 1,
              'demo-mode-blur': currentUser.inDemoMode
            }"
            class="td-created-date text-right"
          >
            {{ DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_MED) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import {mdiCloseCircle, mdiPaperclip} from '@mdi/js'
import {ref} from 'vue'
import {size} from 'lodash'
import {useDisplay} from 'vuetify'
import type {NoteSearchResult} from '@/lib/types'
import {putFocusNextTick, stripHtmlAndTrim, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import PeerAdvisingNoteDetails from '@/components/peer/note/PeerAdvisingNoteDetails.vue'

const props = defineProps({
  notes: {
    required: true,
    type: Array<NoteSearchResult>
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
const {smAndUp} = useDisplay()

const getNoteLabel = (note: NoteSearchResult, index: number) => {
  return `${index + 1} of ${size(props.notes) || 'unknown'}, ${getStudentName(note)}, dated ${DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_FULL)}. ${stripHtmlAndTrim(note.noteSnippet)}`
}

const getStudentName = (note: NoteSearchResult) => note.studentName || `SID: ${note.studentSid}`

const toggleShowHide = (note: NoteSearchResult) => {
  const index = expandedNoteIds.value.indexOf(note.id)
  if (index > -1) {
    expandedNoteIds.value.splice(index, 1)
    putFocusNextTick(`open-peer-advising-${note.id}`)
  } else {
    expandedNoteIds.value.push(note.id)
    putFocusNextTick(`show-note-${note.id}-details`)
  }
}
</script>

<style scoped>
@media (max-width: 599px) {
  .table-container {
    min-width: 300px;
    overflow: hidden; /* Prevent horizontal scrollbar */
  }
  table, tbody, tr {
    border-collapse: collapse;
    display: block; /* Allow table to stack vertically */
  }
  td {
    display: block; /* Allow cells to stack vertically */
    max-width: unset !important;
    padding: 2px 20px !important;
    width: 100% !important;
  }
  td.td-created-date {
    position: absolute;
    top: 12px;
  }
  td.td-student {
    max-width: 100px !important;
  }
  tr {
    padding: 12px 0;
    position: relative;
  }
}
.td-created-date {
  min-width: 125px;
  padding: 8px 5px;
  text-wrap: nowrap;
  vertical-align: top;
  width: 125px;
}
.td-note {
  max-width: 300px;
  padding: 8px 5px;
  vertical-align: top;
  width: 65%;
}
.td-student {
  font-weight: bold;
  max-width: 250px;
  min-width: 150px;
  padding: 8px 5px;
  vertical-align: top;
  width: 20%;
}
.th-created-date {
  padding: 5px;
  text-wrap: nowrap;
}
.th-note {
  padding: 5px;
}
.th-student {
  padding: 5px;
}
.toggle-note-btn {
  height: 24px;
  justify-content: start;
  letter-spacing: normal;
  margin-left: -13px;
  width: 100%;
}
</style>
