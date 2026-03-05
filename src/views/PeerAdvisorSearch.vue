<template>
  <div v-if="!contextStore.loading">
    <div class="bg-sky-blue pt-8">
      <h1 id="page-header" class="mb-3 mx-10 ">Peer Advising Search</h1>
      <v-tabs
        v-model="tab"
        aria-label="peer-advising tabs"
        aria-orientation="horizontal"
        class="mx-8"
        density="comfortable"
        direction="horizontal"
        :items="tabs"
      >
        <template #tab="{ item }">
          <v-tab
            :id="`peer-tab-${item.key}`"
            :aria-controls="`peer-tab-panel-${item.key}`"
            class="border-s-sm border-e-sm border-t-sm mx-1 rounded-t-lg"
            :class="{
              'bg-white border-b-0': item.key === tab,
              'bg-surface-light border-b-md': item.key !== tab
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
        <template #item>
          <v-tabs-window-item
            :id="'peer-tab-panel-student'"
            :aria-labelledby="'peer-tab-student'"
            class="bg-surface h-100"
            role="tabpanel"
            value="student"
          >
            <div class="px-4 px-lg-8 py-6">
              <div class="d-flex align-center px-3">
                <h2 v-if="!isFetchingNotes" id="peer-tab-student-summary" class="text-body-1">
                  {{ studentPhrase }} "<span class="font-weight-bold">{{ queryText }}</span>"
                </h2>
                <span v-else>Searching Students...</span>
                <span :aria-hidden="true" class="mx-3 text-medium-emphasis">|</span>
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
                :sids-with-notes="sidsWithNotes"
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
          </v-tabs-window-item>
          <v-tabs-window-item
            :id="'peer-tab-panel-note'"
            :aria-labelledby="'peer-tab-note'"
            class="bg-surface w-100"
            role="tabpanel"
            value="note"
          >
            <div class="px-4 px-lg-8 py-6">
              <div class="d-flex justify-space-between">
                <div>
                  <div class="d-flex align-center">
                    <h2 v-if="!isFetchingNotes && totalNoteCount >= 0" id="peer-tab-note-summary" class="text-body-1">
                      {{ notePhrase }} "<span class="font-weight-bold">{{ queryText }}</span>"
                    </h2>
                    <span v-else>Searching Notes...</span>
                    <span v-if="showMyNotesOnly || isFetchingNotes || notes.length" :aria-hidden="true" class="mx-3 text-medium-emphasis">|</span>
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
          </v-tabs-window-item>
        </template>
      </v-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import {findIndex, get, map, orderBy, size, uniq} from 'lodash'
import {computed, onMounted, onUnmounted, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
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
const sidsWithNotes = ref<[]>([])
const queryText = ref(searchStore.queryText)

// Tabs
const initialTab = route.query.tab
const tab = ref<'note' | 'student'>(initialTab || 'student')
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
      if (getNotes) {
        notes.value = orderBy([...notes.value, ...data.notes], n => n.updatedAt || n.createdAt, ['desc'])
        totalNoteCount.value = data.totalNoteCount
        sidsWithNotes.value = uniq(map(notes.value, 'sid'))
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
      contextStore.loadingComplete()
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
