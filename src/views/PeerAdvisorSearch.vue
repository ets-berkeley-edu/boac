<template>
  <div v-if="!contextStore.loading" class="mt-8 mx-16">
    <div class="d-flex justify-space-between">
      <div>
        <h1>Peer Advising Notes</h1>
        <div>
          Showing {{ pluralize('result', totalNoteCount) }} for <span class="font-weight-bold">{{ queryText }}</span>
          |
          <v-btn
            class="cursor-pointer text-blue-accent-2 select-none mb-1 pl-0"
            variant="text"
            @click="clearResults"
          >
            Clear Search Results
          </v-btn>
        </div>
      </div>
    </div>
    <div v-if="!isPaging">
      <PeerAdvisorNoteSearchResults
        :current-page="currentPage"
        :items-per-page="itemsPerPage"
        :notes="notes"
        :peer-advising-department-id="peerAdvisingDepartmentId"
        :total-note-count="totalNoteCount"
      />
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
import {alertScreenReader, pluralize} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {peerAdvisorSearch} from '@/api/search'
import {useSearchStore} from '@/stores/search'

const contextStore = useContextStore()
const searchStore = useSearchStore()
const currentPage = ref(1)
const isPaging = ref(false)
const itemsPerPage = ref(50)
const notes = ref<Note[]>([])
const peerAdvisingDepartmentId = ref<number>(NaN)
const peerAdvisor = ref<BoaUser>()
const route = useRoute()
const router = useRouter()
const totalNoteCount = ref(0)
const queryText = ref(searchStore.queryText)

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

onUnmounted(() => contextStore.removeEventHandler('peer-advising-note-created'))

const init = (user: BoaUser) => {
  peerAdvisor.value = user
  const membership = getPeerAdvisorDepartmentMembership(peerAdvisor.value, 'peer_advisor')
  if (peerAdvisor.value.id && membership && membership.peerAdvisingDepartmentId) {
    peerAdvisingDepartmentId.value = membership.peerAdvisingDepartmentId
    searchStore.setQueryText(route.query.q || searchStore.queryText)
    alertScreenReader(`Searching for "${searchStore.queryText}"`)
    peerAdvisorSearch(searchStore.queryText, peerAdvisingDepartmentId.value).then(data => {
      notes.value = data.notes
      totalNoteCount.value = data.totalNoteCount
      isPaging.value = false
      queryText.value = searchStore.queryText
      contextStore.loadingComplete('Notes have loaded')
    })
  } else {
    router.push({path: '/404'})
  }
}

const clearResults = () => {
  notes.value = []
  totalNoteCount.value = 0
}

</script>

<style scoped>
.select-none {
  user-select: none;
}
</style>
