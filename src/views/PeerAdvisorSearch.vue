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
      <PeerAdvisingNotesTable
        :get-note="(noteSearchResult: NoteSearchResult) => noteSearchResult.note"
        :get-note-label="getNoteLabel"
        :notes="notes"
        :set-note-details="setNoteDetails"
      >
        <template #studentName="{note}">
          <router-link
            v-if="currentUser.isAdmin"
            :id="`note-${(note as NoteSearchResult).id}-link-to-student`"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            :to="studentRoutePath((note as NoteSearchResult).studentUid, currentUser.inDemoMode)"
          >
            {{ getStudentName(note as NoteSearchResult) }}
          </router-link>
          <div v-if="!currentUser.isAdmin" :class="{'demo-mode-blur': currentUser.inDemoMode}">
            {{ getStudentName(note as NoteSearchResult) }}
          </div>
        </template>
      </PeerAdvisingNotesTable>
      <div class="my-3 text-center">
        <v-btn
          v-if="totalNoteCount > size(notes)"
          id="fetch-more-notes"
          text="Show additional advising notes"
          variant="text"
          @click.prevent="fetchNotes(contextStore.currentUser)"
        />
        <SectionSpinner v-if="size(notes)" :loading="isFetchingNotes" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import {get, orderBy, size} from 'lodash'
import {onMounted, onUnmounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import type {BoaUser, Note, NoteSearchResult} from '@/lib/types'
import PeerAdvisingNotesTable from '@/components/peer/note/PeerAdvisingNotesTable.vue'
import {alertScreenReader, pluralize, putFocusNextTick, stripHtmlAndTrim, studentRoutePath} from '@/lib/utils'
import {findPeerAdvisingDepartment, getPeerAdvisorDepartmentMembership} from '@/lib/berkeley-department'
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
const notes = ref<NoteSearchResult[]>([])
const offset = ref(0)
const peerAdvisingDepartmentId = ref<number>(NaN)
const peerAdvisor = ref<BoaUser>()
const phrase = ref('')
const route = useRoute()
const router = useRouter()
const searchStore = useSearchStore()
const totalNoteCount = ref(0)

const queryText = ref(searchStore.queryText)

contextStore.loadingStart()

onMounted(() => {
  const currentUser = contextStore.currentUser
  if (currentUser.isAdmin) {
    const uid = route.params.uid.toString()
    getUserByUid(uid, false).then(() => fetchNotes(currentUser))
  } else {
    fetchNotes(currentUser)
  }
})

onUnmounted(() => contextStore.removeEventHandler('peer-advising-note-created'))

const clearResults = () => {
  router.push({path: '/home'})
}

const fetchNotes = (user: BoaUser) => {
  peerAdvisor.value = user
  const membership = getPeerAdvisorDepartmentMembership(peerAdvisor.value, 'peer_advisor')
  if (peerAdvisor.value.id && membership && membership.peerAdvisingDepartmentId) {
    peerAdvisingDepartmentId.value = membership.peerAdvisingDepartmentId
    searchStore.setQueryText(route.query.q || searchStore.queryText)
    alertScreenReader(`Searching for "${searchStore.queryText}"`)
    offset.value = get(notes.value, 'length', 0)
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

const getNoteLabel = (noteSearchResult: NoteSearchResult, index: number) => {
  return `${index + 1} of ${size(notes.value) || 'unknown'}, ${getStudentName(noteSearchResult)}, dated ${DateTime.fromISO(noteSearchResult.createdAt).toLocaleString(DateTime.DATE_FULL)}. ${stripHtmlAndTrim(noteSearchResult.noteSnippet)}`
}

const getStudentName = (noteSearchResult: NoteSearchResult) => noteSearchResult.studentName || `SID: ${noteSearchResult.studentSid}`

const setNoteDetails = (noteSearchResult: NoteSearchResult) => {
  getPeerAdvisorNoteById(noteSearchResult.id).then((note: Note) => {
    if (!note.peerAdvisingDepartment) {
      note.peerAdvisingDepartment = findPeerAdvisingDepartment(note.peerAdvisingDepartmentId)
    }
    noteSearchResult.note = note
  })
}
</script>
