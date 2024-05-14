<template>
  <div class="bg-sky-blue default-margins">
    <div>
      <div class="align-center d-flex">
        <div class="mr-2">
          <h1 class="page-section-header">Search Results</h1>
        </div>
        <div v-if="!loading && isDirty" class="pb-1">
          [<v-btn
            id="edit-search-btn"
            class="mb-1 px-0"
            color="primary"
            text="edit search"
            variant="text"
            @click.prevent="openAdvancedSearch"
          />]
        </div>
      </div>
      <div class="font-weight-500 pb-3">
        Showing results for <span class="font-weight-bold">{{ searchPhraseSubmitted }}</span>
      </div>
    </div>
    <div v-if="!loading">
      <div
        v-if="hasSearchResults"
        aria-live="polite"
        class="sr-only"
        role="alert"
      >
        Search results include {{ describe('Admits', results.totalAdmitCount) }}
        {{ describe('student', results.totalStudentCount) }}
        {{ describe('course', results.totalCourseCount) }}
        {{ describe('note', _size(results.notes)) }}
        {{ describe('appointment', _size(results.appointments)) }}
      </div>
      <div v-if="!hasSearchResults" id="page-header-no-results" class="bg-white pt-4 px-4">
        <div class="pb-4 pt-2">No matching records found.</div>
        <div>Suggestions:</div>
        <ul>
          <li>Keep your search term simple.</li>
          <li>Check your spelling and try again.</li>
          <li>Search classes by section title, e.g., <strong>AMERSTD 10</strong>.</li>
          <li>Avoid using generic terms, such as <strong>test</strong> or <strong>enrollment</strong>.</li>
          <li>Longer search terms may refine results; <strong>registration fees</strong> instead of <strong>registration</strong>.</li>
          <li>Abbreviations of section titles may not return results; <strong>COMPSCI 161</strong> instead of <strong>CS 161</strong>.</li>
        </ul>
      </div>
      <div v-if="results.totalStudentCount">
        <v-tabs
          v-model="tab"
          density="comfortable"
          :direction="$vuetify.display.mdAndUp ? 'horizontal' : 'vertical'"
          :items="tabs"
          mobile-breakpoint="md"
        >
          <template #tab="{item}">
            <v-tab
              :id="`search-results-tab-${item.key}s`"
              class="bg-white border-s-sm border-e-sm border-t-sm mx-1 rounded-t-lg"
              :class="{
                'border-b-0': item.key === tab,
                'border-b-sm': item.key !== tab,
                'ml-3': item.key === 'student'
              }"
              color="white"
              :hide-slider="item.key === tab"
              min-width="120"
              :value="item.key"
              variant="text"
            >
              <template #default>
                <div class="d-flex flex-row-reverse font-size-12 font-weight-bold text-black">
                  <div :id="`search-results-count-${item.key}s`">
                    {{ item.count }}
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
          <template #item="{ item }">
            <v-tabs-window-item class="bg-white pt-2 px-4" :value="item.key">
              <div v-if="item.key === 'student'">
                <div class="my-3">
                  <h2 id="student-results-page-header" class="font-size-18 font-weight-regular">
                    {{ pluralize('student', results.totalStudentCount) }}
                    <span v-if="searchPhraseSubmitted">
                      matching <span class="font-weight-500">{{ searchPhraseSubmitted }}</span>
                    </span>
                  </h2>
                  <div v-if="results.totalStudentCount > 50" class="font-size-14">
                    Showing the first 50 students.
                  </div>
                </div>
                <CuratedGroupSelector
                  context-description="Search"
                  domain="default"
                  :students="results.students"
                />
                <SortableStudents
                  domain="default"
                  :students="results.students"
                  :options="{
                    includeCuratedCheckbox: true,
                    sortBy: 'lastName',
                    reverse: false
                  }"
                />
              </div>
              <div v-if="item.key === 'admit'">
                <div class="mb-3">
                  <h2 id="admit-results-page-header" class="font-size-18 font-weight-regular mb-3">
                    {{ pluralize('admitted student', results.totalAdmitCount, {0: 'Zero', 1: 'One'}) }}
                    <span v-if="searchPhraseSubmitted"> matching <span class="font-weight-500">{{ searchPhraseSubmitted }}</span></span>
                  </h2>
                  <div v-if="results.totalAdmitCount" class="mb-2 ml-1">
                    <AdmitDataWarning :updated-at="_get(results.admits, '[0].updatedAt')" />
                  </div>
                </div>
                <div v-if="results.totalAdmitCount">
                  <div v-if="_size(results.admits) < results.totalAdmitCount" class="mb-2">
                    Showing the first {{ _size(results.admits) }} admitted students.
                  </div>
                  <CuratedGroupSelector
                    context-description="Search"
                    domain="admitted_students"
                    :students="results.admits"
                  />
                  <SortableAdmits :admitted-students="results.admits" />
                </div>
              </div>
              <div v-if="item.key === 'course'">
                <h2
                  id="course-results-page-h1"
                  class="font-size-18 font-weight-regular mb-3"
                  :class="!results.totalStudentCount && !!results.totalCourseCount && !_size(results.notes) ? 'page-section-header' : 'font-size-18'"
                >
                  {{ pluralize('class', results.totalCourseCount, {0: 'Zero', 1: 'One'}, 'es') }}
                  matching <span class="font-weight-500">{{ searchPhraseSubmitted }}</span>
                </h2>
                <div v-if="results.courses.length < results.totalCourseCount">
                  Showing the first {{ results.courses.length }} classes.
                </div>
                <SortableCourses
                  v-if="results.courses.length"
                  :courses="results.courses"
                />
              </div>
              <div v-if="item.key === 'note'">
                <h2 id="note-results-page-header" class="font-size-18 font-weight-regular mb-3">
                  {{ _size(results.notes) }}{{ completeNoteResults ? '' : '+' }}
                  {{ _size(results.notes) === 1 ? 'advising note' : 'advising notes' }}
                  <span v-if="searchPhraseSubmitted"> with <span class="font-weight-500">{{ searchPhraseSubmitted }}</span></span>
                </h2>
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
                <h2 id="appointment-results-page-header" class="font-size-18 font-weight-regular mb-3">
                  {{ _size(results.appointments) }}{{ completeAppointmentResults ? '' : '+' }}
                  {{ _size(results.appointments) === 1 ? 'advising appointment' : 'advising appointments' }}
                  <span v-if="searchPhraseSubmitted"> with <span class="font-weight-500">{{ searchPhraseSubmitted }}</span></span>
                </h2>
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

<script>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdvisingNoteSnippet from '@/components/search/AdvisingNoteSnippet'
import AppointmentSnippet from '@/components/search/AppointmentSnippet'
import Context from '@/mixins/Context'
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector'
import SearchSession from '@/mixins/SearchSession'
import SectionSpinner from '@/components/util/SectionSpinner'
import SortableAdmits from '@/components/admit/SortableAdmits'
import SortableCourses from '@/components/search/SortableCourses'
import SortableStudents from '@/components/search/SortableStudents'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
import {mdiAccountSchool, mdiCalendarCheck, mdiHumanGreeting, mdiHumanMaleBoardPoll, mdiNoteEditOutline} from '@mdi/js'
import {search, searchAdmittedStudents} from '@/api/search'

export default {
  name: 'SearchResults',
  components: {
    AdmitDataWarning,
    AdvisingNoteSnippet,
    AppointmentSnippet,
    CuratedGroupSelector,
    SortableStudents,
    SectionSpinner,
    SortableAdmits,
    SortableCourses
  },
  mixins: [Context, SearchSession, Util],
  data: () => ({
    appointmentOptions: {
      limit: 20,
      offset: 0
    },
    loadingAdditionalAppointments: undefined,
    loadingAdditionalNotes: undefined,
    noteAndAppointmentOptions: {
      advisorCsid: undefined,
      advisorUid: undefined,
      studentCsid: undefined,
      topic: undefined,
      dateFrom: undefined,
      dateTo: undefined,
    },
    noteOptions: {
      limit: 20,
      offset: 0
    },
    results: {
      admits: null,
      appointments: null,
      courses: null,
      notes: null,
      students: null,
      totalCourseCount: null,
      totalStudentCount: null
    },
    searchPhraseSubmitted: undefined,
    tab: undefined
  }),
  computed: {
    completeAppointmentResults() {
      return this._size(this.results.appointments) < this.appointmentOptions.limit + this.appointmentOptions.offset
    },
    completeNoteResults() {
      return this._size(this.results.notes) < this.noteOptions.limit + this.noteOptions.offset
    },
    tabs() {
      const tabs = []
      const push = (key, count, included, icon) => {
        if (included) {
          tabs.push({count, icon, key})
        }
      }
      push('student', this.results.totalStudentCount || 0, this.includeStudents, mdiAccountSchool)
      push('admit', this.results.totalAdmitCount || 0, this.includeAdmits, mdiHumanGreeting)
      push('course', this.results.totalCourseCount || 0, this.includeCourses, mdiHumanMaleBoardPoll)
      push('note', this._size(this.results.notes), this.includeNotes, mdiNoteEditOutline)
      push('appointment', this._size(this.results.appointments), this.includeNotes, mdiCalendarCheck)
      return tabs
    },
    hasSearchResults() {
      return this.results.totalStudentCount
        || this.results.totalCourseCount
        || this.results.totalAdmitCount
        || this._size(this.results.notes)
        || this._size(this.results.appointments)
    }
  },
  mounted() {
    // Update 'queryText' in Vuex store per 'q' arg. If arg is null then preserve existing 'queryText' value.
    this.queryText = this.$route.query.q || this.queryText
    // Take a snapshot of the submitted search phrase. The 'queryText' value (in store) may change.
    this.searchPhraseSubmitted = this.queryText
    this.includeAdmits = this.toBoolean(this.$route.query.admits)
    this.includeCourses = this.toBoolean(this.$route.query.courses)
    this.includeNotesAndAppointments = this.toBoolean(this.$route.query.notes)
    this.includeStudents = this.toBoolean(this.$route.query.students)
    if (this.includeNotesAndAppointments) {
      this.noteAndAppointmentOptions.advisorCsid = this.$route.query.advisorCsid
      this.noteAndAppointmentOptions.advisorUid = this.$route.query.advisorUid
      this.noteAndAppointmentOptions.studentCsid = this.$route.query.studentCsid
      this.noteAndAppointmentOptions.topic = this.$route.query.noteTopic
      this.noteAndAppointmentOptions.dateFrom = this.$route.query.noteDateFrom
      this.noteAndAppointmentOptions.dateTo = this.$route.query.noteDateTo
    }
    if (this.queryText || this.includeNotesAndAppointments) {
      this.isSearching = true
      alertScreenReader(`Searching for '${this.queryText}'`)
      let queries = []
      if (this.includeCourses || this.includeNotesAndAppointments || this.includeStudents) {
        queries.push(
          search(
            this.queryText,
            this.includeNotesAndAppointments,
            this.includeCourses,
            this.includeNotesAndAppointments,
            this.includeStudents,
            this._extend({}, this.noteAndAppointmentOptions, this.appointmentOptions),
            this._extend({}, this.noteAndAppointmentOptions, this.noteOptions)
          )
        )
      }
      if (this.includeAdmits && this._trim(this.queryText)) {
        queries.push(searchAdmittedStudents(this.queryText))
      }
      Promise.all(queries).then(responses => {
        this._each(responses, (response) => this._merge(this.results, response))
        this._each(this.results.students, student => {
          student.alertCount = student.alertCount || 0
          student.term = student.term || {}
          student.term.enrolledUnits = student.term.enrolledUnits || 0
        })
      })
        .then(() => {
          this.loadingComplete()
          const totalCount = this.toInt(this.results.totalCourseCount, 0) + this.toInt(this.results.totalStudentCount, 0)
          const focusId = totalCount ? 'page-header' : 'page-header-no-results'
          this.putFocusNextTick(focusId)
        }).finally(() => {
          this.isSearching = false
        })
    } else {
      this.$router.push({path: '/'}, this._noop)
    }
  },
  methods: {
    describe(noun, count) {
      return count > 0 ? `${count} ${this._capitalize(noun)}${count === 1 ? '' : 's'}, ` : ''
    },
    fetchMoreAppointments() {
      this.appointmentOptions.offset = this.appointmentOptions.offset + this.appointmentOptions.limit
      this.appointmentOptions.limit = 20
      this.loadingAdditionalAppointments = true
      search(
        this.queryText,
        true,
        false,
        false,
        false,
        this._extend({}, this.noteAndAppointmentOptions, this.appointmentOptions),
        null
      )
        .then(data => {
          this.results.appointments = this._concat(this.results.appointments, data.appointments)
          this.loadingAdditionalAppointments = false
        })
    },
    fetchMoreNotes() {
      this.noteOptions.offset = this.noteOptions.offset + this.noteOptions.limit
      this.noteOptions.limit = 20
      this.loadingAdditionalNotes = true
      search(
        this.queryText,
        false,
        false,
        true,
        false,
        null,
        this._extend({}, this.noteAndAppointmentOptions, this.noteOptions)
      )
        .then(data => {
          this.results.notes = this._concat(this.results.notes, data.notes)
          this.loadingAdditionalNotes = false
        })
    },
    openAdvancedSearch() {
      this.showAdvancedSearch = true
      alertScreenReader('Advanced search is open')
    }
  }
}
</script>

<style scoped>
li {
  margin-left: 24px;
  padding-top: 6px;
}
</style>
