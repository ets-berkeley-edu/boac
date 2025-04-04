<template>
  <div v-if="!contextStore.loading" class="mt-8 mx-16">
    <div class="d-flex flex-wrap justify-space-between">
      <div>
        <h1 class="mb-0">Peer Advising Notes</h1>
        <div v-if="notes.length < totalNoteCount">
          Showing {{ notes.length }} of {{ totalNoteCount }} notes.
        </div>
        <div v-if="totalNoteCount === notes.length">
          Showing all {{ notes.length }} notes.
        </div>
      </div>
      <div v-if="!currentUser.isAdmin">
        <v-btn
          id="peer-advisor-create-note-button"
          aria-labelledby="peer-advising-note-modal-header"
          class="px-10"
          color="primary"
          :disabled="!!noteStore.mode"
          :prepend-icon="mdiFileDocument"
          text="New Note"
          @click="onClickCreateNote"
        />
        <EditPeerAdvisingNoteModal
          v-if="noteStore.isCreateNoteModalOpen"
          v-model="createNoteModal"
          :peer-advising-department-id="peerAdvisingDepartmentId"
        />
      </div>
    </div>
    <div class="w=100">
      <PeerAdvisorPaginatedNotes
        :notes="notes"
        :on-click-create-note="onClickCreateNote"
        :peer-advising-department-id="peerAdvisingDepartmentId"
      />
      <div class="my-3 text-center">
        <v-btn
          v-if="totalNoteCount > notes.length"
          id="fetch-more-notes"
          text="Show additional advising notes"
          variant="text"
          @click.prevent="fetchNotes"
        />
        <SectionSpinner v-if="notes.length" :loading="isFetchingNotes" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {Handler} from 'mitt'
import {mdiFileDocument} from '@mdi/js'
import {onMounted, onUnmounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import type {BasicStudent, BoaUser, Note} from '@/lib/types'
import EditPeerAdvisingNoteModal from '@/components/peer/note/EditPeerAdvisingNoteModal.vue'
import {getBasicStudent} from '@/api/peer-advising-users'
import {getDefaultModel} from '@/stores/note-edit-session/note-edit-session-utils'
import {getPeerAdvisorDepartmentMembership} from '@/lib/berkeley-department'
import {getPeerAdvisorNotes} from '@/api/peer-advising-notes'
import {getUserByUid} from '@/api/user'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'
import PeerAdvisorPaginatedNotes from '@/components/peer/note/PeerAdvisorPaginatedNotes.vue'
import SectionSpinner from '@/components/util/SectionSpinner.vue'

const LIMIT_PER_FETCH = 50

const contextStore = useContextStore()
const createNoteModal = ref(false)
const currentUser = contextStore.currentUser
const isFetchingNotes = ref(false)
const noteStore = useNoteStore()
const notes = ref<Note[]>([])
const offset = ref(0)
const peerAdvisingDepartmentId = ref<number>(NaN)
const peerAdvisor = ref<BoaUser>()
const route = useRoute()
const router = useRouter()
const totalNoteCount = ref(0)

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
  noteStore.exitSession()
})

const fetchNotes = () => {
  return new Promise<void>(resolve => {
    if (peerAdvisor.value && peerAdvisor.value.uid) {
      isFetchingNotes.value = true
      offset.value = notes.value.length || 0
      getPeerAdvisorNotes(
        offset.value,
        LIMIT_PER_FETCH,
        peerAdvisor.value.uid,
        true
      ).then(data => {
        const putFocusId = offset.value === 0 ? 'page-header' : `tr-peer-advisor-${data.notes[0].id}`
        notes.value.push(...data.notes)
        totalNoteCount.value = data.totalNoteCount
        isFetchingNotes.value = false
        putFocusNextTick(putFocusId)
        resolve()
      })
    } else {
      throw Error('Not Found')
    }
  })
}

const init = (user: BoaUser) => {
  peerAdvisor.value = user
  const membership = getPeerAdvisorDepartmentMembership(peerAdvisor.value, 'peer_advisor')
  if (peerAdvisor.value.id && membership && membership.peerAdvisingDepartmentId) {
    peerAdvisingDepartmentId.value = membership.peerAdvisingDepartmentId
    fetchNotes().then(() => {
      contextStore.loadingComplete('Notes have loaded')
      contextStore.setEventHandler('peer-advising-note-created', onPeerAdvisingNoteCreated)
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
  note.peerAdvisingDepartmentId = peerAdvisingDepartmentId.value
  noteStore.setModel(note)
  noteStore.setMode('createPeerAdvisorNote')
  createNoteModal.value = true
  noteStore.setIsCreateNoteModalOpen(true)
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const onPeerAdvisingNoteCreated: Handler<any> = (note: Note) => {
  getBasicStudent(note.sid).then((student: BasicStudent) => {
    note.student = student
    notes.value.unshift(note)
  })
}
</script>
