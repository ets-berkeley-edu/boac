<template>
  <div class="peer-advising-notes">
    <slot v-if="!size(notes) && !isFetchingNotes" name="noData" />
    <div
      v-if="size(notes)"
      id="notes-for-peer-advisor-view"
      class="d-block mt-5 w-100"
    >
      <article
        v-for="(note, index) in notes"
        :id="`peer-advisor-note-${note.id}`"
        :key="index"
        class="peer-note"
        :class="{
          'bg-sky-blue expanded border-b-sm': isExpanded(note),
          'bg-surface-light': (index % 2 === 0),
          'border-b-md': index === notes.length - 1,
          'grid-wrap': xs
        }"
      >
        <div
          :id="`peer-advisor-note-${note.id}-student`"
          class="font-weight-bold note-student grid-cell"
        >
          <PeerAdvisorNoteStudentName
            class="text-wrap"
            :note="note"
            :show-student-last-name-first="showStudentLastNameFirst"
          />
        </div>
        <div
          class="note-summary grid-cell"
          :class="{
            'align-content-center': !isExpanded(note),
            'align-content-start': isExpanded(note)
          }"
        >
          <button
            v-if="!isExpanded(note)"
            :id="`note-${note.id}-is-closed`"
            :aria-controls="`note-details-${note.id} note-actions-${note.id} note-dates-${note.id}`"
            :aria-expanded="false"
            :aria-label="`Message ${getNoteLabel(note, index)}`"
            class="align-center d-flex justify-start px-3 text-none text-primary v-btn w-100"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            @click="() => toggleShowHide(note)"
          >
            <span class="v-btn__overlay" />
            <span
              class="truncate-with-ellipsis"
              v-html="stripHtmlAndSummarize(note.body || summarizeTopics(note.topics))"
            />
            <TimelineMessageIcons v-if="size(note.attachments) || size(note.comments)" :message="note" />
          </button>
          <v-btn
            v-if="isExpanded(note) && editingNoteId !== note.id"
            :id="`close-peer-advising-${note.id}`"
            :aria-controls="`note-details-${note.id} note-actions-${note.id} note-dates-${note.id}`"
            :aria-expanded="true"
            :aria-label="`Close message ${getNoteLabel(note, index)}`"
            class="vertical-top w-100"
            color="primary"
            density="compact"
            :prepend-icon="mdiCloseCircle"
            slim
            text="Close Message"
            variant="text"
            @click="toggleShowHide(note)"
          />
        </div>
        <v-expand-transition>
          <div v-show="isExpanded(note)" :id="`peer-advisor-note-details-${note.id}`" class="note-details grid-cell pt-3">
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
                class="px-2 pl-md-10 pr-md-0 w-100"
                initial-mode="editNote"
                :note-id="note.id"
              />
            </div>
          </div>
        </v-expand-transition>
        <div v-if="!isExpanded(note)" class="align-content-center created-date grid-cell text-no-wrap text-right">
          <TimelineDate
            :id="`collapsed-note-${note.id}-created-at`"
            aria-hidden="true"
            :date="note.updatedAt || note.createdAt"
            :include-time-of-day="false"
            sr-prefix="Last updated on"
          />
        </div>
        <div
          v-if="isExpanded(note)"
          :id="`peer-advisor-note-${note.id}-created-at`"
          :class="{
            'demo-mode-blur': currentUser.inDemoMode
          }"
          class="created-date grid-cell"
        >
          <div
            v-if="editingNoteId !== note.id && canUserEditNote(note, currentUser)"
            v-show="isExpanded(note)"
            :id="`note-actions-${note.id}`"
            class="d-flex flex-column"
          >
            <v-btn
              v-show="isExpanded(note)"
              :id="`edit-note-${note.id}-button`"
              :aria-label="`Edit note ${getNoteLabel(note, index)}`"
              class="note-action-button font-size-16 mb-3"
              color="primary"
              density="compact"
              :disabled="!!editingNoteId"
              slim
              text="Edit Note"
              variant="text"
              @click="() => editNote(note.id)"
            />
            <v-btn
              v-if="isPeerAdvisorManager(currentUser)"
              v-show="isExpanded(note)"
              :id="`delete-note-button-${note.id}`"
              :aria-label="`Delete note ${getNoteLabel(note, index)}`"
              class="note-action-button font-size-16 mb-3"
              color="primary"
              density="compact"
              slim
              text="Delete Note"
              variant="text"
              @click="() => onClickDeleteNote(note)"
            />
          </div>
          <v-expand-transition>
            <div v-show="isExpanded(note)" :id="`note-dates-${note.id}`">
              <div class="text-no-wrap">
                <div>
                  <div aria-hidden="true" class="font-size-14 text-medium-emphasis">Created:</div>
                  <TimelineDate
                    :id="`expanded-note-${note.id}-created-at`"
                    :date="note.createdAt"
                    sr-prefix="Created on"
                    :include-time-of-day="note.createdAt.length > 10"
                  />
                </div>
                <div v-if="note.updatedAt" class="mt-2">
                  <div aria-hidden="true" class="font-size-14 text-medium-emphasis">Updated:</div>
                  <TimelineDate
                    :id="`expanded-note-${note.id}-updated-at`"
                    :date="note.updatedAt"
                    :include-time-of-day="note.updatedAt.length > 10"
                    sr-prefix="Last updated on"
                  />
                </div>
              </div>
              <div class="mt-4">
                <div v-if="note.author.name || note.author.email" class="mt-2">
                  <div class="font-size-14 text-medium-emphasis text-no-wrap mb-1">Created by:</div>
                  <AuthorDetails
                    activator-class="font-size-14"
                    :author="note.author"
                    :id-prefix="`note-${note.id}`"
                    :peer-advising-department-id="note.peerAdvisingDepartmentId"
                  />
                </div>
              </div>
            </div>
          </v-expand-transition>
        </div>
        <div
          v-if="isExpanded(note) && editingNoteId !== note.id"
          :id="`peer-advisor-note-${note.id}-comments`"
          class="note-comments grid-cell"
        >
          <AdvisingComments
            class="pl-5"
            :class="{'sr-only': !isExpanded(note)}"
            :parent="note"
          />
        </div>
      </article>
    </div>
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
        containing text "<span class="font-weight-bold text-medium-emphasis">{{ truncate(stripHtmlAndTrim(noteForDelete.body), {separator: ' '}) }}</span>"?</span>
    </AreYouSureModal>
  </div>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {each, find, get, remove, replace, size, truncate} from 'lodash'
import {mdiCloseCircle} from '@mdi/js'
import {useDisplay} from 'vuetify'
import type {Note} from '@/lib/types'
import {alertScreenReader, capitalizeAllWords, putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {canUserEditNote, stripHtmlAndSummarize, summarizeTopics} from '@/lib/note'
import {deleteNote} from '@/api/notes'
import {getPeerAdvisingDepartmentById} from '@/lib/berkeley-department'
import {isPeerAdvisorManager} from '@/lib/boa-user'
import {useContextStore} from '@/stores/context'
import AdvisingComments from '@/components/comment/AdvisingComments'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import AuthorDetails from '@/components/note/AuthorDetails'
import EditAdvisingNote from '@/components/note/EditAdvisingNote.vue'
import PeerAdvisingNoteDetails from '@/components/peer/note/PeerAdvisingNoteDetails.vue'
import PeerAdvisorNoteStudentName from '@/components/peer/note/PeerAdvisorNoteStudentName.vue'
import TimelineDate from '@/components/student/profile/TimelineDate.vue'
import TimelineMessageIcons from '@/components/student/profile/academic-timeline/TimelineMessageIcons.vue'

const props = defineProps({
  afterNoteEdit: {
    default: () => {},
    required: false,
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

const {smAndDown, xs} = useDisplay()
const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const editingNoteId = ref<number | undefined>()
const expandedNoteIds = ref<number[]>([])
const noteForDelete = ref<Note | undefined>()
const showDeleteConfirmation = computed(() => !!noteForDelete.value)

onMounted(() => {
  contextStore.setEventHandler('comment-deleted', onCommentDeleted)
})

onUnmounted(() => {
  contextStore.removeEventHandler('comment-deleted', onCommentDeleted)
})

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

const peerAdvisingDepartmentLabel = (note: Note): string => {
  const pad = note.peerAdvisingDepartment ?? getPeerAdvisingDepartmentById(note.peerAdvisingDepartmentId)
  if (!pad) {
    return ''
  }
  const deptName = pad.deptName ?? ''
  const name = pad.name ?? ''
  return name !== deptName ? `${deptName}, ${name}` : deptName
}

const getNoteAuthorLabel = (note: Note) => {
  const authorName = note.author.name
  const role = note.author.role ? capitalizeAllWords(replace(note.author.role, '_', ' ')) : ''
  const departments = peerAdvisingDepartmentLabel(note)
  const rolePart = role ? `, ${role}` : ''
  const deptPart = departments ? `, ${departments}` : ''
  return `${authorName ? `, created by ${authorName}` : ''}${rolePart}${deptPart}`
}

const getNoteLabel = (note: Note, index: number) => {
  const attachments = note.attachments.length ? `, ${note.attachments.length} attachments` : ''
  const createdDate = `${DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_FULL)}`
  const rowPosition = `${index + 1} of ${size(props.notes)}`
  return `${rowPosition}, ${getStudentName(note)}. ${truncate(stripHtmlAndSummarize(note.body), {length: 50, separator: ' '})} dated ${createdDate}${attachments}${getNoteAuthorLabel(note)}.`
}

const getNotePosition = (index: number) => `${index + 1} of ${size(props.notes) || 'unknown'}`

const getStudentName = (note: Note) => note.student ? `${note.student.firstName} ${note.student.lastName}` : `SID: ${note.sid}`

const isExpanded = (note: Note) => expandedNoteIds.value.includes(note.id)

const onClickDeleteNote = (note: Note) => {
  // The following opens the "Are you sure?" modal
  noteForDelete.value = note
}

const onCommentDeleted = ids => {
  const note = find(props.notes, {'id': ids.parentId})
  if (note) {
    remove(note.comments, {'id': ids.commentId})
  }
}

const toggleShowHide = (note: Note) => {
  const index = expandedNoteIds.value.indexOf(note.id)
  if (index > -1) {
    expandedNoteIds.value.splice(index, 1)
    each(note.comments, c => { c.read = true })
    putFocusNextTick(`note-${note.id}-is-closed`, {scroll: false})
  } else {
    expandedNoteIds.value.push(note.id)
    putFocusNextTick(`close-peer-advising-${note.id}`, {scroll: false})
  }
}
</script>

<style>
.peer-advising-notes .academic-timeline-column-date {
  margin-right: -8px !important;
  min-width: 13rem;
  width: 13rem;
}
</style>

<style scoped>
.edit-advising-note-container {
  margin-top: -30px;
  padding-right: 25px;
}
.note-action-button {
  display: block;
  font-weight: 590;
  margin-left: -8px;
  max-width: fit-content;
}
.peer-advising-notes .grid-cell {
  padding: 8px;
}
.peer-advising-notes .note-summary {
  grid-area: 1 / 2 / 1 / 2;
}
.peer-advising-notes .created-date {
  grid-area: 1 / 3 / 3 / 3;
}
.peer-advising-notes .note-comments {
  grid-area: 3 / 1 / 3 / 4;
}
.peer-advising-notes .note-details {
  grid-area: 2 / 1 / 2 / 3;
}
.peer-advising-notes .note-student {
  grid-area: 1 / 1 / 1 / 1;
}
.peer-advising-notes .peer-note {
  display: grid;
  grid-template-columns: 15rem calc(100% - 23rem) 8rem;
  grid-template-rows: min-content;
  width: 100%;
}
.peer-advising-notes .peer-note.expanded {
  grid-template-columns: 15rem 1fr 13rem;
  grid-template-rows: min-content 1fr min-content;
}
.peer-advising-notes .peer-note.expanded.grid-wrap {
  grid-template-columns: auto auto;
  grid-template-rows: min-content min-content min-content min-content;
  .created-date {
    grid-area: 3 / 1 / 3 / 3;
    padding-left: 24px;
  }
  .note-comments {
    grid-area: 4 / 1 / 4 / 4;
  }
  .note-details {
    grid-area: 2 / 1 / 2 / 3;
    padding-left: 20px;
  }
}
</style>
