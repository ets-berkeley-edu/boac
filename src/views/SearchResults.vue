<template>
  <div class="pa-3">
    <Spinner />
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
    <div v-if="!loading">
      <div v-if="!hasSearchResults" id="page-header-no-results">
        <div class="font-weight-500 pt-2">No matching records found.</div>
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
      <v-sheet v-if="results.totalStudentCount">
        <v-tabs
          v-model="tab"
          color="primary"
          :direction="$vuetify.display.mdAndUp ? 'horizontal' : 'vertical'"
          :items="tabs"
          slider-color="primary"
        >
          <template #tab="{ item }">
            <v-tab
              :prepend-icon="item.icon"
              :text="item.text"
              :value="item.key"
              class="text-none"
            />
          </template>
          <template #item="{ item }">
            <v-tabs-window-item :value="item.key" class="pa-4">
              <div v-if="item.key === 'admit'">
                <h2 id="admit-results-page-header" class="font-size-18">
                  {{ pluralize('admitted student', results.totalAdmitCount) }}<span v-if="searchPhraseSubmitted">  matching '{{ searchPhraseSubmitted }}'</span>
                </h2>
                <div v-if="results.totalAdmitCount">
                  <div class="mb-2 ml-1">
                    <AdmitDataWarning :updated-at="_get(results.admits, '[0].updatedAt')" />
                  </div>
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
              <div v-if="item.key === 'student'">
                <h2 id="student-results-page-header" class="font-size-18">
                  {{ pluralize('student', results.totalStudentCount) }}<span v-if="searchPhraseSubmitted">  matching '{{ searchPhraseSubmitted }}'</span>
                </h2>
                <div v-if="results.totalStudentCount > 50" class="mb-2">
                  Showing the first 50 students.
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
              <div v-if="item.key === 'course'">
                <SortableCourses
                  :courses="results.courses"
                  :header-class-name="!results.totalStudentCount && !!results.totalCourseCount && !_size(results.notes) ? 'page-section-header' : 'font-size-18'"
                  :search-phrase="searchPhraseSubmitted"
                  :total-course-count="results.totalCourseCount"
                />
              </div>
              <div v-if="item.key === 'note'">
                <h2 id="note-results-page-header" class="font-size-18">
                  {{ _size(results.notes) }}{{ completeNoteResults ? '' : '+' }}
                  {{ _size(results.notes) === 1 ? 'advising note' : 'advising notes' }}
                  <span v-if="searchPhraseSubmitted"> with '{{ searchPhraseSubmitted }}'</span>
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
                <h2 id="appointment-results-page-header" class="font-size-18">
                  {{ _size(results.appointments) }}{{ completeAppointmentResults ? '' : '+' }}
                  {{ _size(results.appointments) === 1 ? 'advising appointment' : 'advising appointments' }}
                  <span v-if="searchPhraseSubmitted"> with '{{ searchPhraseSubmitted }}'</span>
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
      </v-sheet>
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
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {mdiAccountSchool, mdiCalendarCheck, mdiHumanGreeting, mdiHumanMaleBoardPoll, mdiNoteEditOutline} from '@mdi/js'
import {pluralize} from '@/lib/utils'
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
    SortableCourses,
    Spinner
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
          tabs.push({icon, key, text: pluralize(key, count)})
        }
      }
      push('admit', this.results.totalAdmitCount || 0, this.includeAdmits, mdiHumanGreeting)
      push('student', this.results.totalStudentCount || 0, this.includeStudents, mdiAccountSchool)
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
      this.alertScreenReader(`Searching for '${this.queryText}'`)
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
          this.loadingComplete(this.describeResults())
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
    describeResults() {
      const describe = (noun, count) => count > 0 ? `${count} ${noun}${count === 1 ? '' : 's'}, ` : ''
      let alert = `Search results include ${describe('Admits', this.results.totalAdmitCount)}`
      alert += describe('student', this.results.totalStudentCount)
      alert += describe('course', this.results.totalCourseCount)
      alert += describe('note', this._size(this.results.notes))
      alert += describe('appointment', this._size(this.results.appointments))
      return alert
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
      this.alertScreenReader('Advanced search is open')
    }
  }
}
</script>
