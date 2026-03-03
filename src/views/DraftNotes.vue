<template>
  <div class="default-margins">
    <h1 id="page-header" class="my-5">{{ currentUser.isAdmin ? 'Draft Notes' : 'My Draft Notes' }}</h1>
    <div v-if="!contextStore.loading">
      <div v-if="size(myDraftNotes)">
        <div v-if="!currentUser.isAdmin" class="mb-4 mt-1">
          A draft note is only visible to its author.
        </div>
        <v-data-table
          id="draft-notes-table"
          v-table-caption="tableCaption"
          :cell-props="data => {
            const classes = ['font-size-16', 'vertical-baseline']
            if (data.column.key === 'subject') {
              classes.push('subject-cell')
            }
            return {
              class: classes.join(' '),
              'data-label': data.column.title,
              id: `draft-note-${data.item.id}-column-${data.column.key}`
            }
          }"
          class="table-striped"
          :class="{'stacked-table': isStacked}"
          :hide-default-header="isStacked"
          disable-sort
          :headers="headers"
          :header-props="{class: 'data-table-header-cell', tabindex: undefined}"
          hide-default-footer
          hide-no-data
          :items="myDraftNotes || []"
          :items-per-page="-1"
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
              <span aria-hidden="true">&mdash;</span>
              <span class="sr-only">blank</span>
            </span>
          </template>
          <template #item.sid="{item}">
            <span :class="{'demo-mode-blur': currentUser.inDemoMode}">
              <span aria-hidden="true">{{ item.sid || '&mdash;' }}</span>
              <span class="sr-only">{{ item.sid || 'blank' }}</span>
            </span>
          </template>
          <template #item.subject="{ item, index }">
            <div class="d-flex align-center flex-wrap subject-content">
              <span
                v-if="item.author.uid !== currentUser.uid"
                class="font-size-16"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
              >
                <span :class="{'text-medium-emphasis': !trim(item.subject)}">
                  {{ trim(item.subject) || config.draftNoteSubjectPlaceholder }}
                </span>
              </span>

              <v-btn
                v-if="item.author.uid === currentUser.uid"
                :id="`open-draft-note-${item.id}`"
                :aria-label="editNoteAriaLabel(item, index)"
                class="mr-1 px-0 py-2 text-left text-primary subject-btn"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
                size="lg"
                :title="draftNoteLabel(item)"
                variant="text"
                @click="() => openEditDialog(item)"
              >
                <span class="subject-btn-text">
                  {{ item.subject.length > lengthTruncateButtonText
                    ? truncate(draftNoteLabel(item), {length: lengthTruncateButtonText})
                    : draftNoteLabel(item)
                  }}
                </span>
              </v-btn>

              <span v-if="item.attachmentCount" class="ml-1">
                <span class="sr-only">Has attachment(s)</span>
                <v-icon class="mb-1" :icon="mdiPaperclip" size="small" />
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
          <template #item.delete="{ item, index }">
            <v-btn
              :id="`delete-draft-note-${item.id}`"
              class="align-self-center bg-transparent text-error"
              :disabled="isDeleteDialogOpen || isDeleting || isEditDialogOpen"
              :icon="mdiTrashCan"
              size="md"
              :aria-label="deleteNoteAriaLabel(item, index)"
              :title="`Delete ${draftNoteLabel(item)}`"
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
  </div>
</template>

<script setup>
import {computed, onBeforeUnmount, onMounted, ref, watch} from 'vue'
import {DateTime} from 'luxon'
import {each, find, findIndex, get, size, trim, truncate} from 'lodash'
import {mdiPaperclip, mdiTrashCan} from '@mdi/js'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal'
import TimelineDate from '@/components/student/profile/TimelineDate'
import vuetify from '@/plugins/vuetify'
import {alertScreenReader, putFocusNextTick, studentRoutePath} from '@/lib/utils'
import {deleteNote, getMyDraftNotes} from '@/api/notes'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const contextStore = useContextStore()
const noteStore = useNoteStore()
const config = contextStore.config
const currentUser = contextStore.currentUser
const eventHandlers = {
  'note-created': () => {
    reloadDraftNotes()
  },
  'note-deleted': noteId => find(myDraftNotes.value, ['id', noteId]) && reloadDraftNotes(),
  'note-updated': note => {
    if (find(myDraftNotes.value, ['id', note.id])) {
      reloadDraftNotes()
    }
  }
}
const isDeleteDialogOpen = ref(false)
const isEditDialogOpen = ref(false)
const isDeleting = ref(false)
const mobileBreakpoint = 800
const myDraftNotes = ref(undefined)
const selectedNote = ref(undefined)

const isStacked = computed(() => vuetify.display.width.value <= mobileBreakpoint)

const lengthTruncateButtonText = computed(() => vuetify.display.lgAndUp.value ? 60 : (vuetify.display.mdAndUp.value ? 30 : 16))

const draftNotesCount = computed(() => size(myDraftNotes.value) || 0)

const tableCaption = computed(() => currentUser.isAdmin ? 'Draft Notes' : 'My Draft Notes')

const headers = computed(() => {
  const isLg = vuetify.display.lgAndUp.value

  const cols = [
    {align: 'start', key: 'student', title: 'Student', width: isLg ? 220 : 170},
    {align: 'start', ariaLabel: 'S I D', key: 'sid', title: 'SID', width: isLg ? 150 : 120},
    {align: 'start', key: 'subject', title: 'Subject'}
  ]

  if (currentUser.isAdmin) {
    cols.push({align: 'start', key: 'author', title: 'Author', width: isLg ? 200 : 160})
  }

  cols.push(
    {align: 'start', key: 'updatedAt', title: 'Date', width: isLg ? 135 : 115},
    {align: 'center', key: 'delete', title: 'Delete', width: isLg ? 100 : 84}
  )

  return cols
})

const draftNoteLabel = note => trim(note?.subject) || config.draftNoteSubjectPlaceholder

const editNoteAriaLabel = (note, index) =>
  `Edit note ${index + 1} of ${draftNotesCount.value}: ${draftNoteLabel(note)}`

const deleteNoteAriaLabel = (note, index) =>
  `Delete note ${index + 1} of ${draftNotesCount.value}: ${draftNoteLabel(note)}`

contextStore.loadingStart()

watch(() => noteStore.isSaving, (newValue, oldValue) => {
  if (newValue === false && oldValue === true) {
    reloadDraftNotes()
  }
})

onMounted(() => {
  getMyDraftNotes().then(data => {
    myDraftNotes.value = data
    contextStore.loadingComplete()
    each(eventHandlers, (handler, eventType) => contextStore.setEventHandler(eventType, handler))
  })
})

onBeforeUnmount(() => each(eventHandlers, (handler, eventType) => contextStore.removeEventHandler(eventType, handler)))

const afterEditDraft = () => {
  isEditDialogOpen.value = false
  putFocusNextTick(`open-draft-note-${selectedNote.value.id}`)
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

  const selectedNoteId = selectedNote.value.id
  const selectedNoteIndex = findIndex(myDraftNotes.value, {id: selectedNoteId})

  isDeleting.value = true

  deleteNote(selectedNoteId).then(() => {
    myDraftNotes.value.splice(selectedNoteIndex, 1)

    const newLength = size(myDraftNotes.value)
    const focusIndex = newLength ? Math.min(selectedNoteIndex, newLength - 1) : -1
    const focusNote = focusIndex >= 0 ? myDraftNotes.value[focusIndex] : null

    isDeleting.value = false
    isDeleteDialogOpen.value = false

    alertScreenReader('Draft note deleted')
    putFocusNextTick(focusNote ? `delete-draft-note-${focusNote.id}` : 'draft-notes-no-data')
  })
}
const formatFromISO = isoDate => {
  const date = DateTime.fromISO(isoDate).setZone(config.timezone)
  return date.toFormat(date.year === DateTime.now().year ? 'MMM d' : 'MMM d, yyyy')
}

const openDeleteDialog = draftNote => {
  selectedNote.value = draftNote
  isDeleteDialogOpen.value = true
}

const openEditDialog = noteDraft => {
  isEditDialogOpen.value = true
  selectedNote.value = noteDraft
}

const reloadDraftNotes = () => getMyDraftNotes().then(data => myDraftNotes.value = data)
</script>

<style>
.data-table-header-cell {
  font-size: 14px;
  font-weight: bold;
  height: 32px !important;
}

.data-table-header-cell {
  font-size: 14px;
  font-weight: bold;
  height: 32px !important;
}

#draft-notes-table .v-table__wrapper {
  overflow-x: auto;
}

#draft-notes-table .v-table__wrapper > table {
  table-layout: fixed;
  width: 100%;
}

#draft-notes-table td,
#draft-notes-table th {
  overflow: hidden;
}

#draft-notes-table .subject-cell {
  overflow-wrap: anywhere;
}

#draft-notes-table .subject-content {
  min-width: 0;
  gap: 4px;
}

#draft-notes-table .subject-btn {
  max-width: 100%;
  height: auto;
  justify-content: flex-start;
  text-align: left;
  white-space: normal;
  min-width: 0;
}

#draft-notes-table .subject-btn .v-btn__content {
  width: 100%;
  white-space: normal;
}

#draft-notes-table .subject-btn-text {
  overflow-wrap: anywhere;
}

#draft-notes-table.stacked-table .v-table__wrapper tbody tr > td {
  display: block !important;
  width: 100% !important;
  text-align: left !important;
  padding-top: 10px;
  padding-bottom: 10px;
}

#draft-notes-table.stacked-table .v-table__wrapper tbody tr > td::before {
  content: attr(data-label);
  display: block;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 4px;
  opacity: 0.75;
}

</style>
