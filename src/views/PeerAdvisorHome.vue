<template>
  <div v-if="!contextStore.loading" class="mt-10 page-container">
    <div class="d-flex justify-space-between">
      <div>
        <h1>Peer Advising Notes</h1>
      </div>
      <div>
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
        />
      </div>
    </div>
    <div v-if="!isPaging">
      <PeerAdvisorPaginatedNotes
        :current-page="currentPage"
        :go-to-page="goToPage"
        :items-per-page="itemsPerPage"
        :notes="notes"
        :peer-advising-department-id="peerAdvisingDepartmentId"
        :total-note-count="totalNoteCount"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type {Handler} from 'mitt'
import {mdiFileDocument} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import EditPeerAdvisingNoteModal from '@/components/peer/note/EditPeerAdvisingNoteModal.vue'
import PeerAdvisorPaginatedNotes from '@/components/peer/note/PeerAdvisorPaginatedNotes.vue'
import {getPeerAdvisorDepartmentMembership} from '@/lib/berkeley-department'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'
import {putFocusNextTick} from '@/lib/utils'
import {getPeerAdvisorNotes} from '@/api/peer-advising-notes'
import type {BoaUser, Note} from '@/lib/types'
import {getDefaultModel} from '@/stores/note-edit-session/note-edit-session-utils'
import {getUserByUid} from '@/api/user'

const contextStore = useContextStore()
const createNoteModal = ref(false)
const currentPage = ref(1)
const isPaging = ref(false)
const itemsPerPage = ref(50)
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
    getUserByUid(uid, true).then(init)
  } else {
    init(currentUser)
  }
})

const goToPage = (page: number) => {
  return new Promise<void>(resolve => {
    if (peerAdvisor.value && peerAdvisor.value.uid) {
      isPaging.value = true
      currentPage.value = page
      offset.value = (page - 1) * itemsPerPage.value
      getPeerAdvisorNotes(
        offset.value,
        itemsPerPage.value,
        peerAdvisor.value.uid,
        true
      ).then(data => {
        notes.value = data.notes
        totalNoteCount.value = data.totalNoteCount
        isPaging.value = false
        putFocusNextTick(page > 1 ? `pagination-page-${page}` : 'page-header')
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
  if (peerAdvisor.value.id && membership.peerAdvisingDepartmentId) {
    peerAdvisingDepartmentId.value = membership.peerAdvisingDepartmentId
    goToPage(1).then(() => {
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
  notes.value.unshift(note)
}
</script>

<style scoped>
.page-container {
  margin-left: 12%;
  margin-right: 12%;
}
</style>
