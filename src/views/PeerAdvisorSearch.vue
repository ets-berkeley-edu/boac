<template>
  <div v-if="!contextStore.loading">
    <!-- HEADER (title + tabs) -->
    <div class="peer-header pt-10 px-12">
      <h1 id="page-header" class="mb-3">Peer Advising Search</h1>

      <!-- Tabs strip (header background applies here too) -->
      <v-tabs
        v-model="tab"
        aria-label="peer-advising tabs"
        :aria-orientation="tabsDirection"
        density="comfortable"
        :direction="tabsDirection"
        :items="tabs"
        mobile-breakpoint="md"
        class="tab-strip"
      >
        <template #tab="{ item }">
          <v-tab
            :id="`peer-tab-${item.key}`"
            :aria-controls="`peer-tab-panel-${item.key}`"
            class="border-s-sm border-e-sm border-t-sm mx-1 rounded-t-lg"
            :class="{
              'bg-white border-b-0': item.key === tab,
              'bg-grey-lighten-4 border-b-md': item.key !== tab
            }"
            hide-slider
            min-width="120"
            :value="item.key"
            variant="text"
          >
            <template #default>
              <div class="d-flex flex-row-reverse font-size-12 font-weight-bold">
                <div :id="`peer-tab-count-${item.key}`" class="text-black">
                  {{ item.countLabel }}
                </div>
                <div
                  class="mr-1 text-uppercase"
                  :class="{'text-black': item.key === tab, 'text-primary': item.key !== tab}"
                >
                  {{ item.title }}
                </div>
              </div>
            </template>
          </v-tab>
        </template>
      </v-tabs>
    </div>

    <!-- PANELS (full-width below tabs) -->
    <div class="peer-content">
      <v-window v-model="tab">
        <!-- STUDENTS TAB -->
        <v-window-item
          :id="'peer-tab-panel-student'"
          value="student"
          :aria-labelledby="'peer-tab-student'"
          role="tabpanel"
          class="w-100"
        >
          <div class="px-4 py-6 mx-4">
            <div class="d-flex align-center">
              <span v-if="!isFetchingNotes">
                {{ studentPhrase }} "<span class="font-weight-bold">{{ queryText }}</span>"
              </span>
              <span v-else>Searching Students...</span>
              <span :aria-hidden="true" class="ml-3 mr-2 text-medium-emphasis">|</span>
              <v-btn
                class="text-anchor mx-1 px-1"
                role="link"
                variant="text"
                :disabled="isFetchingNotes"
                @click="clearResults"
              >
                Return to Home
              </v-btn>
            </div>
            <PeerAdvisingStudentsTable
              :students="students"
              :peer-advising-department-id="peerAdvisingDepartmentId"
            />
            <div class="my-3 text-center">
              <v-btn
                v-if="hasMoreStudents"
                id="fetch-more-students"
                text="Show additional students"
                variant="text"
                @click.prevent="showMoreStudents"
              />
              <SectionSpinner v-if="size(notes)" :loading="isFetchingNotes" />
            </div>
          </div>
        </v-window-item>

        <!-- NOTES TAB -->
        <v-window-item
          :id="'peer-tab-panel-note'"
          value="note"
          :aria-labelledby="'peer-tab-note'"
          role="tabpanel"
          class="w-100"
        >
          <div class="px-12 py-4">
            <div class="d-flex justify-space-between">
              <div>
                <div class="d-flex align-center">
                  <span v-if="!isFetchingNotes && totalNoteCount >= 0">
                    {{ notePhrase }} "<span class="font-weight-bold">{{ queryText }}</span>"
                  </span>
                  <span v-else>Searching Notes...</span>
                  <span v-if="showMyNotesOnly || isFetchingNotes || notes.length" :aria-hidden="true" class="ml-3 mr-2 text-medium-emphasis">|</span>
                  <ShowMyPeerAdvisingNotesToggle
                    v-if="showMyNotesOnly || isFetchingNotes || notes.length"
                    v-model="showMyNotesOnly"
                    :is-fetching-notes="isFetchingNotes"
                  />
                </div>
              </div>
            </div>
            <PeerAdvisingNotesTable
              class="mt-4"
              :after-note-edit="afterNoteEdit"
              :notes="notes"
              :is-fetching-notes="isFetchingNotes"
            />
            <div class="my-3 text-center">
              <v-btn
                v-if="hasMoreNotes"
                id="fetch-more-notes"
                text="Show additional advising notes"
                variant="text"
                @click.prevent="showMoreNotes"
              />
              <SectionSpinner v-if="size(notes)" :loading="isFetchingNotes" />
            </div>
          </div>
        </v-window-item>
      </v-window>
    </div>
  </div>
</template>

<script setup lang="ts">
import {findIndex, get, orderBy, size} from 'lodash'
import {computed, onMounted, onUnmounted, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useDisplay} from 'vuetify'
import type {BoaUser, Note} from '@/lib/types'
import PeerAdvisingNotesTable from '@/components/peer/note/PeerAdvisingNotesTable.vue'
import SectionSpinner from '@/components/util/SectionSpinner.vue'
import ShowMyPeerAdvisingNotesToggle from '@/components/peer/note/ShowMyPeerAdvisingNotesToggle.vue'
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'
import {getPeerAdvisorDepartmentMemberships} from '@/lib/berkeley-department'
import {getPeerAdvisorNoteById} from '@/api/peer-advising-notes'
import {getUserByUid} from '@/api/user'
import {useContextStore} from '@/stores/context'
import {peerAdvisorSearch} from '@/api/search'
import {useSearchStore} from '@/stores/search'
import PeerAdvisingStudentsTable from '@/components/peer/PeerAdvisingStudentsTable.vue'

const {mdAndUp} = useDisplay()
const tabsDirection = computed(() => (mdAndUp.value ? 'horizontal' : 'vertical'))

const LIMIT_PER_FETCH = 50

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const isFetchingNotes = ref(false)
const notes = ref<Note[]>([])
const students = ref<[]>([])
const offset = ref(0)
const peerAdvisingDepartmentId = ref<number | undefined>()
const peerAdvisor = ref<BoaUser>(contextStore.currentUser)
const notePhrase = ref('')
const studentPhrase = ref('')
const route = useRoute()
const router = useRouter()
const searchStore = useSearchStore()
const totalNoteCount = ref(0)
const totalStudentCount = ref(0)
const showMyNotesOnly = ref(false)
const queryText = ref(searchStore.queryText)

// Tabs
const tab = ref<'note' | 'student'>('student')
const hasMoreNotes = computed(() => totalNoteCount.value > size(notes.value))
const hasMoreStudents = computed(() => totalStudentCount.value > size(students.value))

const tabs = computed(() => ([
  {
    key: 'student',
    title: 'STUDENTS',
    countLabel: totalStudentCount.value
      ? `${Math.min(size(students.value), totalStudentCount.value)}${size(students.value) < totalStudentCount.value ? '+' : ''}`
      : '0'
  },
  {
    key: 'note',
    title: 'NOTES',
    countLabel: totalNoteCount.value
      ? `${Math.min(size(notes.value), totalNoteCount.value)}${size(notes.value) < totalNoteCount.value ? '+' : ''}`
      : '0'
  }
] as const))

watch(showMyNotesOnly, async () => {
  notes.value = []
  totalNoteCount.value = 0
  isFetchingNotes.value = true
  search(true, false)
})

contextStore.loadingStart()

onMounted(() => {
  const memberships = getPeerAdvisorDepartmentMemberships(peerAdvisor.value, 'peer_advisor')
  peerAdvisingDepartmentId.value = memberships.length ? memberships[0].peerAdvisingDepartmentId : undefined
  if (currentUser.isAdmin) {
    const uid = route.params.uid.toString()
    getUserByUid(uid, false).then(data => {
      peerAdvisor.value = data
      search(true, true)
    })
  } else {
    search(true, true)
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

const search = (getNotes = true, getStudents = true) => {
  peerAdvisor.value = contextStore.currentUser
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
      LIMIT_PER_FETCH,
      peerAdvisor.value.uid,
      showMyNotesOnly.value,
      getNotes,
      getStudents
    ).then(data => {
      const putFocusId = offset.value === 0 ? 'page-header' : `tr-peer-advisor-${data.notes[0]?.id}`
      // notes.value = orderBy(data.notes, n => n.updatedAt || n.createdAt, ['desc'])
      if (getNotes) {
        notes.value = orderBy([...notes.value, ...data.notes], n => n.updatedAt || n.createdAt, ['desc'])
        totalNoteCount.value = data.totalNoteCount
        if (totalNoteCount.value === 0) {
          notePhrase.value = 'No results found matching '
        } else if (size(notes.value) < totalNoteCount.value) {
          notePhrase.value = `Showing ${notes.value.length} of ${pluralize('result', totalNoteCount.value)} matching `
        } else {
          notePhrase.value = `Showing ${pluralize('result', totalNoteCount.value)} matching `
        }
      }

      if (getStudents) {
        students.value = [...students.value, ...data.students]
        totalStudentCount.value = data.totalStudentCount
        if (totalStudentCount.value === 0) {
          studentPhrase.value = 'No results found matching '
        } else if (size(students.value) < totalStudentCount.value) {
          studentPhrase.value = `Showing ${students.value.length} of ${pluralize('result', totalStudentCount.value)} matching `
        } else {
          studentPhrase.value = `Showing ${pluralize('result', totalStudentCount.value)} matching `
        }
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
  search(true, false)
}

const showMoreStudents = () => {
  offset.value = get(students.value, 'length', 0)
  search(false, true)
}
</script>

<style scoped>
.peer-header {
  background-color: rgb(var(--v-theme-sky-blue)) !important;
}

.peer-content {
  width: 100%;
}
</style>
