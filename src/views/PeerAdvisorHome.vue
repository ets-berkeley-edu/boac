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
          v-if="noteStore.isCreateNoteModalOpen && peerAdvisingDepartmentId"
          :peer-advising-department-id="peerAdvisingDepartmentId"
        />
      </div>
    </div>
    <div>
      <div v-for="note in notes" :key="note.id">
        {{ note }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {mdiFileDocument} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {useRouter} from 'vue-router'
import type {Note} from '@/lib/types'
import EditPeerAdvisingNoteModal from '@/components/peer/note/EditPeerAdvisingNoteModal.vue'
import {getPeerAdvisorNotes} from '@/api/peer-advising-notes'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'
import {getPeerAdvisorDepartmentMembership} from '@/lib/berkeley-department'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const noteStore = useNoteStore()
const notes = ref<Note[]>([])
const peerAdvisingDepartmentId = ref<number | undefined>()
const router = useRouter()

contextStore.loadingStart()

onMounted(() => {
  const membership = getPeerAdvisorDepartmentMembership(currentUser, 'peer_advisor')
  if (currentUser.id && membership.peerAdvisingDepartmentId) {
    peerAdvisingDepartmentId.value = membership.peerAdvisingDepartmentId
    getPeerAdvisorNotes(
      peerAdvisingDepartmentId.value,
      currentUser.id
    ).then(data => {
      notes.value = data
    })
  } else {
    router.push({path: '/404'})
  }
  contextStore.loadingComplete()
})

const onClickCreateNote = () => {
  noteStore.exitSession()
  noteStore.setMode('createPeerAdvisorNote')
  noteStore.setIsCreateNoteModalOpen(true)
}
</script>

<style scoped>
.page-container {
  margin-left: 12%;
  margin-right: 12%;
}
</style>
