<template>
  <div class="peer-advising-table-wrapper">
    <slot v-if="!size(notes) && !isFetchingNotes" name="noData" />
    <table
      v-if="size(notes)"
      id="notes-for-peer-advisor-view"
      class="d-block mt-5 w-100"
    >
      <caption class="sr-only">Peer Advising notes, sorted by date created descending.</caption>
      <thead class="sr-only">
        <tr>
          <th class="border-b-md th-student" role="columnheader" scope="col">Student</th>
          <th class="border-b-md th-note" role="columnheader" scope="col">Note</th>
          <th class="border-b-md th-created-date" role="columnheader" scope="col">Date Created</th>
        </tr>
      </thead>
      <tbody class="d-block w-100">
        <tr
          v-for="(note, index) in notes"
          :id="`tr-peer-advisor-note-${note.id}`"
          :key="index"
          :class="{
            'bg-sky-blue expanded border-b-sm': isExpanded(note),
            'bg-surface-light': (index % 2 === 0),
            'border-b-md': index === notes.length - 1
          }"
        >
          <td
            :id="`td-note-${note.id}-student`"
            class="font-weight-bold td-student"
            :class="{'d-contents': !smAndDown}"
          >
            <div class="grid-cell">
              <PeerAdvisorNoteAuthorName
                :show-student-last-name-first="showStudentLastNameFirst"
                :note="note"
              />
            </div>
          </td>
          <td
            :id="`td-note-${note.id}-body`"
            class="td-note"
            :class="{'d-contents': !smAndDown}"
          >
            <div v-if="!isExpanded(note)" class="grid-cell">
              <button
                :id="`open-peer-advising-${note.id}`"
                aria-hidden="true"
                :aria-expanded="false"
                :aria-label="`Message ${getNoteLabel(note, index)}`"
                class="align-center d-flex justify-start px-3 text-none text-primary toggle-note-btn v-btn w-100"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
                tabindex="-1"
                @click="() => toggleShowHide(note)"
              >
                <span class="v-btn__overlay" />
                <span
                  class="truncate-with-ellipsis"
                  v-html="stripHtmlAndSummarize(note.body || summarizeTopics(note.topics))"
                />
                <span v-if="size(note.attachments)" class="ml-2">
                  <span class="sr-only">Has attachment(s)</span>
                  <v-icon class="has-attachment-icon" :icon="mdiPaperclip" size="small" />
                </span>
              </button>
              <span class="sr-only">
                {{ stripHtmlAndTrim(note.body || summarizeTopics(note.topics)) }}
              </span>
            </div>
            <div v-if="isExpanded(note)" :class="{'d-contents': !smAndDown}">
              <div class="grid-cell">
                <div class="d-flex pl-4 pr-md-4">
                  <v-btn
                    v-if="editingNoteId !== note.id"
                    :id="`show-note-${note.id}-details`"
                    aria-hidden="true"
                    :aria-expanded="true"
                    :aria-label="`Close message ${getNoteLabel(note, index)}`"
                    class="toggle-note-btn w-75 w-md-100"
                    color="primary"
                    :prepend-icon="mdiCloseCircle"
                    text="Close Message"
                    variant="text"
                    tabindex="-1"
                    @click="toggleShowHide(note)"
                  />
                </div>
              </div>
              <v-expand-transition>
                <div
                  v-if="isExpanded(note)"
                  :class="{'mb-3': !smAndDown}"
                  class="grid-cell note-details"
                >
                  <PeerAdvisingNoteDetails
                    v-if="note.id !== editingNoteId"
                    :after-note-edit="afterNoteUpdated"
                    class="px-1 px-sm-5"
                    :note="note"
                    :note-description="`Note ${getNotePosition(index)}`"
                  />
                  <div v-if="note.id === editingNoteId" :class="{'edit-advising-note-container': !smAndDown}">
                    <EditAdvisingNote
                      :after-cancel="afterNoteEditCancel"
                      :after-saved="afterEditAdvisingNote"
                      initial-mode="editNote"
                      wrapper-class="pl-md-10 w-100"
                      :note-id="note.id"
                    />
                  </div>
                </div>
              </v-expand-transition>
            </div>
          </td>
          <td
            :id="`td-note-${note.id}-created-at`"
            :class="{
              'd-contents': !smAndDown,
              'demo-mode-blur': currentUser.inDemoMode
            }"
            class="td-created-date"
          >
            <div class="grid-cell px-4 px-md-2">
              <span class="sr-only">
                {{ getNoteMetaForScreenReader(note) }}
              </span>
              <div
                v-if="isExpanded(note) && editingNoteId !== note.id && canUserEditNote(note, currentUser)"
                class="d-flex flex-column pl-5"
              >
                <v-btn
                  :id="`edit-note-${note.id}-button`"
                  :aria-label="`Edit note ${getNotePosition(index)}`"
                  class="edit-note-button font-size-16 mb-2 w-md-100"
                  color="primary"
                  density="compact"
                  :disabled="!!editingNoteId"
                  text="Edit Note"
                  variant="text"
                  @click="() => editNote(note.id)"
                />
                <v-btn
                  v-if="isPeerAdvisorManager(currentUser)"
                  :id="`delete-note-button-${note.id}`"
                  :aria-label="`Delete ${getNoteLabel(note, index)}`"
                  class="delete-note-button font-size-16 my-2 w-md-100"
                  color="primary"
                  density="compact"
                  size="md"
                  text="Delete Note"
                  variant="text"
                  @click="() => onClickDeleteNote(note)"
                />
              </div>
              <div v-if="!isExpanded(note)" class="created-date text-no-wrap">
                <TimelineDate
                  :id="`collapsed-note-${note.id}-updated-at`"
                  :date="note.updatedAt || note.createdAt"
                  :include-time-of-day="false"
                  sr-prefix="Last updated on"
                />
              </div>
              <div
                v-if="isExpanded(note)"
                class="created-date text-no-wrap"
              >
                <div>
                  <div :aria-hidden="true" class="font-size-14 text-medium-emphasis">Created:</div>
                  <TimelineDate
                    :id="`expanded-note-${note.id}-created-at`"
                    :date="note.createdAt"
                    sr-prefix="Created on"
                    :include-time-of-day="note.createdAt.length > 10"
                  />
                </div>
                <div v-if="note.updatedAt" class="mt-2">
                  <div :aria-hidden="true" class="font-size-14 text-medium-emphasis">Updated:</div>
                  <TimelineDate
                    :id="`expanded-note-${note.id}-updated-at`"
                    :date="note.updatedAt"
                    :include-time-of-day="note.updatedAt.length > 10"
                    sr-prefix="Last updated on"
                  />
                </div>
              </div>
              <v-expand-transition>
                <div v-if="isExpanded(note)" :class="{'mt-4': !isExpanded(note)}">
                  <div v-if="note.author.name || note.author.email" class="mt-2">
                    <div class="font-size-15 text-medium-emphasis text-no-wrap">Created by:</div>
                    <div v-if="note.author.uid && note.author.name">
                      <router-link
                        v-if="currentUser.isAdmin && note.peerAdvisingDepartmentId"
                        :id="`note-${note.id}-link-to-peer-advisor-home`"
                        :class="{'demo-mode-blur': currentUser.inDemoMode}"
                        :to="`/peer_advisor/${note.author.uid}/home`"
                      >
                        {{ note.author.name }}
                      </router-link>
                      <a
                        v-if="!currentUser.isAdmin || !note.peerAdvisingDepartmentId"
                        :id="`note-${note.id}-author-name`"
                        :class="{'demo-mode-blur': currentUser.inDemoMode}"
                        :href="`https://www.berkeley.edu/directory/results?search-term=${note.author.name}`"
                        target="_blank"
                      >
                        {{ note.author.name }} <span class="sr-only">&nbsp;UC Berkeley Directory page (opens in new tab)</span>
                      </a>
                    </div>
                    <div :id="`note-${note.id}-author-role`" class="font-weight-550 mt-2">
                      {{ capitalizeAllWords(replace(note.author.role, '_', ' ')) }}
                    </div>
                  </div>
                  <div
                    v-if="size(note.author.departments)"
                    class="text-medium-emphasis"
                  >
                    <div v-for="(department, deptIndex) in note.author.departments" :key="deptIndex">
                      <span :id="`note-${note.id}-author-dept-${deptIndex}`">{{ department.deptName }}</span>
                    </div>
                  </div>
                  <PeerAdvisingDepartmentSummary
                    :id-prefix="`note-${note.id}`"
                    :peer-advising-department-id="note.peerAdvisingDepartmentId"
                  />
                </div>
              </v-expand-transition>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="!size(notes)" id="peer-advisor-no-notes" class="align-center d-flex pt-3">
      <slot name="append" />
    </div>
    <AreYouSureModal
      v-model="showDeleteConfirmation"
      button-label-confirm="Delete"
      :function-cancel="cancelTheDelete"
      :function-confirm="deleteConfirmed"
      modal-header="Delete note"
    >
      Are you sure you want to delete the note
      <span v-if="get(noteForDelete, 'subject')">
        with subject "<span class="font-weight-bold text-medium-emphasis">{{ get(noteForDelete, 'subject') }}</span>"?
      </span>
      <span v-if="noteForDelete && !get(noteForDelete, 'subject')">
        containing text "<span class="font-weight-bold text-medium-emphasis">{{ truncate(stripHtmlAndTrim(noteForDelete.body), {length: 30}) }}</span>"?</span>
    </AreYouSureModal>
  </div>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import {computed, ref} from 'vue'
import {get, replace, size, truncate} from 'lodash'
import {mdiCloseCircle, mdiPaperclip} from '@mdi/js'
import {useDisplay} from 'vuetify'
import type {Note} from '@/lib/types'
import {alertScreenReader, capitalizeAllWords, putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {canUserEditNote, stripHtmlAndSummarize, summarizeTopics} from '@/lib/note'
import {deleteNote} from '@/api/notes'
import {isPeerAdvisorManager} from '@/lib/boa-user'
import {useContextStore} from '@/stores/context'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import EditAdvisingNote from '@/components/note/EditAdvisingNote.vue'
import PeerAdvisingNoteDetails from '@/components/peer/note/PeerAdvisingNoteDetails.vue'
import PeerAdvisingDepartmentSummary from '@/components/peer/PeerAdvisingDepartmentSummary.vue'
import PeerAdvisorNoteAuthorName from '@/components/peer/note/PeerAdvisorNoteAuthorName.vue'
import TimelineDate from '@/components/student/profile/TimelineDate.vue'

const props = defineProps({
  afterNoteEdit: {
    required: true,
    type: Function
  },
  notes: {
    required: true,
    type: Array<Note>
  },
  isFetchingNotes: {
    required: true,
    type: Boolean
  },
  showStudentLastNameFirst: {
    required: false,
    type: Boolean
  }
})

const {smAndDown} = useDisplay()
const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const editingNoteId = ref<number | undefined>()
const expandedNoteIds = ref<number[]>([])
const noteForDelete = ref<Note | undefined>()
const showDeleteConfirmation = computed(() => !!noteForDelete.value)

const afterEditAdvisingNote = async (updatedNote: Note, putFocusId: string) => {
  editingNoteId.value = undefined
  await props.afterNoteEdit(editingNoteId.value)
  putFocusNextTick(putFocusId || `edit-note-${updatedNote.id}-button`)
}

const afterNoteUpdated = async (noteId: number, putFocusElementId?: string) => {
  await props.afterNoteEdit(noteId)
  editingNoteId.value = undefined
  putFocusNextTick(putFocusElementId || `show-note-${editingNoteId.value}-details`)
}
const afterNoteEditCancel = () => {
  putFocusNextTick(`edit-note-${editingNoteId.value}-button`)
  editingNoteId.value = undefined
}

const cancelTheDelete = () => {
  if (noteForDelete.value) {
    alertScreenReader('Canceled')
    putFocusNextTick(`delete-note-button-${noteForDelete.value.id}`)
    noteForDelete.value = undefined
  }
}

const deleteConfirmed = () => {
  if (noteForDelete.value) {
    deleteNote(noteForDelete.value.id).then(() => {
      alertScreenReader('Note deleted')
      noteForDelete.value = undefined
      putFocusNextTick('modal-header')
    })
  }
}

const editNote = (noteId: number) => {
  editingNoteId.value = noteId
  putFocusNextTick('edit-note-subject')
}

const getNoteLabel = (note: Note, index: number) => {
  const attachments = note.attachments.length ? `, ${note.attachments.length} attachments` : ''
  const createdDate = `${DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_FULL)}`
  const rowPosition = `${index + 1} of ${size(props.notes)}`
  return `${rowPosition}, ${getStudentName(note)}. ${truncate(stripHtmlAndSummarize(note.body))} dated ${createdDate}${attachments}.`
}

const getNoteMetaForScreenReader = (note: Note) => {
  const date = DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_FULL)
  const authorName = note.author.name
  const role = note.author.role ? capitalizeAllWords(replace(note.author.role, '_', ' ')) : ''
  const departments = size(note.author.departments)
    ? note.author.departments.map(dept => dept.deptName).join(', ')
    : ''
  const rolePart = role ? `, ${role}` : ''
  const deptPart = departments ? `, ${departments}` : ''
  return `Dated ${date}${authorName ? `, created by ${authorName}` : ''}${rolePart}${deptPart}.`
}

const getNotePosition = (index: number) => `${index + 1} of ${size(props.notes) || 'unknown'}`

const getStudentName = (note: Note) => note.student ? `${note.student.firstName} ${note.student.lastName}` : `SID: ${note.sid}`

const isExpanded = (note: Note) => expandedNoteIds.value.includes(note.id)

const onClickDeleteNote = (note: Note) => {
  // The following opens the "Are you sure?" modal
  noteForDelete.value = note
}

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
  .grid-cell {
    padding-bottom: 0 !important;
  }
  .peer-advising-table-wrapper {
    min-width: 300px;
    overflow: hidden; /* Prevent horizontal scrollbar */
  }
  .peer-advising-table-wrapper .td-created-date {
    width: calc(100% - 10rem) !important;
  }
  .peer-advising-table-wrapper .td-created-date .created-date {
    position: absolute;
    right: 12px;
    text-align: end;
    top: 12px;
    width: 10rem !important;
  }
  .peer-advising-table-wrapper tr.expanded .td-created-date .created-date {
    position: static;
    right: auto;
    top: auto;
    width: 100% !important;
    text-align: left;
    margin-top: 8px;
  }
  .peer-advising-table-wrapper .td-note .grid-cell.note-details {
    margin: 12px 0 !important;
    width: calc(100% - 10rem) !important;
  }
  .peer-advising-table-wrapper table, tbody, tr {
    border-collapse: collapse;
    display: block !important; /* Allow table to stack vertically */
  }
  .peer-advising-table-wrapper td {
    display: block !important; /* Allow cells to stack vertically */
    max-width: unset !important;
    padding: 2px 8px !important;
    width: 100% !important;
  }
  .peer-advising-table-wrapper tr {
    position: relative;
  }
  .peer-advising-table-wrapper tr.expanded {
    padding-bottom: 12px !important;
  }
}
.d-contents {
  display: contents;
}
.delete-note-button {
  font-weight: 590;
  margin-left: -18px;
}
.edit-advising-note-container {
  margin-top: -30px;
  padding-right: 25px;
}
.edit-note-button {
  font-weight: 590;
  margin-left: -18px;
}
.has-attachment-icon {
  margin-bottom: 1px;
}
.peer-advising-table-wrapper .grid-cell {
  padding: 8px 12px;
}
.peer-advising-table-wrapper .td-created-date .grid-cell {
  grid-area: 1 / 3 / 1 / 3;
}
.peer-advising-table-wrapper .td-note .grid-cell {
  grid-area: 1 / 2 / 1 / 2;
  z-index: 2;
}
.peer-advising-table-wrapper .td-note .grid-cell.note-details {
  grid-area: 2 / 1 / 1 / 3;
  margin-top: 68px;
  z-index: 3;
}
.peer-advising-table-wrapper .td-student .grid-cell {
  grid-area: 1 / 1 / 1 / 1;
  min-width: 200px;
}
.peer-advising-table-wrapper .toggle-note-btn {
  height: 24px;
  letter-spacing: normal;
}
.peer-advising-table-wrapper td {
  padding: 8px 12px;
  vertical-align: top;
}
.peer-advising-table-wrapper tr {
  display: grid;
  grid-auto-rows: min-content;
  grid-template-columns: 20% 60% 20%;
  width: 100%;
}
</style>
