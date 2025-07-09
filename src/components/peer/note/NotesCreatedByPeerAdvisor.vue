<template>
  <div>
    <button
      :id="timeframe ? `open-notes-created-by-${user.uid}-during-${timeframe.year}-${timeframe.month}` : `open-notes-created-by-${user.uid}`"
      :aria-label="`View notes created by ${user.name}`"
      class="text-primary"
      @click="showModal"
    >
      {{ get(user, 'noteCount') }}<span class="sr-only"> notes <span v-if="timeframe">created during {{ timeframe.label }}</span></span>
    </button>
    <v-dialog
      v-model="isModalOpen"
      max-width="1100"
      min-width="500"
      persistent
      width="80vw"
      @keydown.esc="closeModal"
    >
      <v-card class="peer-advising-notes-modal modal-content scrollbar-gutter-stable w-100">
        <v-card-title class="pb-0">
          <div class="align-start d-flex justify-content-between w-100">
            <ModalHeader :text="headerText" />
            <div class="text-right w-100">
              <v-btn
                id="header-close-modal"
                aria-label="Close this modal"
                class="font-size-14 font-weight-bold"
                density="comfortable"
                elevation="0"
                icon
                title="Close"
                @click="closeModal"
              >
                <v-icon
                  color="primary"
                  :icon="mdiCloseThick"
                  size="16"
                />
              </v-btn>
            </div>
          </div>
        </v-card-title>
        <v-card-text class="modal-body">
          <div :id="`peer-advising-department-${peerAdvisingDepartment.id}`">
            {{ peerAdvisingDepartment.name }}
            <span v-if="timeframe">
              ({{ timeframe.label }})
            </span>
          </div>
          <div v-if="isFetchingNotes" class="py-16 text-center w-100">
            <v-progress-circular
              id="is-fetching-notes"
              color="primary"
              indeterminate
            />
          </div>
          <v-expand-transition>
            <PeerAdvisingNotesTable
              v-if="!isFetchingNotes"
              class="d-block font-size-14 w-100"
              :get-note-label="getNoteLabel"
              :notes="notes"
              :set-note-details="setPeerAdvisingDepartment"
            >
              <template #studentName="{note}">
                <router-link
                  :id="`note-${note.id}-link-to-student`"
                  :class="{'demo-mode-blur': currentUser.inDemoMode}"
                  :to="studentRoutePath((note as Note).student.uid, currentUser.inDemoMode)"
                >
                  <span v-html="lastNameFirst((note as Note).student)" />
                </router-link>
              </template>
            </PeerAdvisingNotesTable>
          </v-expand-transition>
        </v-card-text>
        <v-card-actions class="modal-footer">
          <v-btn
            id="close-modal"
            class="mr-3"
            color="primary"
            text="Close"
            variant="text"
            @click="closeModal"
          />
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {onBeforeUnmount, onMounted, ref} from 'vue'
import {DateTime} from 'luxon'
import {get, size} from 'lodash'
import {mdiCloseThick} from '@mdi/js'
import type {BoaUser, Note, PeerAdvisingDepartment} from '@/lib/types'
import type {Month} from '@/lib/types-peer-advising'
import ModalHeader from '@/components/util/ModalHeader.vue'
import PeerAdvisingNotesTable from '@/components/peer/note/PeerAdvisingNotesTable.vue'
import {findPeerAdvisingDepartment} from '@/lib/berkeley-department'
import {getPeerAdvisingNotesAuthoredBy} from '@/api/peer-advising-notes'
import {lastNameFirst, stripHtmlAndTrim, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  headerText: {
    required: true,
    type: String
  },
  peerAdvisingDepartment: {
    required: true,
    type: Object as PropType<PeerAdvisingDepartment>
  },
  timeframe: {
    default: undefined,
    required: false,
    type: Object as PropType<Month>
  },
  user: {
    required: true,
    type: Object as PropType<BoaUser>
  }
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const isFetchingNotes = ref(false)
const isModalOpen = ref(false)
const notes = ref<Note[]>([])

onMounted(() => {
  contextStore.setEventHandler('note-deleted', () => {
    getPeerAdvisingNotesAuthoredBy(props.peerAdvisingDepartment.id, props.user.uid, props.timeframe).then(data => {
      notes.value = data
    })
  })
})

onBeforeUnmount(() => contextStore.removeEventHandler('note-deleted'))

const closeModal = () => {
  isModalOpen.value = false
  notes.value = []
}

const getNoteLabel = (note: Note, index: number) => {
  const attachments = note.attachments.length ? `, ${note.attachments.length} attachments` : ''
  const createdDate = `${DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_FULL)}`
  const rowPosition = `${index + 1} of ${size(notes.value) || 'unknown'}`
  return `${rowPosition}, ${getStudentName(note)}, dated ${createdDate}${attachments}. ${stripHtmlAndTrim(note.body)}`
}

const getStudentName = (note: Note) => note.student ? `${note.student.firstName} ${note.student.lastName}` : `SID: ${note.sid}`

const setPeerAdvisingDepartment = (note: Note) => {
  if (!note.peerAdvisingDepartment) {
    note.peerAdvisingDepartment = findPeerAdvisingDepartment(props.peerAdvisingDepartment.id)
  }
}

const showModal = () => {
  isModalOpen.value = true
  isFetchingNotes.value = true
  getPeerAdvisingNotesAuthoredBy(
    props.peerAdvisingDepartment.id,
    props.user.uid,
    props.timeframe
  ).then(data => {
    notes.value = data
    isFetchingNotes.value = false
  })
}
</script>
