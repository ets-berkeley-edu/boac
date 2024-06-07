<template>
  <div class="default-margins">
    <h1 class="mb-0">{{ currentUser.isAdmin ? 'Draft Notes' : 'My Draft Notes' }}</h1>
    <div v-if="!contextStore.loading">
      <div v-if="size(myDraftNotes)">
        <div v-if="!currentUser.isAdmin" class="font-weight-700 pb-3 text-medium-emphasis">
          A draft note is only visible to its author.
        </div>
        <v-data-table
          id="responsive-data-table"
          :cell-props="{
            class: 'font-size-14 vertical-baseline',
            style: $vuetify.display.mdAndUp ? 'max-width: 200px;' : ''
          }"
          disable-sort
          :headers="headers"
          :header-props="{class: 'data-table-header-cell'}"
          hide-default-footer
          hide-no-data
          :items="myDraftNotes || []"
          :items-per-page="-1"
          mobile-breakpoint="md"
          :row-props="row => ({id: `draft-note-${row.item.id}`})"
        >
          <template #item.student="{item}">
            <span v-if="item.student">
              <router-link
                :id="`link-to-student-${item.student.uid}`"
                :to="studentRoutePath(item.student.uid, currentUser.inDemoMode)"
              >
                <span :class="{'demo-mode-blur': currentUser.inDemoMode}">
                  {{ item.student.firstName }} {{ item.student.lastName }}
                </span>
              </router-link>
            </span>
            <span v-if="!item.student" class="font-italic">
              &mdash;
            </span>
          </template>
          <template #item.sid="{item}">
            <span :class="{'demo-mode-blur': currentUser.inDemoMode}">
              {{ item.sid || '&mdash;' }}
            </span>
          </template>
          <template #item.subject="{item}">
            <div class="align-center d-flex justify-space-between">
              <div>
                <div v-if="item.author.uid !== currentUser.uid" :class="{'demo-mode-blur': currentUser.inDemoMode}">
                  {{ trim(item.subject) || contextStore.config.draftNoteSubjectPlaceholder }}
                </div>
                <v-btn
                  v-if="item.author.uid === currentUser.uid"
                  :id="`open-draft-note-${item.id}`"
                  class="pl-0 text-primary"
                  :class="{'demo-mode-blur': currentUser.inDemoMode}"
                  density="compact"
                  variant="text"
                  @click="() => openEditModal(item)"
                >
                  {{ trim(item.subject) || contextStore.config.draftNoteSubjectPlaceholder }}
                </v-btn>
              </div>
              <div v-if="size(item.attachments)">
                <span class="sr-only">Has attachment(s)</span>
                <v-icon :icon="mdiPaperclip" />
              </div>
            </div>
          </template>
          <template v-if="currentUser.isAdmin" #item.author="{item}">
            {{ item.author.name }}
          </template>
          <template #item.updatedAt="{item}">
            <TimelineDate
              :date="item.updatedAt || item.createdAt"
              sr-prefix="Draft note saved on"
            />
          </template>
          <template #item.delete="{item}">
            <div class="float-right">
              <v-btn
                :disabled="isDeleting"
                variant="text"
                @click="() => openDeleteModal(item)"
              >
                <v-icon
                  aria-label="Delete"
                  :class="isDeleting ? 'text-medium-emphasis' : 'text-error'"
                  :icon="mdiTrashCan"
                  title="Delete"
                />
              </v-btn>
            </div>
          </template>
        </v-data-table>
      </div>
      <div v-if="!size(myDraftNotes)" class="pl-2 pt-2">
        {{ currentUser.isAdmin ? 'No' : 'You have no' }} saved drafts.
      </div>
      <AreYouSureModal
        :button-label-confirm="isDeleting ? 'Deleting' : 'Delete'"
        :function-cancel="deselectDraftNote"
        :function-confirm="deleteDraftNote"
        modal-header="Are you sure?"
        :show-modal="!!selectedDraftNote && activeOperation === 'delete'"
      >
        {{ deleteModalBodyText }}
      </AreYouSureModal>
    </div>
    <EditBatchNoteModal
      v-model="showEditModal"
      initial-mode="editDraft"
      :note-id="get(selectedDraftNote, 'id')"
      :on-close="afterEditDraft"
      :sid="get(selectedDraftNote, 'sid')"
    />
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal'
import TimelineDate from '@/components/student/profile/TimelineDate'
import {alertScreenReader, studentRoutePath} from '@/lib/utils'
import {computed, onUnmounted} from 'vue'
import {deleteNote, getMyDraftNotes} from '@/api/notes'
import {each, find, get, size, trim} from 'lodash'
import {mdiPaperclip, mdiTrashCan} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const headers = [
  {align: 'start', key: 'student', title: 'Student', width: 200},
  {align: 'start', key: 'sid', title: 'SID', width: 150},
  {align: 'start', key: 'subject', title: 'Subject'}
]
if (currentUser.isAdmin) {
  headers.push({align: 'start', key: 'author', title: 'Author', width: 200})
}
headers.push(
  {align: 'start', key: 'updatedAt', title: 'Date', width: 100},
  {align: 'center', key: 'delete', title: 'Delete', width: 100}
)

let activeOperation
let isDeleting = false
let myDraftNotes = undefined
let selectedDraftNote = undefined

const afterEditDraft = data => {
  const existing = find(myDraftNotes, ['id', data.id])
  if (existing) {
    Object.assign(existing, data)
    reloadDraftNotes().then(deselectDraftNote)
  } else {
    deselectDraftNote()
  }
}

const deleteDraftNote = () => {
  return new Promise(resolve => {
    isDeleting = true
    deleteNote(selectedDraftNote).then(() => {
      reloadDraftNotes('Draft note deleted').then(() => {
        deselectDraftNote()
        isDeleting = false
        resolve()
      })
    })
  })
}

const deselectDraftNote = () => {
  console.log('deselectDraftNote')
  selectedDraftNote = activeOperation = null
}

const onDeleteNote = noteId => {
  if (find(myDraftNotes, ['id', noteId])) {
    reloadDraftNotes()
  }
}

const onUpdateNote = note => {
  if (find(myDraftNotes, ['id', note.id])) {
    reloadDraftNotes()
  }
}

const openDeleteModal = draftNote => {
  activeOperation = 'delete'
  selectedDraftNote = draftNote
  alertScreenReader('Please confirm draft note deletion.')
}

const openEditModal = noteDraft => {
  activeOperation = 'edit'
  selectedDraftNote = noteDraft
}

const deleteModalBodyText = computed(() => {
  let message
  if (selectedDraftNote) {
    const student = selectedDraftNote.student
    const style = currentUser.inDemoMode ? 'demo-mode-blur' : ''
    message = 'Please confirm the deletion of the draft note '
    message += student ? `for <b class="${style}">${student.firstName} ${student.lastName}</b>.` : `with subject ${selectedDraftNote.subject}.`
  }
  return message
})

const reloadDraftNotes = () => {
  return getMyDraftNotes().then(data => myDraftNotes = data)
}

const showEditModal = computed({
  get() {
    return !!selectedDraftNote && activeOperation === 'edit'
  },
  set(value) {
    !value && deselectDraftNote()
  }
})

const eventHandlers = {
  'note-created': reloadDraftNotes,
  'note-deleted': onDeleteNote,
  'note-updated': onUpdateNote
}
each(eventHandlers, (handler, eventType) => contextStore.setEventHandler(eventType, handler))

reloadDraftNotes().then(() => contextStore.loadingComplete('Draft notes list is ready.'))

onUnmounted(() => {
  each(eventHandlers || {}, (handler, eventType) => contextStore.removeEventHandler(eventType, handler))
})
</script>

<style>
tbody tr:nth-of-type(odd) {
 background-color: rgba(0, 0, 0, .05);
}
.data-table-header-cell {
  font-size: 14px;
  font-weight: bold;
  height: 32px !important;
}
</style>
