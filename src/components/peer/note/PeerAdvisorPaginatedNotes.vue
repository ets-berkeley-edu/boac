<template>
  <div class="table-container">
    <table
      v-if="size(notes)"
      id="notes-for-peer-advisor-view"
      class="mt-5 w-100"
    >
      <caption class="sr-only">Peer Advising notes, sorted by date created descending.</caption>
      <thead :class="{'sr-only': smAndDown}">
        <tr>
          <th class="border-b-md th-student" role="columnheader" scope="col">Student</th>
          <th class="border-b-md th-note" role="columnheader" scope="col">Note</th>
          <th class="border-b-md th-topics" role="columnheader" scope="col">Topic(s)</th>
          <th class="border-b-md th-created-date text-right" role="columnheader" scope="col">Date Created</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(note, index) in notes"
          :id="`tr-peer-advisor-note-${note.id}`"
          :key="index"
          :aria-description="`Note ${getNotePosition(note, index)}`"
          :class="{
            'bg-sky-blue': expandedNoteIds.includes(note.id),
            'bg-surface-light': (index % 2 === 0),
            'border-b-md': smAndDown && index === notes.length - 1
          }"
          tabindex="-1"
        >
          <td
            :id="`td-note-${note.id}-student`"
            :class="{'border-b-md': !smAndDown && index === notes.length - 1}"
            class="font-weight-bold text-medium-emphasis td-student"
          >
            <router-link
              v-if="currentUser.isAdmin"
              :id="`note-${note.id}-link-to-student`"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
              :to="studentRoutePath(note.student.uid, currentUser.inDemoMode)"
            >
              {{ note.student ? lastNameFirst(note.student) : getStudentName(note) }}
            </router-link>
            <div v-if="!currentUser.isAdmin" :class="{'demo-mode-blur': currentUser.inDemoMode}">
              {{ getStudentName(note) }}
            </div>
          </td>
          <td
            :id="`td-note-${note.id}-body`"
            :class="{'border-b-md': !smAndDown && index === notes.length - 1}"
            class="td-note"
            :colspan="expandedNoteIds.includes(note.id) ? 2 : 1"
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
                  <span class="truncate-with-ellipsis" v-html="stripHtmlAndTrim(note.body)" />
                  <span v-if="note.attachments.length" class="ml-2">
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
                <PeerAdvisingNoteDetails class="my-3" :note="note" :note-description="`Note ${getNotePosition(note, index)}`" />
              </div>
            </v-expand-transition>
          </td>
          <td
            v-if="!expandedNoteIds.includes(note.id)"
            :id="`td-note-${note.id}-topics`"
            :class="{
              'border-b-md': !smAndDown && index === notes.length - 1
            }"
            class="td-topics"
          >
            <div class="align-center d-flex font-weight-medium justify-space-between w-100">
              <span
                v-if="note.topics.length"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
                class="truncate-with-ellipsis"
              >
                {{ note.topics.join(', ') }}
              </span>
              <span v-if="!note.topics.length && !smAndDown">
                <span aria-hidden="true" class="text-medium-emphasis">&mdash;</span>
                <span class="sr-only">blank</span>
              </span>
            </div>
          </td>
          <td
            :id="`td-note-${note.id}-created-at`"
            :class="{
              'border-b-md': !smAndDown && index === notes.length - 1,
              'demo-mode-blur': currentUser.inDemoMode
            }"
            class="td-created-date text-right"
          >
            <span :aria-hidden="true">{{ DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_MED) }}</span>
            <span class="sr-only">{{ DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_FULL) }}</span>
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
import {lastNameFirst, putFocusNextTick, stripHtmlAndTrim, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import PeerAdvisingNoteDetails from '@/components/peer/note/PeerAdvisingNoteDetails.vue'

const props = defineProps({
  notes: {
    required: true,
    type: Array<Note>
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

const getNoteLabel = (note: Note, index: number) => {
  const attachments = note.attachments.length ? `, ${note.attachments.length} attachments` : ''
  const createdDate = `${DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_FULL)}`
  const rowPosition = getNotePosition(note, index)
  return `${rowPosition}, ${getStudentName(note)}, dated ${createdDate}${attachments}. ${stripHtmlAndTrim(note.body)}`
}

const getNotePosition = (note: Note, index: number) => `${index + 1} of ${size(props.notes) || 'unknown'}`

const getStudentName = (note: Note) => note.student ? `${note.student.firstName} ${note.student.lastName}` : `SID: ${note.sid}`

const toggleShowHide = (note: Note) => {
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
@media (max-width: 959px) {
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
  width: 60%;
}
.td-student {
  max-width: 250px;
  min-width: 150px;
  padding: 8px 5px;
  vertical-align: top;
  width: 15%;
}
.td-topics {
  max-width: 200px;
  padding: 8px 5px;
  vertical-align: top;
  width: 25%;
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
.th-topics {
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
