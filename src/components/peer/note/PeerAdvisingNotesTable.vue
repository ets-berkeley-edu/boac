<template>
  <div class="peer-advising-table-wrapper">
    <slot v-if="!size(notes)" name="noData" />
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
          :aria-description="`Note ${getNotePosition(index)}`"
          :class="{
            'bg-sky-blue expanded border-b-sm': isExpanded(note),
            'bg-surface-light': (index % 2 === 0),
            'border-b-md': index === notes.length - 1
          }"
          tabindex="-1"
        >
          <td
            :id="`td-note-${note.id}-student`"
            class="font-weight-bold td-student"
            :class="{'d-contents': !smAndDown}"
          >
            <div class="grid-cell">
              <slot name="studentName" :note="note" />
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
                :aria-expanded="false"
                :aria-label="`Expand message ${getNoteLabel(note, index)}`"
                class="align-center d-flex justify-start px-3 text-none text-primary toggle-note-btn v-btn"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
                @click="() => toggleShowHide(note)"
              >
                <span class="v-btn__overlay" />
                <span class="truncate-with-ellipsis" v-html="stripHtmlAndSummarize((note as Note).body || (note as NoteSearchResult).noteSnippet)" />
                <span v-if="(note as NoteSearchResult).attachmentCount || size((note as Note).attachments)" class="ml-2">
                  <span class="sr-only">Has attachment(s)</span>
                  <v-icon class="has-attachment-icon" :icon="mdiPaperclip" size="small" />
                </span>
              </button>
            </div>
            <div v-if="isExpanded(note)" :class="{'d-contents': !smAndDown}">
              <div class="grid-cell">
                <v-btn
                  v-if="editingNoteId !== note.id"
                  :id="`show-note-${note.id}-details`"
                  :aria-expanded="true"
                  :aria-label="`Close message ${getNoteLabel(note, index)}`"
                  class="toggle-note-btn px-4"
                  color="primary"
                  :prepend-icon="mdiCloseCircle"
                  text="Close Message"
                  variant="outlined"
                  @click="toggleShowHide(note)"
                />
              </div>
              <v-expand-transition>
                <div
                  v-if="isExpanded(note)"
                  :class="{'mb-3': !smAndDown}"
                  class="grid-cell note-details"
                >
                  <PeerAdvisingNoteDetails
                    v-if="note.id !== editingNoteId"
                    class="ml-10"
                    :note="getNote(note)"
                    :note-description="`Note ${getNotePosition(index)}`"
                  />
                  <div v-if="note.id === editingNoteId" class="edit-advising-note-container">
                    <EditAdvisingNote
                      :after-cancel="afterNoteEditCancel"
                      :after-saved="afterEditAdvisingNote"
                      initial-mode="editNote"
                      wrapper-class="pl-10 w-100"
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
            <div class="grid-cell">
              <div v-if="isExpanded(note) && editingNoteId !== note.id && canUserEditNote(getNote(note), currentUser)" class="pl-2">
                <!--
                TODO: Give Peer Advisors the power to edit their own notes.
                <v-btn
                  :id="`edit-note-${note.id}-button`"
                  :aria-label="`Edit ${getNoteLabel(note, index)}`"
                  class="action-button"
                  color="primary"
                  density="compact"
                  size="md"
                  slim
                  text="Edit Note"
                  variant="text"
                  @click="() => editNote(note.id)"
                />
                -->
                <v-btn
                  v-if="isPeerAdvisorManager(currentUser)"
                  :id="`delete-note-button-${note.id}`"
                  :aria-label="`Delete ${getNoteLabel(note, index)}`"
                  class="action-button"
                  color="primary"
                  density="compact"
                  size="md"
                  text="Delete Note"
                  variant="text"
                  @click="() => onClickDeleteNote(getNote(note))"
                />
              </div>
              <div
                :class="{'mt-4': isExpanded(note) && editingNoteId !== note.id && canUserEditNote(getNote(note), currentUser)}"
                class="created-date text-nowrap"
              >
                <span :aria-hidden="true">{{ DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_MED) }}</span>
                <span class="sr-only">{{ DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_FULL) }}</span>
              </div>
              <v-expand-transition>
                <div v-if="getNote(note) && isExpanded(note)" :class="{'mt-4': !isExpanded(note)}">
                  <div v-if="getNote(note).author.name || getNote(note).author.email" class="mt-2">
                    <div class="font-size-15 text-medium-emphasis text-nowrap">Created by:</div>
                    <div v-if="getNote(note).author.uid && getNote(note).author.name">
                      <router-link
                        v-if="currentUser.isAdmin && getNote(note).peerAdvisingDepartmentId"
                        :id="`note-${note.id}-link-to-peer-advisor-home`"
                        :to="`/peer_advisor/${getNote(note).author.uid}/home`"
                      >
                        {{ getNote(note).author.name }}
                      </router-link>
                      <a
                        v-if="!currentUser.isAdmin || !getNote(note).peerAdvisingDepartmentId"
                        :id="`note-${note.id}-author-name`"
                        :href="`https://www.berkeley.edu/directory/results?search-term=${getNote(note).author.name}`"
                        target="_blank"
                      >
                        {{ getNote(note).author.name }} <span class="sr-only">&nbsp;UC Berkeley Directory page (opens in new window)</span>
                      </a>
                    </div>
                    <div :id="`note-${note.id}-author-role`" class="font-weight-550 mt-2">
                      {{ capitalizeAllWords(replace(getNote(note).author.role, '_', ' ')) }}
                    </div>
                  </div>
                  <div
                    v-if="size(getNote(note).author.departments)"
                    class="text-medium-emphasis"
                  >
                    <div v-for="(department, deptIndex) in getNote(note).author.departments" :key="deptIndex">
                      <span :id="`note-${note.id}-author-dept-${deptIndex}`">{{ department.deptName }}</span>
                    </div>
                  </div>
                  <div v-if="getNote(note).peerAdvisingDepartment" class="text-medium-emphasis">
                    <span :id="`note-${note.id}-university-department`">{{ getNote(note).peerAdvisingDepartment.deptName }}</span><!--
                    --><span v-if="getNote(note).peerAdvisingDepartment.name !== getNote(note).peerAdvisingDepartment.deptName" :id="`note-${note.id}-peer-advising-department`">, {{ getNote(note).peerAdvisingDepartment.name }}</span>
                  </div>
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
import {mdiCloseCircle, mdiPaperclip} from '@mdi/js'
import {computed, ref} from 'vue'
import {get, replace, size, truncate} from 'lodash'
import {useDisplay} from 'vuetify'
import type {Note, NoteSearchResult} from '@/lib/types'
import {alertScreenReader, capitalizeAllWords, putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {canUserEditNote, stripHtmlAndSummarize} from '@/lib/note'
import {deleteNote} from '@/api/notes'
import {isPeerAdvisorManager} from '@/lib/boa-user'
import {useContextStore} from '@/stores/context'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import EditAdvisingNote from '@/components/note/EditAdvisingNote.vue'
import PeerAdvisingNoteDetails from '@/components/peer/note/PeerAdvisingNoteDetails.vue'

const props = defineProps({
  getNote: {
    default: (note: Note) => note,
    required: false,
    type: Function
  },
  getNoteLabel: {
    required: true,
    type: Function
  },
  notes: {
    required: true,
    type: Array<Note | NoteSearchResult>
  },
  setNoteDetails: {
    default: () => {},
    required: false,
    type: Function
  }
})

const {smAndDown} = useDisplay()
const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const editingNoteId = ref<number | undefined>()
const expandedNoteIds = ref<number[]>([])
const noteForDelete = ref<Note | undefined>()
const showDeleteConfirmation = computed(() => !!noteForDelete.value)

const afterEditAdvisingNote = (updatedNote: Note, putFocusId: string) => {
  editingNoteId.value = undefined
  putFocusNextTick(putFocusId || `edit-note-${updatedNote.id}-button`)
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

// TODO: Give Peer Advisors the power to edit their own notes.
// const editNote = (noteId: number) => {
//   editingNoteId.value = noteId
//   putFocusNextTick('edit-note-subject')
// }

const getNotePosition = (index: number) => `${index + 1} of ${size(props.notes) || 'unknown'}`

const isExpanded = (note: Note | NoteSearchResult) => expandedNoteIds.value.includes(note.id)

const onClickDeleteNote = (note: Note) => {
  // The following opens the "Are you sure?" modal
  noteForDelete.value = note
}

const toggleShowHide = (note: Note | NoteSearchResult) => {
  const index = expandedNoteIds.value.indexOf(note.id)
  if (index > -1) {
    expandedNoteIds.value.splice(index, 1)
    putFocusNextTick(`open-peer-advising-${note.id}`)
  } else {
    props.setNoteDetails(note)
    expandedNoteIds.value.push(note.id)
    putFocusNextTick(`show-note-${note.id}-details`)
  }
}
</script>

<style scoped>
@media (max-width: 959px) {
  .grid-cell {
    padding-bottom: 0px !important;
  }
  .peer-advising-table-wrapper {
    min-width: 300px;
    overflow: hidden; /* Prevent horizontal scrollbar */
  }
  .peer-advising-table-wrapper .td-created-date .created-date {
    position: absolute;
    right: 12px;
    top: 12px;
    width: 20% !important;
  }
  .peer-advising-table-wrapper .td-note .grid-cell.note-details {
    margin-top: 8px !important;
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
.action-button {
  font-weight: 590;
  margin-left: -10px;
}
.d-contents {
  display: contents;
}
.edit-advising-note-container {
  margin-top: -25px;
  padding-right: 25px;
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
  z-index: 1;
}
.peer-advising-table-wrapper .td-student .grid-cell {
  grid-area: 1 / 1 / 1 / 1;
  min-width: 200px;
}
.peer-advising-table-wrapper .toggle-note-btn {
  height: 24px;
  letter-spacing: normal;
  width: 100%;
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
