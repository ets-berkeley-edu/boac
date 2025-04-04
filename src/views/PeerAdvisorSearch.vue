<template>
  <div v-if="!contextStore.loading" class="mt-8 mx-16">
    <div class="d-flex justify-space-between">
      <div>
        <h1 id="page-header">Peer Advising Search</h1>
        <div>
          Showing {{ notes.length }} of {{ pluralize('result', totalNoteCount) }} for <span class="font-weight-bold">{{ queryText }}</span>
          |
          <v-btn
            class="cursor-pointer text-blue-accent-2 select-none mb-1 pl-0"
            variant="text"
            @click="clearResults"
          >
            Return to Home
          </v-btn>
        </div>
      </div>
    </div>
    <div>
      <PeerAdvisorNoteSearchResults
        :notes="notes"
        :peer-advising-department-id="peerAdvisingDepartmentId"
        :total-note-count="totalNoteCount"
      />
      <div class="my-3 text-center">
        <v-btn
          v-if="totalNoteCount > notes.length"
          id="fetch-more-notes"
          text="Show additional advising notes"
          variant="text"
          @click.prevent="fetchNotes(contextStore.currentUser)"
        />
        <SectionSpinner v-if="notes.length" :loading="isFetchingNotes" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {onMounted, onUnmounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import type {BoaUser, Note} from '@/lib/types'
import PeerAdvisorNoteSearchResults from '@/components/peer/note/PeerAdvisorNoteSearchResults.vue'
import {getPeerAdvisorDepartmentMembership} from '@/lib/berkeley-department'
import {getUserByUid} from '@/api/user'
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {peerAdvisorSearch} from '@/api/search'
import {useSearchStore} from '@/stores/search'
import SectionSpinner from '@/components/util/SectionSpinner.vue'

const LIMIT_PER_FETCH = 50

const contextStore = useContextStore()
const searchStore = useSearchStore()
const notes = ref<Note[]>([])
const peerAdvisingDepartmentId = ref<number>(NaN)
const peerAdvisor = ref<BoaUser>()
const route = useRoute()
const router = useRouter()
const totalNoteCount = ref(0)
const isFetchingNotes = ref(false)
const offset = ref(0)

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

const fetchNotes = (user: BoaUser) => {
  peerAdvisor.value = user
  const membership = getPeerAdvisorDepartmentMembership(peerAdvisor.value, 'peer_advisor')
  if (peerAdvisor.value.id && membership && membership.peerAdvisingDepartmentId) {
    peerAdvisingDepartmentId.value = membership.peerAdvisingDepartmentId
    searchStore.setQueryText(route.query.q || searchStore.queryText)
    alertScreenReader(`Searching for "${searchStore.queryText}"`)
    offset.value = notes.value.length ? notes.value.length : 0
    isFetchingNotes.value = true
    peerAdvisorSearch(
      searchStore.queryText,
      peerAdvisingDepartmentId.value,
      offset.value,
      LIMIT_PER_FETCH
    ).then(data => {
      const putFocusId = offset.value === 0 ? 'page-header' : `tr-peer-advisor-${data.notes[0].id}`
      notes.value.push(...data.notes.reverse())
      totalNoteCount.value = data.totalNoteCount
      queryText.value = searchStore.queryText
      contextStore.loadingComplete('Notes have loaded')
      isFetchingNotes.value = false
      putFocusNextTick(putFocusId)
    })
  } else {
    router.push({path: '/404'})
  }
}

const clearResults = () => {
  router.push({path: '/home'})
}

</script>

<style scoped>
.select-none {
  user-select: none;
}
</style>
