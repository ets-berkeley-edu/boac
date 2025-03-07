<template>
  <div>
    <button
      :id="`open-notes-created-by-${user.uid}`"
      :aria-label="`View notes created by ${user.name}`"
      class="text-primary"
      @click="showModel"
    >
      {{ get(user, 'noteCount') }}
    </button>
    <v-dialog
      v-model="isModalOpen"
      persistent
      width="800"
      @keydown.esc="closeModal"
    >
      <v-card class="pl-3 pr-5 py-4">
        <v-card-title class="pb-0">
          <div class="align-start d-flex justify-content-between w-100">
            <ModalHeader :text="headerText" />
            <div class="text-right w-100">
              <v-btn
                v-if="!isFetchingNotes"
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
        <v-card-text class="py-0">
          <div v-if="isFetchingNotes" class="my-16 text-center w-100">
            <v-progress-circular
              color="primary"
              indeterminate
            />
          </div>
          <v-expand-transition>
            <table
              v-if="!isFetchingNotes"
              id="notes-for-peer-advisor-view"
              class="mt-5 w-100"
            >
              <thead>
                <tr>
                  <th class="border-b-md th-student">Student</th>
                  <th class="border-b-md th-note">Note</th>
                  <th class="border-b-md th-created-date">
                    <div class="float-right">Date Created</div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(note, index) in notes"
                  :key="index"
                  :class="index % 2 === 0 ? '' : 'bg-surface-light'"
                >
                  <td :class="{'border-b-md': index === notes.length - 1}" class="td-student text-medium-emphasis">
                    <div
                      v-if="note.student"
                      :id="`note-student-${note.student.sid}`"
                      :class="{'demo-mode-blur': currentUser.inDemoMode}"
                    >
                      <router-link
                        v-if="currentUser.isAdmin"
                        :id="`link-to-student-${note.sid}`"
                        :class="{'demo-mode-blur': currentUser.inDemoMode}"
                        :to="studentRoutePath(note.student.uid, currentUser.inDemoMode)"
                      >
                        <span v-html="lastNameFirst(note.student)" />
                      </router-link>
                      <div v-if="!currentUser.isAdmin">
                        <span v-html="`${getStudentName(note)}`" />
                      </div>
                    </div>
                    <div v-if="!note.student">
                      SID: {{ note.sid }}
                    </div>
                  </td>
                  <td :id="`note-body-in-row-${index}`" :class="{'border-b-md': index === notes.length - 1}" class="td-note">
                    <!--
                    TODO: Should admins link to /student profile page so they can easily delete.
                    <router-link
                      v-if="currentUser.isAdmin"
                      :id="`link-to-student-${note.student.uid}`"
                      :class="{'demo-mode-blur': currentUser.inDemoMode}"
                      class="align-center d-flex font-weight-medium justify-space-between w-100"
                      :to="`${studentRoutePath(note.student.uid, currentUser.inDemoMode)}#permalink-note-${note.id}`"
                    >
                      <span class="truncate-with-ellipsis">{{ stripHtmlAndTrim(note.body) }}</span>
                    </router-link>
                    -->
                    <v-expand-transition>
                      <button
                        v-if="!expandedNoteIds.includes(note.id)"
                        :id="`open-peer-advising-${note.id}`"
                        :aria-label="`Edit ${getStudentName(note)} note`"
                        class="align-center d-flex justify-space-between text-primary w-100"
                        :class="{'demo-mode-blur': currentUser.inDemoMode}"
                        @click="() => toggleShowHide(note)"
                      >
                        <span class="truncate-with-ellipsis">{{ stripHtmlAndTrim(note.body) }}</span>
                      </button>
                    </v-expand-transition>
                    <v-expand-transition>
                      <div v-if="expandedNoteIds.includes(note.id)">
                        <div class="margins-of-hide-note-btn text-center w-100">
                          <v-btn
                            :id="`hide-note-${note.id}-details`"
                            :aria-expanded="true"
                            class="w-100"
                            color="primary"
                            density="compact"
                            :prepend-icon="mdiCloseCircle"
                            text="Close Message"
                            variant="text"
                            @click="toggleShowHide(note)"
                          />
                        </div>
                        <PeerAdvisingNoteDetails class="my-3" :note="note" />
                      </div>
                    </v-expand-transition>
                  </td>
                  <td
                    :id="`note-created-date-in-row-${index}`"
                    :class="{'border-b-md': index === notes.length - 1}"
                    class="td-created-date"
                  >
                    <div class="float-right">
                      {{ DateTime.fromISO(note.createdAt).toLocaleString(DateTime.DATE_MED) }}
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </v-expand-transition>
        </v-card-text>
        <v-card-actions v-if="!isFetchingNotes" class="text-right">
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
import {DateTime} from 'luxon'
import {get, isNil} from 'lodash'
import {mdiCloseCircle, mdiCloseThick} from '@mdi/js'
import {computed, ref} from 'vue'
import type {BoaUser, Note} from '@/lib/types'
import {getNotesAuthoredBy} from '@/api/notes'
import {lastNameFirst, stripHtmlAndTrim, studentRoutePath} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import ModalHeader from '@/components/util/ModalHeader.vue'
import PeerAdvisingNoteDetails from '@/components/peer/note/PeerAdvisingNoteDetails.vue'

const props = defineProps({
  headerText: {
    required: true,
    type: String
  },
  user: {
    required: true,
    type: Object as PropType<BoaUser>
  }
})

const currentUser = useContextStore().currentUser
const expandedNoteIds = ref<number[]>([])
const isFetchingNotes = computed(() => isNil(notes.value))
const isModalOpen = ref(false)
const notes = ref<Note[] | undefined>()

const closeModal = () => isModalOpen.value = false
const getStudentName = (note: Note) => note.student ? `${note.student.firstName} ${note.student.lastName}` : `SID: ${note.sid}`

const showModel = () => {
  isModalOpen.value = true
  if (isNil(notes.value)) {
    getNotesAuthoredBy(props.user.uid).then(data => {
      notes.value = data
    })
  }
}

const toggleShowHide = (note: Note) => {
  const index = expandedNoteIds.value.indexOf(note.id)
  if (index > -1) {
    expandedNoteIds.value.splice(index, 1)
  } else {
    expandedNoteIds.value.push(note.id)
  }
}
</script>

<style scoped>
.td-created-date {
  font-size: 14px;
  max-width: 120px !important;
  padding: 5px 0;
  text-wrap: nowrap;
  vertical-align: top;
  width: 120px !important;
}
.td-note {
  font-size: 14px;
  max-width: 300px !important;
  padding: 5px;
  vertical-align: top;
}
.td-student {
  font-size: 14px;
  font-weight: bolder;
  max-width: 200px !important;
  padding: 5px;
  vertical-align: top;
}
.th-created-date {
  padding: 5px 0;
  text-wrap: nowrap;
}
.th-note {
  padding: 5px;
}
.th-student {
  font-weight: bold;
  padding: 0 5px;
}
</style>
