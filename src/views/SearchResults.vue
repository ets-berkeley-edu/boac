<template>
  <div class="m-3">
    <Spinner />
    <SearchResultsHeader :results="results" />
    <div v-if="!loading && _size(results.admits)">
      <hr class="section-divider" />
      <AdmittedStudentResults
        :results="results"
        :search-phrase="searchPhraseSubmitted"
      />
    </div>
    <div v-if="!loading && results.totalStudentCount">
      <hr class="section-divider" />
      <StudentResults
        :results="results"
        :search-phrase="searchPhraseSubmitted"
      />
    </div>
    <div v-if="!loading && results.totalCourseCount" class="pt-4">
      <hr class="section-divider" />
      <SortableCourses
        :courses="results.courses"
        :header-class-name="!results.totalStudentCount && !!results.totalCourseCount && !_size(results.notes) ? 'page-section-header' : 'font-size-18'"
        :search-phrase="searchPhraseSubmitted"
        :total-course-count="results.totalCourseCount"
      />
    </div>
    <div v-if="!loading && _size(results.notes)" class="pt-4">
      <hr class="section-divider" />
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
        <b-btn
          v-if="!completeNoteResults"
          id="fetch-more-notes"
          variant="link"
          @click.prevent="fetchMoreNotes"
        >
          Show additional advising notes
        </b-btn>
        <SectionSpinner :loading="loadingAdditionalNotes" />
      </div>
    </div>
    <div v-if="!loading && _size(results.appointments)" class="pt-4">
      <hr class="section-divider" />
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
        <b-btn
          v-if="!completeAppointmentResults"
          id="fetch-more-appointments"
          variant="link"
          @click.prevent="fetchMoreAppointments"
        >
          Show additional advising appointments
        </b-btn>
        <SectionSpinner :loading="loadingAdditionalAppointments" />
      </div>
    </div>
  </div>
</template>

<script>
import AdvisingNoteSnippet from '@/components/search/AdvisingNoteSnippet'
import AppointmentSnippet from '@/components/search/AppointmentSnippet'
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import AdmittedStudentResults from '@/components/search/AdmittedStudentResults'
import SearchResultsHeader from '@/components/search/SearchResultsHeader'
import SearchSession from '@/mixins/SearchSession'
import SectionSpinner from '@/components/util/SectionSpinner'
import SortableCourses from '@/components/search/SortableCourses'
import Spinner from '@/components/util/Spinner'
import StudentResults from '@/components/search/StudentResults'
import Util from '@/mixins/Util'
import {search, searchAdmittedStudents} from '@/api/search'

export default {
  name: 'SearchResults',
  components: {
    AdmittedStudentResults,
    AdvisingNoteSnippet,
    AppointmentSnippet,
    SearchResultsHeader,
    SectionSpinner,
    SortableCourses,
    Spinner,
    StudentResults
  },
  mixins: [Context, Loading, SearchSession, Util],
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
    searchPhraseSubmitted: undefined
  }),
  computed: {
    completeAppointmentResults() {
      return this._size(this.results.appointments) < this.appointmentOptions.limit + this.appointmentOptions.offset
    },
    completeNoteResults() {
      return this._size(this.results.notes) < this.noteOptions.limit + this.noteOptions.offset
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
      this.$announcer.polite(`Searching for '${this.queryText}'`)
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
          this.loaded(this.describeResults())
          const totalCount = this.toInt(this.results.totalCourseCount, 0) + this.toInt(this.results.totalStudentCount, 0)
          const focusId = totalCount ? 'page-header' : 'page-header-no-results'
          this.$putFocusNextTick(focusId)
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
    }
  }
}
</script>
