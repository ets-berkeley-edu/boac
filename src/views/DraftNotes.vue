<template>
  <div class="default-margins">
    <h1 class="my-5">{{ currentUser.isAdmin ? 'Draft Notes' : 'My Draft Notes' }}</h1>
    <div v-if="!contextStore.loading">
      <div v-if="size(myDraftNotes)">
        <div v-if="!currentUser.isAdmin" class="mb-4 mt-1">
          A draft note is only visible to its author.
        </div>
        <v-data-table
          id="responsive-data-table"
          :cell-props="{
            class: 'font-size-16 vertical-baseline',
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
            <div class="align-center overflow-wrap-break-word">
              <span
                v-if="item.author.uid !== currentUser.uid"
                class="font-size-16"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
              >
                {{ trim(item.subject) || config.draftNoteSubjectPlaceholder }}
              </span>
              <v-btn
                v-if="item.author.uid === currentUser.uid"
                :id="`open-draft-note-${item.id}`"
                class="pl-0 py-2 text-left text-primary"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
                size="lg"
                variant="text"
                @click="() => openEditDialog(item)"
              >
                <div v-if="item.subject.length <= lengthTruncateButtonText" class="align-start">
                  {{ trim(item.subject) || config.draftNoteSubjectPlaceholder }}
                </div>
                <div v-if="item.subject.length > lengthTruncateButtonText" class="align-start">
                  {{ truncate(trim(item.subject), {length: lengthTruncateButtonText}) }}
                </div>
              </v-btn>
              <span v-if="item.attachmentCount">
                <span class="sr-only">Has attachment(s)</span>
                <v-icon class="mb-1 ml-1" :icon="mdiPaperclip" size="small" />
              </span>
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
            <v-btn
              :id="`delete-draft-note-${item.id}`"
              aria-label="Delete"
              class="bg-transparent text-error"
              :disabled="isDeleteDialogOpen || isDeleting || isEditDialogOpen"
              :icon="mdiTrashCan"
              size="md"
              title="Delete"
              variant="flat"
              @click="() => openDeleteDialog(item)"
            />
          </template>
        </v-data-table>
      </div>
      <div
        v-if="!size(myDraftNotes)"
        id="draft-notes-no-data"
        tabindex="-1"
      >
        {{ currentUser.isAdmin ? 'No' : 'You have no' }} saved drafts.
      </div>
    </div>
  </div>
  <AreYouSureModal
    v-model="isDeleteDialogOpen"
    :button-label-confirm="isDeleting ? 'Deleting' : 'Delete'"
    :function-cancel="cancel"
    :function-confirm="deleteDraftNote"
    modal-header="Are you sure?"
  >
    <span v-if="selectedNote">
      <span v-if="selectedNote.student">
        Delete draft note for
        <span class="font-weight-medium" :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ selectedNote.student.firstName }} {{ selectedNote.student.lastName }}</span>.
      </span>
      <span v-if="!selectedNote.student && selectedNote.subject">
        Delete draft note with subject "<span class="font-weight-medium">{{ selectedNote.subject }}</span>".
      </span>
      <span v-if="!selectedNote.student && !selectedNote.subject">
        Delete draft note created on {{ formatFromISO(selectedNote.createdAt) }}.
      </span>
    </span>
  </AreYouSureModal>
  <EditBatchNoteModal
    v-model="isEditDialogOpen"
    initial-mode="editDraft"
    :note-id="get(selectedNote, 'id')"
    :on-close="afterEditDraft"
    :sid="get(selectedNote, 'sid')"
  />
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal'
import TimelineDate from '@/components/student/profile/TimelineDate'
import vuetify from '@/plugins/vuetify'
import {alertScreenReader, putFocusNextTick, studentRoutePath} from '@/lib/utils'
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {DateTime} from 'luxon'
import {deleteNote, getMyDraftNotes} from '@/api/notes'
import {each, find, findIndex, get, size, trim, truncate} from 'lodash'
import {mdiPaperclip, mdiTrashCan} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const config = contextStore.config
const currentUser = contextStore.currentUser
const eventHandlers = {
  'note-created': note => {
    reloadDraftNotes().then(() => putFocusNextTick(`open-draft-note-${note.id}`))
  },
  'note-deleted': noteId => find(myDraftNotes.value, ['id', noteId]) && reloadDraftNotes(),
  'note-updated': note => {
    if (find(myDraftNotes.value, ['id', note.id])) {
      reloadDraftNotes().then(() => putFocusNextTick(`open-draft-note-${note.id}`))
    }
  }
}
const headers = []
const isDeleteDialogOpen = ref(false)
const isEditDialogOpen = ref(false)
const isDeleting = ref(false)
const lengthTruncateButtonText = computed(() => vuetify.display.lgAndUp.value ? 60 : (vuetify.display.lgAndUp.value ? 50 : 30))
const myDraftNotes = ref(undefined)
const selectedNote = ref(undefined)

onMounted(() => {
  contextStore.loadingStart()
  headers.push(
    {align: 'start', key: 'student', title: 'Student', width: 200},
    {align: 'start', key: 'sid', title: 'SID', width: 150},
    {align: 'start', key: 'subject', title: 'Subject'}
  )
  if (currentUser.isAdmin) {
    headers.push({align: 'start', key: 'author', title: 'Author', width: 200})
  }
  headers.push(
    {align: 'start', key: 'updatedAt', title: 'Date', width: 100},
    {align: 'center', key: 'delete', title: 'Delete', width: 100}
  )
  getMyDraftNotes().then(data => {
    myDraftNotes.value = data
    contextStore.loadingComplete('Draft notes list is ready.')
    each(eventHandlers, (handler, eventType) => contextStore.setEventHandler(eventType, handler))
  })
})

onUnmounted(() => each(eventHandlers, (handler, eventType) => contextStore.removeEventHandler(eventType, handler)))

const afterEditDraft = () => {
  isEditDialogOpen.value = false
}

const cancel = () => {
  const noteId = selectedNote.value.id
  isDeleteDialogOpen.value = isEditDialogOpen.value = false
  selectedNote.value = undefined
  alertScreenReader('Canceled')
  putFocusNextTick(`delete-draft-note-${noteId}`)
}

const deleteDraftNote = () => {
  alertScreenReader('Deleting draft note')
  return new Promise(resolve => {
    const selectedNoteIndex = findIndex(myDraftNotes.value, {'id': selectedNote.value.id})
    const nextNote = get(myDraftNotes.value, selectedNoteIndex >= (size(myDraftNotes.value) - 1) ? 0 : selectedNoteIndex + 1)
    isDeleting.value = true
    deleteNote(selectedNote.value).then(() => {
      myDraftNotes.value.splice(selectedNoteIndex, 1)
      isDeleting.value = isDeleteDialogOpen.value = false
      alertScreenReader('Draft note deleted')
      putFocusNextTick(nextNote ? `delete-draft-note-${nextNote.id}` : 'draft-notes-no-data')
      resolve()
    })
  })
}

const formatFromISO = isoDate => {
  const date = DateTime.fromISO(isoDate).setZone(config.timezone)
  return date.toFormat(date.year === DateTime.now().year ? 'MMM d' : 'MMM d, yyyy')
}

const openDeleteDialog = draftNote => {
  selectedNote.value = draftNote
  isDeleteDialogOpen.value = true
  alertScreenReader('Please confirm draft note deletion.')
}

const openEditDialog = noteDraft => {
  isEditDialogOpen.value = true
  selectedNote.value = noteDraft
}

const reloadDraftNotes = () => getMyDraftNotes().then(data => myDraftNotes.value = data)
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
