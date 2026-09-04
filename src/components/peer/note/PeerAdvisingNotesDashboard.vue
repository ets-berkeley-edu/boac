<template>
  <div>
    <div class="align-start d-flex flex-wrap justify-space-between px-4">
      <div
        class="w-100"
        :class="{'d-flex align-start justify-space-between': inlineNotesCount}"
      >
        <div>
          <component :is="headingTag" id="page-header" class="mb-0 mr-4">Peer Advising Notes</component>
          <div v-if="!hideDepartmentName">{{ get(peerAdvisingDepartment, 'name') }}</div>
        </div>
        <div
          v-if="inlineNotesCount && totalNoteCount"
          id="notes-description"
          class="inline-notes-description ml-4 text-no-wrap"
        >
          {{ notesDescription }}
        </div>
      </div>
      <div v-if="!hideCreateNoteButton && !currentUser.isAdmin" class="d-flex flex-grow-1">
        <v-btn
          id="peer-advisor-create-note-button"
          class="px-10 ml-auto"
          color="primary"
          :disabled="!!noteStore.mode"
          :prepend-icon="mdiFileDocument"
          text="New Note"
          @click="onClickCreateNote"
        />
        <EditPeerAdvisingNoteModal
          v-if="peerAdvisingDepartment"
          v-model="createNoteModal"
          :peer-advising-department-id="peerAdvisingDepartment.id"
        />
      </div>
    </div>
    <div
      v-if="!hideMyNotesToggle || (!inlineNotesCount && totalNoteCount)"
      class="align-center d-flex flex-wrap justify-space-between mt-2 px-4"
    >
      <ShowMyPeerAdvisingNotesToggle
        v-if="!hideMyNotesToggle && (showMyNotesOnly || isFetchingNotes || notes.length)"
        v-model="showMyNotesOnly"
        :is-fetching-notes="isFetchingNotes"
      />
      <div v-if="!inlineNotesCount && totalNoteCount" id="notes-description">
        {{ notesDescription }}
      </div>
    </div>
    <div v-if="!isFetchingNotes && !totalNoteCount" class="mt-5 px-4">
      {{ notesDescription }}
    </div>
    <div class="w-100">
      <PeerAdvisingNotesTable
        :key="totalNoteCount"
        :notes="notes"
        :is-fetching-notes="isFetchingNotes"
      >
        <template #noData>
          <div class="d-flex align-center">
            <template v-if="!hideCreateNoteButton">
              {{ showMyNotesOnly ? 'You currently have' : 'There are currently' }} no student notes.
              Would you like to
              <v-btn
                id="peer-advisor-create-note-link"
                class="font-size-15 px-1 mx-1"
                color="anchor"
                variant="text"
                @click="onClickCreateNote"
              >
                make your first note<span class="text-black text-decoration-none">?</span>
              </v-btn>
            </template>
            <template v-else>
              There are currently no student notes.
            </template>
          </div>
        </template>
      </PeerAdvisingNotesTable>
      <div class="py-3 text-center">
        <v-btn
          v-if="notes.length && totalNoteCount > notes.length"
          id="fetch-more-notes"
          :disabled="isFetchingNotes"
          text="Show additional advising notes"
          variant="text"
          @click.prevent="onClickShowMore"
        />
        <SectionSpinner v-if="notes.length" :loading="isFetchingNotes" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {Handler} from 'mitt'
import type {PropType} from 'vue'
import {findIndex, get, last, orderBy} from 'lodash'
import {mdiFileDocument} from '@mdi/js'
import {computed, onMounted, onUnmounted, ref, watch} from 'vue'
import type {BasicStudent, Note, NoteComment, PeerAdvisingDepartment} from '@/lib/types'
import EditPeerAdvisingNoteModal from '@/components/peer/note/EditPeerAdvisingNoteModal.vue'
import PeerAdvisingNotesTable from '@/components/peer/note/PeerAdvisingNotesTable.vue'
import SectionSpinner from '@/components/util/SectionSpinner.vue'
import ShowMyPeerAdvisingNotesToggle from '@/components/peer/note/ShowMyPeerAdvisingNotesToggle.vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {getBasicStudent} from '@/api/peer-advising-users'
import {getDefaultModel} from '@/stores/note-edit-session/note-edit-session-utils'
import {mergePeerAdvisingNoteUpdate, updateNoteComments} from '@/lib/note'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const LIMIT_PER_FETCH = 50

const props = defineProps({
  fetchNotes: {
    required: true,
    type: Function as PropType<(offset: number, limit: number, showMyNotesOnly?: boolean) => Promise<{notes: Note[], totalNoteCount: number}>>
  },
  headingTag: {
    default: 'h1',
    type: String
  },
  hideCreateNoteButton: {
    type: Boolean
  },
  hideDepartmentName: {
    type: Boolean
  },
  hideMyNotesToggle: {
    type: Boolean
  },
  inlineNotesCount: {
    type: Boolean
  },
  peerAdvisingDepartment: {
    default: undefined,
    type: Object as PropType<PeerAdvisingDepartment>
  }
})

const emit = defineEmits(['ready'])

const contextStore = useContextStore()
const createNoteModal = ref(false)
const currentUser = contextStore.currentUser
const isFetchingNotes = ref(false)
const noteStore = useNoteStore()
const notes = ref<Note[]>([])
const totalNoteCount = ref(0)
const showMyNotesOnly = ref(false)

watch(showMyNotesOnly, async () => {
  isFetchingNotes.value = true
  await loadNotes()
  const filterPhrase = showMyNotesOnly.value ? 'Showing Your Notes.' : 'Showing All Notes.'
  alertScreenReader(`${filterPhrase} ${notesDescription.value}`)
  putFocusNextTick('my-notes-only-toggle')
})

onMounted(() => {
  isFetchingNotes.value = true
  loadNotes().then(() => {
    contextStore.setEventHandler('peer-advising-note-created', onPeerAdvisingNoteCreated)
    contextStore.setEventHandler('note-updated', onPeerAdvisingNoteUpdated)
    contextStore.setEventHandler('note-deleted', onNoteDeleted)
    emit('ready')
    putFocusNextTick('page-header')
  })
})

onUnmounted(() => {
  contextStore.removeEventHandler('peer-advising-note-created', onPeerAdvisingNoteCreated)
  contextStore.removeEventHandler('note-updated', onPeerAdvisingNoteUpdated)
  contextStore.removeEventHandler('note-deleted', onNoteDeleted)
  noteStore.exitSession()
})

const notesDescription = computed(() => {
  if (notes.value.length < totalNoteCount.value) {
    return `Showing ${notes.value.length} of ${totalNoteCount.value} notes.`
  }
  return `Showing all ${notes.value.length} notes.`
})

const loadNotes = (offset?: number) => {
  return new Promise<void>(resolve => {
    props.fetchNotes(offset || 0, LIMIT_PER_FETCH, showMyNotesOnly.value).then(data => {
      if (!offset) {
        notes.value = []
      }
      notes.value = sortNotes([...notes.value, ...data.notes])
      totalNoteCount.value = data.totalNoteCount
      isFetchingNotes.value = false
      resolve()
    })
  })
}

const onClickCreateNote = () => {
  noteStore.exitSession()
  const note = getDefaultModel()
  note.subject = ''
  note.peerAdvisingDepartmentId = get(props.peerAdvisingDepartment, 'id')
  noteStore.setModel(note)
  noteStore.setMode('createPeerAdvisorNote')
  createNoteModal.value = true
  noteStore.setIsCreateNoteModalOpen(true)
}

const onClickShowMore = () => {
  alertScreenReader('Loading additional notes')
  isFetchingNotes.value = true
  loadNotes(notes.value.length).then(() => {
    alertScreenReader(notesDescription.value)
    if (totalNoteCount.value > notes.value.length) {
      putFocusNextTick('fetch-more-notes')
    } else {
      putFocusNextTick(`peer-advisor-note-${get(last(notes.value), 'id')}`)
    }
    isFetchingNotes.value = false
  })
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const onPeerAdvisingNoteCreated: Handler<any> = (note: Note) => {
  getBasicStudent(note.sid).then((student: BasicStudent) => {
    note.student = student
    notes.value.unshift(note)
    totalNoteCount.value += 1
  })
}

const onPeerAdvisingNoteUpdated = (note: Note|NoteComment) => {
  const noteId = note.parentNoteId || note.id
  const existingNoteIndex = findIndex(notes.value, {'id': noteId})
  if (existingNoteIndex > -1) {
    if (note.parentNoteId) {
      const parentNote = notes.value[existingNoteIndex]
      if (parentNote) {
        updateNoteComments(parentNote, note as NoteComment)
      } else {
        loadNotes()
      }
    } else {
      const existingNote = notes.value[existingNoteIndex]
      notes.value.splice(existingNoteIndex, 1, mergePeerAdvisingNoteUpdate(existingNote, note as Note))
      notes.value = sortNotes(notes.value)
    }
  } else {
    loadNotes()
  }
}

const onNoteDeleted = () => {
  loadNotes()
}

const sortNotes = (notesToSort: Note[]) => {
  return orderBy(notesToSort, n => n.updatedAt || n.createdAt, ['desc'])
}
</script>

<style scoped>
.inline-notes-description {
  margin-top: 7px;
}
</style>
