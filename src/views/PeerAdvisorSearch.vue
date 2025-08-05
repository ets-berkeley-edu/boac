<template>
  <div v-if="!contextStore.loading" class="mt-8 mx-8 mx-md-16">
    <div class="d-flex justify-space-between">
      <div>
        <h1 id="page-header">Peer Advising Search</h1>
        <div class="d-flex align-center">
          {{ phrase }}&nbsp;<span class="font-weight-bold">{{ queryText }}</span>
          <span :aria-hidden="true" class="ml-3 mr-2 text-medium-emphasis">|</span>
          <v-btn
            class="text-anchor mx-1 px-1"
            role="link"
            variant="text"
            @click="clearResults"
          >
            Return to Home
          </v-btn>
        </div>
      </div>
    </div>
    <div>
      <PeerAdvisingNotesTable :after-note-edit="afterNoteEdit" :notes="notes">
        <template #studentName="{note}">
          <router-link
            v-if="currentUser.isAdmin"
            :id="`note-${note.id}-link-to-student`"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            :to="studentRoutePath(note.student.uid, currentUser.inDemoMode)"
          >
            {{ getStudentName(note) }}
          </router-link>
          <div v-if="!currentUser.isAdmin" :class="{'demo-mode-blur': currentUser.inDemoMode}">
            {{ getStudentName(note) }}
          </div>
        </template>
      </PeerAdvisingNotesTable>
      <div class="my-3 text-center">
        <v-btn
          v-if="totalNoteCount > size(notes)"
          id="fetch-more-notes"
          text="Show additional advising notes"
          variant="text"
          @click.prevent="showMoreNotes"
        />
        <SectionSpinner v-if="size(notes)" :loading="isFetchingNotes" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {findIndex, get, orderBy, size} from 'lodash'
import {onMounted, onUnmounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import type {BoaUser, Note} from '@/lib/types'
import PeerAdvisingNotesTable from '@/components/peer/note/PeerAdvisingNotesTable.vue'
import {alertScreenReader, pluralize, putFocusNextTick, studentRoutePath} from '@/lib/utils'
import {getPeerAdvisorDepartmentMemberships} from '@/lib/berkeley-department'
import {getPeerAdvisorNoteById} from '@/api/peer-advising-notes'
import {getUserByUid} from '@/api/user'
import {useContextStore} from '@/stores/context'
import {peerAdvisorSearch} from '@/api/search'
import {useSearchStore} from '@/stores/search'
import SectionSpinner from '@/components/util/SectionSpinner.vue'

const LIMIT_PER_FETCH = 50

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const isFetchingNotes = ref(false)
const notes = ref<Note[]>([])
const offset = ref(0)
const peerAdvisingDepartmentId = ref<number | undefined>()
const peerAdvisor = ref<BoaUser>(contextStore.currentUser)
const phrase = ref('')
const route = useRoute()
const router = useRouter()
const searchStore = useSearchStore()
const totalNoteCount = ref(0)

const queryText = ref(searchStore.queryText)

contextStore.loadingStart()

onMounted(() => {
  if (currentUser.isAdmin) {
    const uid = route.params.uid.toString()
    getUserByUid(uid, false).then(data => {
      peerAdvisor.value = data
      search()
    })
  } else {
    search()
  }
})

onUnmounted(() => contextStore.removeEventHandler('peer-advising-note-created'))

const clearResults = () => {
  router.push({path: '/home'})
}

const afterNoteEdit = (noteId: number) => {
  return new Promise<void>(resolve => {
    const index = findIndex(notes.value, ['id', noteId])
    if (index > -1) {
      const student = notes.value[index].student
      getPeerAdvisorNoteById(noteId).then(data => {
        notes.value.splice(index, 1, {
          ...data,
          student
        })
        resolve()
      })
    }
  })
}

const getStudentName = (note: Note) => note.student.lastName ? `${note.student.firstName} ${note.student.lastName}` : `SID: ${note.student.sid}`

const search = () => {
  // Peer Advisors can belong to one and only one Peer Advising Department.
  const memberships = getPeerAdvisorDepartmentMemberships(peerAdvisor.value, 'peer_advisor')
  peerAdvisingDepartmentId.value = memberships.length ? memberships[0].peerAdvisingDepartmentId : undefined
  if (peerAdvisor.value.id && peerAdvisingDepartmentId.value) {
    searchStore.setQueryText(route.query.q || searchStore.queryText)
    alertScreenReader(`Searching for "${searchStore.queryText}"`)
    isFetchingNotes.value = true
    peerAdvisorSearch(
      searchStore.queryText,
      peerAdvisingDepartmentId.value,
      offset.value,
      LIMIT_PER_FETCH
    ).then(data => {
      const putFocusId = offset.value === 0 ? 'page-header' : `tr-peer-advisor-${data.notes[0].id}`
      notes.value = orderBy(data.notes, ['createdAt'], ['desc'])
      totalNoteCount.value = data.totalNoteCount
      if (totalNoteCount.value === 0) {
        phrase.value = 'No results found matching '
      } else if (size(notes.value) < totalNoteCount.value) {
        phrase.value = `Showing ${notes.value.length} of ${pluralize('result', totalNoteCount.value)} matching `
      } else {
        phrase.value = `Showing ${pluralize('result', totalNoteCount.value)} matching `
      }
      queryText.value = searchStore.queryText
      contextStore.loadingComplete('Search results loaded')
      isFetchingNotes.value = false
      searchStore.setIsSearching(false)
      putFocusNextTick(putFocusId)
    })
  } else {
    router.push({path: '/404'})
  }
}

const showMoreNotes = () => {
  offset.value = get(notes.value, 'length', 0)
  search()
}
</script>
