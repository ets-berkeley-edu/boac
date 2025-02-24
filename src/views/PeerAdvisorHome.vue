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
        <EditPeerAdvisingNoteModal v-if="noteStore.isCreateNoteModalOpen" />
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

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const noteStore = useNoteStore()
const notes = ref<Note[]>([])
const router = useRouter()

contextStore.loadingStart()

onMounted(() => {
  // We assume that Peer Advisor belongs solely to one department, with only one role: Peer Advisor.
  const membership = currentUser.departments[0].memberships[0]
  const peerAdvisingDepartmentId = membership.peerAdvisingDepartmentId
  if (peerAdvisingDepartmentId && membership.role === 'peer_advisor' && currentUser.id) {
    getPeerAdvisorNotes(
      peerAdvisingDepartmentId,
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
  noteStore.setIsCreateNoteModalOpen(true)
}
</script>

<style scoped>
.page-container {
  margin-left: 12%;
  margin-right: 12%;
}
</style>
