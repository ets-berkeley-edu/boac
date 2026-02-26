<template>
  <div v-if="!contextStore.loading" class="pt-8 px-8 px-md-16">
    <div class="align-start d-flex flex-wrap justify-space-between">
      <div>
        <h1 id="page-header" class="mb-0">Peer Advising Notes</h1>
        <div>{{ get(peerAdvisingDepartment, 'name') }}</div>
      </div>
      <div v-if="!currentUser.isAdmin" class="d-flex align-end">
        <v-btn
          id="peer-advisor-create-note-button"
          class="px-10"
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
    <div class="align-center d-flex flex-wrap justify-space-between mt-2">
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
        :after-note-edit="fetchNotes"
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
import type {BasicStudent, BoaUser, Note, PeerAdvisingDepartment} from '@/lib/types'
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
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const LIMIT_PER_FETCH = 50

const contextStore = useContextStore()
const createNoteModal = ref(false)
const currentUser = contextStore.currentUser
const isFetchingNotes = ref(false)
const noteStore = useNoteStore()
const notes = ref<Note[]>([])
const offset = ref(0)
const peerAdvisingDepartment = ref<PeerAdvisingDepartment | undefined>()
const peerAdvisor = ref<BoaUser>()
const route = useRoute()
const router = useRouter()
const totalNoteCount = ref(0)
const showMyNotesOnly = ref(false)

watch(showMyNotesOnly, async () => {
  // clear out the old notes and set loading
  notes.value = []
  isFetchingNotes.value = true
  // fetch fresh data filtered by the new switch state
  await fetchNotes()
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

const fetchNotes = () => {
  return new Promise<void>(resolve => {
    if (peerAdvisor.value && peerAdvisor.value.uid) {
      offset.value = notes.value.length || 0
      getPeerAdvisorNotes(
        offset.value,
        LIMIT_PER_FETCH,
        peerAdvisor.value.uid,
        true,
        showMyNotesOnly.value
      ).then(data => {
        notes.value = orderBy([...notes.value, ...data.notes], n => n.updatedAt || n.createdAt, ['desc'])
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
      contextStore.setEventHandler('note-updated', data => {
        const note: Note = (data as Note)
        const index = findIndex(notes.value, {'id': note.id})
        if (index > -1) {
          note.peerAdvisingDepartment = notes.value[index].peerAdvisingDepartment
          notes.value[index] = note
        }
      })
      putFocusNextTick('page-header')
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
  fetchNotes().then(() => {
    alertScreenReader(notesDescription.value)
    putFocusNextTick(`tr-peer-advisor-note-${get(last(notes.value), 'id')}`)
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
</script>
