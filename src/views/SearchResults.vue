<template>
  <div :class="{'bg-sky-blue': hasSearchResults}">
    <div class="pa-4" :class="{'bg-sky-blue': !hasSearchResults}">
      <div class="align-center d-flex">
        <h1 id="page-header" class="mr-2">{{ searchStore.isSearching ? 'Searching...' : 'Search Results' }}</h1>
        <div v-if="!loading" class="pb-1">
          [<v-btn
            id="edit-search-btn"
            class="px-0"
            color="primary"
            text="edit search"
            variant="text"
            @click.prevent="openAdvancedSearch"
          />]
        </div>
      </div>
      <div v-if="!hasSearchResults && !searchStore.isSearching">
        <div v-if="searchPhraseSubmitted && searchPhraseSubmitted.length > 0">
          No results found for <span class="font-weight-bold">{{ searchPhraseSubmitted }}</span>.
        </div>
        <div v-if="!searchPhraseSubmitted || searchPhraseSubmitted.length === 0">
          No results found for your search query.
        </div>
      </div>
    </div>
    <div v-if="!loading && !searchStore.isSearching">
      <div
        v-if="hasSearchResults"
        aria-live="polite"
        class="sr-only"
        role="alert"
      >
        Search results include {{ describe('Admits', results.totalAdmitCount) }}
        {{ describe('student', results.totalStudentCount) }}
        {{ describe('course', results.totalCourseCount) }}
        {{ describe('note', size(results.notes)) }}{{ completeNoteResults ? '' : '+' }}
        {{ describe('appointment', size(results.appointments)) }}{{ completeAppointmentResults ? '' : '+' }}
      </div>
      <div v-if="!hasSearchResults" id="page-header-no-results" class="my-4 px-5">
        <h3>Suggestions</h3>
        <ul class="mt-2">
          <li class="font-size-15 pt-1">Keep your search term simple.</li>
          <li class="font-size-15 pt-1">Check your spelling and try again.</li>
          <li class="font-size-15 pt-1">Search classes by section title, e.g., <strong>AMERSTD 10</strong>.</li>
          <li class="font-size-15 pt-1">Avoid using generic terms, such as <strong>test</strong> or <strong>enrollment</strong>.</li>
          <li class="font-size-15 pt-1">Longer search terms may refine results; <strong>registration fees</strong> instead of <strong>registration</strong>.</li>
          <li class="font-size-15 pt-1">Abbreviations of section titles may not return results; <strong>COMPSCI 161</strong> instead of <strong>CS 161</strong>.</li>
        </ul>
      </div>
      <div v-if="results.totalAdmitCount || results.totalStudentCount || results.totalCourseCount || size(results.appointments) || size(results.notes)">
        <v-tabs
          v-model="tab"
          aria-label="search results tab"
          :aria-orientation="$vuetify.display.mdAndUp ? 'horizontal' : 'vertical'"
          class="ml-3"
          density="comfortable"
          :direction="$vuetify.display.mdAndUp ? 'horizontal' : 'vertical'"
          :items="tabs"
          mobile-breakpoint="md"
        >
          <template #tab="{item}">
            <v-tab
              :id="`search-results-tab-${item.key}s`"
              :aria-controls="`search-results-tab-panel-${item.key}s`"
              class="bg-white border-s-sm border-e-sm border-t-sm mx-1 rounded-t-lg"
              :class="{
                'border-b-0': item.key === tab,
                'border-b-sm': item.key !== tab
              }"
              hide-slider
              min-width="120"
              :value="item.key"
              variant="text"
            >
              <template #default>
                <div class="d-flex flex-row-reverse font-size-12 font-weight-bold">
                  <div :id="`search-results-count-${item.key}s`">
                    {{ getTabLabel(item) }}
                  </div>
                  <div
                    class="mr-1 text-uppercase"
                    :class="{'text-black': item.key === tab, 'text-primary': item.key !== tab}"
                  >
                    {{ item.key }}s
                  </div>
                </div>
              </template>
            </v-tab>
          </template>
          <template #item="{item}">
            <v-tabs-window-item
              :id="`search-results-tab-panel-${item.key}s`"
              :aria-labelledby="`search-results-tab-${item.key}s`"
              :aria-selected="item.key === tab"
              class="bg-white px-4"
              role="tabpanel"
              :value="item.key"
            >
              <div v-if="item.key === 'student'">
                <SearchResultsHeader
                  class="mb-2 mt-4"
                  :count-in-view="size(results.students)"
                  :count-total="results.totalStudentCount"
                  :results-type="item.key"
                  :search-phrase="searchPhraseSubmitted"
                />
                <div v-if="size(results.students)" class="mt-1">
                  <CuratedGroupSelector
                    context-description="Search"
                    domain="default"
                    :students="results.students"
                  />
                  <SortableStudents
                    domain="default"
                    :include-curated-checkbox="true"
                    :students="results.students"
                  />
                </div>
              </div>
              <div v-if="item.key === 'admit'">
                <div v-if="results.totalAdmitCount" class="mt-5">
                  <AdmitDataWarning :updated-at="get(results.admits, '[0].updatedAt')" />
                </div>
                <SearchResultsHeader
                  class="my-3"
                  :count-in-view="size(results.admits)"
                  :count-total="results.totalAdmitCount"
                  :results-type="item.key"
                  :search-phrase="searchPhraseSubmitted"
                />
                <div v-if="results.totalAdmitCount">
                  <div class="mb-2">
                    <CuratedGroupSelector
                      context-description="Search"
                      domain="admitted_students"
                      :students="results.admits"
                    />
                  </div>
                  <SortableAdmits :admitted-students="results.admits" />
                </div>
              </div>
              <div v-if="item.key === 'course'">
                <div class="mb-4 mt-3">
                  <SearchResultsHeader
                    :count-in-view="size(results.courses)"
                    :count-total="results.totalCourseCount"
                    :results-type="item.key"
                    :search-phrase="searchPhraseSubmitted"
                  />
                </div>
                <SortableCourses
                  v-if="size(results.courses)"
                  :courses="results.courses"
                />
              </div>
              <div v-if="item.key === 'note'">
                <SearchResultsHeader
                  class="mb-2 mt-4"
                  :count-in-view="size(results.notes)"
                  :count-total="results.totalNoteCount"
                  :results-type="item.key"
                  :search-phrase="searchPhraseSubmitted"
                />
                <AdvisingNoteSnippet
                  v-for="advisingNote in results.notes"
                  :key="advisingNote.id"
                  :note="advisingNote"
                />
                <div class="text-center">
                  <v-btn
                    v-if="!completeNoteResults"
                    id="fetch-more-notes"
                    text="Show additional advising notes"
                    variant="text"
                    @click.prevent="fetchMoreNotes"
                  />
                  <SectionSpinner :loading="loadingAdditionalNotes" />
                </div>
              </div>
              <div v-if="item.key === 'appointment'">
                <SearchResultsHeader
                  class="mb-2 mt-4"
                  :count-in-view="size(results.appointments)"
                  :count-total="results.totalAppointmentCount"
                  :results-type="item.key"
                  :search-phrase="searchPhraseSubmitted"
                />
                <AppointmentSnippet
                  v-for="appointment in results.appointments"
                  :key="appointment.id"
                  :appointment="appointment"
                />
                <div class="text-center">
                  <v-btn
                    v-if="!completeAppointmentResults"
                    id="fetch-more-appointments"
                    text="Show additional advising appointments"
                    variant="text"
                    @click.prevent="fetchMoreAppointments"
                  />
                  <SectionSpinner :loading="loadingAdditionalAppointments" />
                </div>
              </div>
            </v-tabs-window-item>
          </template>
        </v-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdvisingNoteSnippet from '@/components/search/AdvisingNoteSnippet'
import AppointmentSnippet from '@/components/search/AppointmentSnippet'
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector'
import router from '@/router'
import SearchResultsHeader from '@/components/search/SearchResultsHeader'
import SectionSpinner from '@/components/util/SectionSpinner'
import SortableAdmits from '@/components/admit/SortableAdmits'
import SortableCourses from '@/components/search/SortableCourses'
import SortableStudents from '@/components/search/SortableStudents'
import {alertScreenReader, putFocusNextTick, toBoolean, toInt} from '@/lib/utils'
import {capitalize, concat, each, extend, get, merge, size, trim} from 'lodash'
import {computed, onMounted, reactive, ref} from 'vue'
import {mdiAccountSchool, mdiCalendarCheck, mdiHumanGreeting, mdiHumanMaleBoardPoll, mdiNoteEditOutline} from '@mdi/js'
import {search, searchAdmittedStudents} from '@/api/search'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'
import {useSearchStore} from '@/stores/search'

const contextStore = useContextStore()
const searchStore = useSearchStore()

const appointmentsQuery = {limit: 20, offset: 0}
const completeAppointmentResults = computed(() => {
  return size(results.appointments) < appointmentsQuery.limit + appointmentsQuery.offset
})
const completeNoteResults = computed(() => {
  return size(results.notes) < notesQuery.limit + notesQuery.offset
})
const hasSearchResults = computed(() => {
  return !!(results.totalStudentCount || results.totalCourseCount || results.totalAdmitCount || size(results.notes) || size(results.appointments))
})
const loading = computed(() => contextStore.loading)
const loadingAdditionalAppointments = ref(false)
const loadingAdditionalNotes = ref(false)
const noteAndAppointmentOptions = reactive({
  advisorCsid: undefined,
  advisorUid: undefined,
  studentCsid: undefined,
  departmentCodes: undefined,
  topic: undefined,
  dateFrom: undefined,
  dateTo: undefined
})
const notesQuery = reactive({limit: 20, offset: 0})
const results = reactive({
  admits: [],
  appointments: [],
  courses: [],
  notes: [],
  students: [],
  totalAdmitCount: undefined,
  totalCourseCount: undefined,
  totalStudentCount: undefined
})
const searchPhraseSubmitted = ref(undefined)
const tab = ref(undefined)
const tabs = computed(() => {
  const tabs = []
  const push = (key, count, included, icon) => {
    if (included) {
      tabs.push({count, icon, key})
    }
  }
  push('student', results.totalStudentCount || 0, searchStore.includeStudents, mdiAccountSchool)
  push('admit', results.totalAdmitCount || 0, searchStore.includeAdmits, mdiHumanGreeting)
  push('course', results.totalCourseCount || 0, searchStore.includeCourses, mdiHumanMaleBoardPoll)
  push('note', size(results.notes), searchStore.includeNotes, mdiNoteEditOutline)
  push('appointment', size(results.appointments), searchStore.includeNotes, mdiCalendarCheck)
  return tabs
})

contextStore.loadingStart()

onMounted(() => {
  // Update 'queryText' in Vuex store per 'q' arg. If arg is null then preserve existing 'queryText' value.
  const route = useRoute()
  searchStore.setQueryText(route.query.q || searchStore.queryText)
  // Take a snapshot of the submitted search phrase. The 'queryText' value (in store) may change.
  searchPhraseSubmitted.value = searchStore.queryText
  searchStore.setIncludeAdmits(toBoolean(route.query.admits))
  searchStore.setIncludeCourses(toBoolean(route.query.courses))
  searchStore.setIncludeStudents(toBoolean(route.query.students))
  const includeNotesAndAppointments = toBoolean(route.query.notes)
  if (includeNotesAndAppointments) {
    noteAndAppointmentOptions.advisorCsid = route.query.advisorCsid
    noteAndAppointmentOptions.advisorUid = route.query.advisorUid
    noteAndAppointmentOptions.studentCsid = route.query.studentCsid
    noteAndAppointmentOptions.departmentCodes = route.query.departmentCodes
    noteAndAppointmentOptions.topic = route.query.noteTopic
    noteAndAppointmentOptions.dateFrom = route.query.noteDateFrom
    noteAndAppointmentOptions.dateTo = route.query.noteDateTo
  }
  if (searchStore.queryText || includeNotesAndAppointments) {
    searchStore.setIsSearching(true)
    alertScreenReader(`Searching for '${searchStore.queryText}'`)
    const queries = []
    if (searchStore.includeCourses || includeNotesAndAppointments || searchStore.includeStudents) {
      queries.push(
        search(
          searchStore.queryText,
          includeNotesAndAppointments,
          searchStore.includeCourses,
          includeNotesAndAppointments,
          searchStore.includeStudents,
          extend({}, noteAndAppointmentOptions, appointmentsQuery),
          extend({}, noteAndAppointmentOptions, notesQuery)
        )
      )
    }
    if (searchStore.includeAdmits && trim(searchStore.queryText)) {
      queries.push(searchAdmittedStudents(searchStore.queryText))
    }
    Promise.all(queries).then(responses => {
      each(responses, (response) => merge(results, response))
      each(results.students, student => {
        student.alertCount = student.alertCount || 0
        student.term = student.term || {}
        student.term.enrolledUnits = student.term.enrolledUnits || 0
      })
    })
      .then(() => {
        contextStore.loadingComplete()
        const totalCount = toInt(results.totalCourseCount, 0) + toInt(results.totalStudentCount, 0)
        const focusId = totalCount ? 'page-header' : 'page-header-no-results'
        putFocusNextTick(focusId)
      }).finally(() => {
        searchStore.setIsSearching(false)
      })
  } else {
    router.push({path: '/'})
  }
})

const getTabLabel = item => {
  const admitCount = size(results.admits)
  const courseCount = size(results.courses)
  const studentCount = size(results.students)
  let label
  switch (item.key) {
  case 'admit':
    label = `${admitCount}${!admitCount || admitCount === results.totalAdmitCount ? '' : '+' }`
    break
  case 'appointment':
    label = `${item.count}${completeAppointmentResults.value ? '' : '+'}`
    break
  case 'course':
    label = `${courseCount}${!courseCount || courseCount === results.totalCourseCount ? '' : '+' }`
    break
  case 'note':
    label = `${item.count}${completeNoteResults.value ? '' : '+'}`
    break
  case 'student':
    label = `${studentCount}${!studentCount || studentCount === results.totalStudentCount ? '' : '+' }`
    break
  }
  return label
}

const describe = (noun, count) => {
  return count > 0 ? `${count} ${capitalize(noun)}${count === 1 ? '' : 's'}, ` : ''
}

const fetchMoreAppointments = () => {
  appointmentsQuery.offset = appointmentsQuery.offset + appointmentsQuery.limit
  appointmentsQuery.limit = 20
  loadingAdditionalAppointments.value = true
  search(
    searchStore.queryText,
    true,
    false,
    false,
    false,
    extend({}, noteAndAppointmentOptions, appointmentsQuery),
    null
  )
    .then(data => {
      results.appointments = concat(results.appointments, data.appointments)
      loadingAdditionalAppointments.value = false
    })
}

const fetchMoreNotes = () => {
  notesQuery.offset = notesQuery.offset + notesQuery.limit
  notesQuery.limit = 20
  loadingAdditionalNotes.value = true
  search(
    searchStore.queryText,
    false,
    false,
    true,
    false,
    null,
    extend({}, noteAndAppointmentOptions, notesQuery)
  )
    .then(data => {
      results.notes = concat(results.notes, data.notes)
      loadingAdditionalNotes.value = false
    })
}

const openAdvancedSearch = () => {
  searchStore.setShowAdvancedSearch(true)
  alertScreenReader('Advanced search is open')
}
</script>

<style scoped>
li {
  margin-left: 24px;
  padding-top: 6px;
}
</style>
