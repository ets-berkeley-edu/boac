<template>
  <div v-if="!contextStore.loading" class="pt-8 px-8 px-md-16">
    <div class="d-flex flex-wrap justify-space-between">
      <div>
        <h1 id="page-header" class="mb-0">Peer Advising Notes</h1>
        <div id="notes-description">
          <span v-if="!isFetchingNotes && notes.length">{{ notesDescription }}</span>
        </div>
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
          v-if="peerAdvisingDepartmentId"
          v-model="createNoteModal"
          :peer-advising-department-id="peerAdvisingDepartmentId"
        />
      </div>
    </div>
    <div class="w-100">
      <PeerAdvisingNotesTable :notes="notes">
        <template #studentName="{note}">
          <router-link
            v-if="currentUser.isAdmin"
            :id="`note-${note.id}-link-to-student`"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            :to="studentRoutePath(note.student.uid, currentUser.inDemoMode)"
          >
            {{ note.student ? lastNameFirst(note.student) : getStudentName(note) }}
          </router-link>
          <div v-if="!currentUser.isAdmin" class="text-medium-emphasis" :class="{'demo-mode-blur': currentUser.inDemoMode}">
            {{ getStudentName(note) }}
          </div>
        </template>
        <template #noData>
          <div class="d-flex align-center">
            There currently are no student notes. Would you like to
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
import {onMounted, onUnmounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import type {BasicStudent, BoaUser, Note} from '@/lib/types'
import EditPeerAdvisingNoteModal from '@/components/peer/note/EditPeerAdvisingNoteModal.vue'
import PeerAdvisingNotesTable from '@/components/peer/note/PeerAdvisingNotesTable.vue'
import SectionSpinner from '@/components/util/SectionSpinner.vue'
import {getBasicStudent} from '@/api/peer-advising-users'
import {getDefaultModel} from '@/stores/note-edit-session/note-edit-session-utils'
import {getPeerAdvisorDepartmentMemberships} from '@/lib/berkeley-department'
import {getPeerAdvisorNotes} from '@/api/peer-advising-notes'
import {getUserByUid} from '@/api/user'
import {alertScreenReader, lastNameFirst, putFocusNextTick, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const LIMIT_PER_FETCH = 50

const contextStore = useContextStore()
const createNoteModal = ref(false)
const currentUser = contextStore.currentUser
const isFetchingNotes = ref(false)
const noteStore = useNoteStore()
const notes = ref<Note[]>([])
const notesDescription = ref('')
const offset = ref(0)
const peerAdvisingDepartmentId = ref<number | undefined>()
const peerAdvisor = ref<BoaUser>()
const route = useRoute()
const router = useRouter()
const totalNoteCount = ref(0)

contextStore.loadingStart('Peer advising home page is loading')

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

const fetchNotes = () => {
  return new Promise<void>(resolve => {
    if (peerAdvisor.value && peerAdvisor.value.uid) {
      offset.value = notes.value.length || 0
      getPeerAdvisorNotes(
        offset.value,
        LIMIT_PER_FETCH,
        peerAdvisor.value.uid,
        true
      ).then(data => {
        notes.value = orderBy([...notes.value, ...data.notes], ['createdAt'], ['desc'])
        totalNoteCount.value = data.totalNoteCount
        notesDescription.value = notes.value.length < totalNoteCount.value ? `Showing ${notes.value.length} of ${totalNoteCount.value} notes.` : `Showing all ${notes.value.length} notes.`
        isFetchingNotes.value = false
        resolve()
      })
    } else {
      throw Error('Not Found')
    }
  })
}

const getStudentName = (note: Note) => note.student ? `${note.student.firstName} ${note.student.lastName}` : `SID: ${note.sid}`

const init = (user: BoaUser) => {
  peerAdvisor.value = user
  // Peer Advisors can belong to one and only one Peer Advising Department.
  const memberships = getPeerAdvisorDepartmentMemberships(peerAdvisor.value, 'peer_advisor')
  peerAdvisingDepartmentId.value = memberships.length ? memberships[0].peerAdvisingDepartmentId : undefined
  if (peerAdvisor.value.id && peerAdvisingDepartmentId.value) {
    fetchNotes().then(() => {
      contextStore.loadingComplete(`Home page loaded. ${notesDescription.value}`)
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
  note.peerAdvisingDepartmentId = peerAdvisingDepartmentId.value
  noteStore.setModel(note)
  noteStore.setMode('createPeerAdvisorNote')
  createNoteModal.value = true
  noteStore.setIsCreateNoteModalOpen(true)
}

const onClickShowMore = () => {
  alertScreenReader('Loading additional notes')
  fetchNotes().then(() => {
    alertScreenReader(notesDescription.value)
    putFocusNextTick(`tr-peer-advisor-note-${get(last(notes.value), 'id')}`)
  })
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const onPeerAdvisingNoteCreated: Handler<any> = (note: Note) => {
  totalNoteCount.value += 1
  getBasicStudent(note.sid).then((student: BasicStudent) => {
    note.student = student
    notes.value.unshift(note)
  })
}
</script>
