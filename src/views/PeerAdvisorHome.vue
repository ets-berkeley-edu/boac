<template>
  <div v-if="!contextStore.loading" class="pt-6 px-2 px-sm-2 px-md-8">
    <div class="align-start d-flex flex-wrap justify-space-between px-4">
      <div>
        <h1 id="page-header" class="mb-0 mr-4">Peer Advising Notes</h1>
        <div>{{ get(peerAdvisingDepartment, 'name') }}</div>
      </div>
      <div v-if="!currentUser.isAdmin" class="d-flex flex-grow-1">
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
    <div class="align-center d-flex flex-wrap justify-space-between mt-2 px-4">
      <ShowMyPeerAdvisingNotesToggle
        v-if="showMyNotesOnly || isFetchingNotes || notes.length"
        v-model="showMyNotesOnly"
        :is-fetching-notes="isFetchingNotes"
      />
      <div v-if="!isFetchingNotes && totalNoteCount" id="notes-description">
        {{ notesDescription }}
      </div>
    </div>
    <div v-if="!isFetchingNotes && !totalNoteCount" class="mt-5">
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
import {findIndex, get, last, orderBy} from 'lodash'
import {mdiFileDocument} from '@mdi/js'
import {computed, onMounted, onUnmounted, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import type {BasicStudent, BoaUser, Note, NoteComment, PeerAdvisingDepartment} from '@/lib/types'
import EditPeerAdvisingNoteModal from '@/components/peer/note/EditPeerAdvisingNoteModal.vue'
import PeerAdvisingNotesTable from '@/components/peer/note/PeerAdvisingNotesTable.vue'
import SectionSpinner from '@/components/util/SectionSpinner.vue'
import ShowMyPeerAdvisingNotesToggle from '@/components/peer/note/ShowMyPeerAdvisingNotesToggle.vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {getBasicStudent} from '@/api/peer-advising-users'
import {getDefaultModel} from '@/stores/note-edit-session/note-edit-session-utils'
import {findPeerAdvisingDepartment, getPeerAdvisorDepartmentMemberships} from '@/lib/berkeley-department'
import {getPeerAdvisorNotes} from '@/api/peer-advising-notes'
import {getUserByUid} from '@/api/user'
import {mergePeerAdvisingNoteUpdate, updateNoteComments} from '@/lib/note'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const LIMIT_PER_FETCH = 50

const contextStore = useContextStore()
const createNoteModal = ref(false)
const currentUser = contextStore.currentUser
const isFetchingNotes = ref(false)
const noteStore = useNoteStore()
const notes = ref<Note[]>([])
const peerAdvisingDepartment = ref<PeerAdvisingDepartment | undefined>()
const peerAdvisor = ref<BoaUser>()
const route = useRoute()
const router = useRouter()
const totalNoteCount = ref(0)
const showMyNotesOnly = ref(false)

watch(showMyNotesOnly, async () => {
  isFetchingNotes.value = true
  // fetch fresh data filtered by the new switch state
  await fetchNotes()
  const filterPhrase = showMyNotesOnly.value ? 'Showing Your Notes.' : 'Showing All Notes.'
  alertScreenReader(`${filterPhrase} ${notesDescription.value}`)
  putFocusNextTick('my-notes-only-toggle')
})

contextStore.loadingStart()

onMounted(() => {
  const currentUser = contextStore.currentUser
  if (currentUser.isAdmin) {
    const uid = route.params.uid.toString()
    getUserByUid(uid, false).then(init)
  } else {
    init(currentUser)
  }
})

onUnmounted(() => {
  contextStore.removeEventHandler('peer-advising-note-created')
  contextStore.removeEventHandler('note-updated')
  noteStore.exitSession()
})

const notesDescription = computed(() => {
  if (notes.value.length < totalNoteCount.value) {
    return `Showing ${notes.value.length} of ${totalNoteCount.value} notes.`
  }
  return `Showing all ${notes.value.length} notes.`
})

const fetchNotes = (offset) => {
  return new Promise<void>(resolve => {
    if (peerAdvisor.value && peerAdvisor.value.uid) {
      getPeerAdvisorNotes(
        offset || 0,
        LIMIT_PER_FETCH,
        peerAdvisor.value.uid,
        true,
        showMyNotesOnly.value
      ).then(data => {
        if (!offset) {
          notes.value = []
        }
        notes.value = sortNotes([...notes.value, ...data.notes])
        totalNoteCount.value = data.totalNoteCount
        isFetchingNotes.value = false
        resolve()
      })
    } else {
      throw Error('Not Found')
    }
  })
}

const init = (user: BoaUser) => {
  peerAdvisor.value = user
  // Peer Advisors can belong to one and only one Peer Advising Department.
  const memberships = getPeerAdvisorDepartmentMemberships(peerAdvisor.value, 'peer_advisor')
  const peerAdvisingDepartmentId = memberships.length ? memberships[0].peerAdvisingDepartmentId : undefined
  peerAdvisingDepartment.value = peerAdvisingDepartmentId ? findPeerAdvisingDepartment(peerAdvisingDepartmentId) : undefined
  if (peerAdvisor.value.id && peerAdvisingDepartment) {
    fetchNotes().then(() => {
      contextStore.loadingComplete()
      contextStore.setEventHandler('peer-advising-note-created', onPeerAdvisingNoteCreated)
      contextStore.setEventHandler('note-updated', onPeerAdvisingNoteUpdated)
    })
  } else {
    router.push({path: '/404'})
  }
}

const onClickCreateNote = () => {
  noteStore.exitSession()
  const note = getDefaultModel()
  // Peer Advisors do not provide note.subject thus subject is set to empty string to satisfy not-null db constraints.
  note.subject = ''
  note.peerAdvisingDepartmentId = get(peerAdvisingDepartment.value, 'id')
  noteStore.setModel(note)
  noteStore.setMode('createPeerAdvisorNote')
  createNoteModal.value = true
  noteStore.setIsCreateNoteModalOpen(true)
}

const onClickShowMore = () => {
  alertScreenReader('Loading additional notes')
  isFetchingNotes.value = true
  fetchNotes(notes.value.length).then(() => {
    alertScreenReader(notesDescription.value)
    if (totalNoteCount.value > notes.value.length) {
      // Keep focus on the "Show additional advising notes" button while it remains available.
      putFocusNextTick('fetch-more-notes')
    } else {
      // Once the button is gone (all notes are visible), move focus to the last note row.
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
        fetchNotes()
      }
    } else {
      const existingNote = notes.value[existingNoteIndex]
      notes.value.splice(existingNoteIndex, 1, mergePeerAdvisingNoteUpdate(existingNote, note as Note))
      notes.value = sortNotes(notes.value)
    }
  } else {
    fetchNotes()
  }
}

const sortNotes = notes => {
  return orderBy(notes, n => n.updatedAt || n.createdAt, ['desc'])

}
</script>
