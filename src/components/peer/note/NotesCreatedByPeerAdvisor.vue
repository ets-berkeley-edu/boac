<template>
  <div>
    <v-btn
      :id="timeframe ? `open-notes-created-by-${user.uid}-during-${timeframe.year}-${timeframe.month}` : `open-notes-created-by-${user.uid}`"
      :aria-label="`View notes created by ${user.name}`"
      class="peer-advisor-btn text-primary pa-1 mb-1"
      size="md"
      variant="text"
      @click="showModal"
    >
      {{ get(user, 'noteCount') }}<span class="sr-only"> notes <span v-if="timeframe">created during {{ timeframe.label }}</span></span>
    </v-btn>
    <v-dialog
      v-model="isModalOpen"
      :fullscreen="$vuetify.display.smAndDown"
      persistent
      scrollable
      @keydown.esc="closeModal"
    >
      <v-card
        class="peer-advising-notes-modal modal-content px-0"
        max-width="1100"
        min-height="calc(100vh - 100px)"
        width="90vw"
      >
        <v-card-title>
          <div class="align-start d-flex justify-content-between w-100">
            <ModalHeader class="text-wrap w-100" :text="headerText" />
            <div class="text-right">
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
        <v-card-text class="modal-body overflow-x-hidden px-1 px-md-6">
          <div :id="`peer-advising-department-${peerAdvisingDepartment.id}`" class="pl-5 pl-md-0">
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
              :after-note-edit="afterNoteEdit"
              class="d-block font-size-16 w-100"
              :is-fetching-notes="isFetchingNotes"
              :notes="notes"
              :show-student-last-name-first="true"
            />
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
import {get, orderBy} from 'lodash'
import {onBeforeUnmount, onMounted, ref} from 'vue'
import {mdiCloseThick} from '@mdi/js'
import type {BoaUser, Note, PeerAdvisingDepartment} from '@/lib/types'
import type {Month} from '@/lib/types-peer-advising'
import ModalHeader from '@/components/util/ModalHeader.vue'
import PeerAdvisingNotesTable from '@/components/peer/note/PeerAdvisingNotesTable.vue'
import {toggleModalBackgroundDisabled} from '@/lib/utils'
import {getPeerAdvisingNotesAuthoredBy} from '@/api/peer-advising-notes'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

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
const noteStore = useNoteStore()
const isFetchingNotes = ref<boolean>(false)
const isModalOpen = ref<boolean>(false)
const notes = ref<Note[]>([])

onMounted(() => {
  contextStore.setEventHandler('note-deleted', () => {
    getPeerAdvisingNotesAuthoredBy(props.peerAdvisingDepartment.id, props.user.uid, props.timeframe).then(data => {
      notes.value = orderBy(data, n => n.updatedAt || n.createdAt, ['desc'])
    })
  })
})

onBeforeUnmount(() => {
  toggleModalBackgroundDisabled(false)
  noteStore.exitSession()
  contextStore.removeEventHandler('note-deleted')
})

const afterNoteEdit = () => {
  getPeerAdvisingNotesAuthoredBy(
    props.peerAdvisingDepartment.id,
    props.user.uid,
    props.timeframe
  ).then(data => {
    notes.value = data
  })
}

const closeModal = () => {
  toggleModalBackgroundDisabled(false)
  noteStore.exitSession()
  isModalOpen.value = false
  notes.value = []
}

const showModal = () => {
  toggleModalBackgroundDisabled(true)
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
