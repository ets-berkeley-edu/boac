<template>
  <div v-if="!contextStore.loading" class="pt-6 px-2 px-sm-2 px-md-8">
    <PeerAdvisingNotesDashboard
      v-if="peerAdvisingDepartment && peerAdvisor"
      :fetch-notes="fetchNotes"
      :peer-advising-department="peerAdvisingDepartment"
      @ready="onDashboardReady"
    />
  </div>
</template>

<script setup lang="ts">
import {onMounted, onUnmounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import type {BoaUser, Note, PeerAdvisingDepartment} from '@/lib/types'
import PeerAdvisingNotesDashboard from '@/components/peer/note/PeerAdvisingNotesDashboard.vue'
import {findPeerAdvisingDepartment, getPeerAdvisorDepartmentMemberships} from '@/lib/berkeley-department'
import {getPeerAdvisorNotes} from '@/api/peer-advising-notes'
import {getUserByUid} from '@/api/user'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const contextStore = useContextStore()
const noteStore = useNoteStore()
const peerAdvisingDepartment = ref<PeerAdvisingDepartment | undefined>()
const peerAdvisor = ref<BoaUser>()
const route = useRoute()
const router = useRouter()

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
  noteStore.exitSession()
})

const fetchNotes = (offset: number, limit: number, onlyMyNotes?: boolean): Promise<{notes: Note[], totalNoteCount: number}> => {
  if (!peerAdvisor.value?.uid) {
    return Promise.reject(new Error('Not Found'))
  }
  return getPeerAdvisorNotes(
    offset,
    limit,
    peerAdvisor.value.uid,
    true,
    onlyMyNotes
  )
}

const init = (user: BoaUser) => {
  peerAdvisor.value = user
  const memberships = getPeerAdvisorDepartmentMemberships(peerAdvisor.value, 'peer_advisor')
  const peerAdvisingDepartmentId = memberships.length ? memberships[0].peerAdvisingDepartmentId : undefined
  peerAdvisingDepartment.value = peerAdvisingDepartmentId ? findPeerAdvisingDepartment(peerAdvisingDepartmentId) : undefined
  if (!peerAdvisor.value.id || !peerAdvisingDepartment.value) {
    router.push({path: '/404'})
  }
}

const onDashboardReady = () => {
  contextStore.loadingComplete()
}
</script>
