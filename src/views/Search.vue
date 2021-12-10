<template>
  <div class="m-3">
    <Spinner />
    <div v-if="loading || (results.totalStudentCount || results.totalCourseCount || results.totalAdmitCount || $_.size(results.notes) || $_.size(results.appointments))">
      <h1 id="page-header" class="sr-only" tabindex="-1">Search Results</h1>
    </div>
    <div v-if="!loading && !results.totalStudentCount && !results.totalCourseCount && !results.totalAdmitCount && !$_.size(results.notes) && !$_.size(results.appointments)">
      <h1 id="page-header-no-results" class="page-section-header" tabindex="-1">
        No results<span v-if="phrase"> matching '{{ phrase }}'</span>
      </h1>
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
    <div v-if="!loading && $_.size(results.admits)">
      <h2 id="admit-results-page-header" class="page-section-header">
        {{ pluralize('admitted student', results.totalAdmitCount) }}<span v-if="phrase">  matching '{{ phrase }}'</span>
      </h2>
      <div v-if="$_.size(results.admits) < results.totalAdmitCount">
        Showing the first {{ $_.size(results.admits) }} admitted students.
      </div>
      <AdmitDataWarning :updated-at="$_.get(results.admits, '[0].updatedAt')" />
      <div class="search-header-curated-cohort">
        <SelectAll
          context-description="Search"
          domain="admitted_students"
          :ga-event-tracker="$ga.searchEvent"
          :students="results.admits"
        />
      </div>
      <div>
        <SortableAdmits :admitted-students="results.admits" />
      </div>
    </div>
    <div v-if="!loading && results.totalStudentCount">
      <h2 id="student-results-page-header" class="page-section-header">
        {{ pluralize('student', results.totalStudentCount) }}<span v-if="phrase">  matching '{{ phrase }}'</span>
      </h2>
      <div v-if="results.totalStudentCount > studentLimit">
        Showing the first {{ studentLimit }} students.
      </div>
    </div>
    <div v-if="!loading && results.totalStudentCount" class="cohort-column-results">
      <div class="search-header-curated-cohort">
        <SelectAll
          context-description="Search"
          domain="default"
          :ga-event-tracker="$ga.searchEvent"
          :students="results.students"
        />
      </div>
      <div>
        <SortableStudents
          domain="default"
          :students="results.students"
          :options="studentListOptions"
        />
      </div>
    </div>
    <div v-if="!loading && results.totalCourseCount" class="pt-4">
      <SortableCourseList
        :search-phrase="phrase"
        :courses="results.courses"
        :total-course-count="results.totalCourseCount"
        :render-primary-header="!results.totalStudentCount && !!results.totalCourseCount && !$_.size(results.notes)"
      />
    </div>
    <div v-if="!loading && $_.size(results.notes)" class="pt-4">
      <h2 id="search-results-category-header-notes" class="page-section-header">
        {{ $_.size(results.notes) }}{{ completeNoteResults ? '' : '+' }}
        {{ $_.size(results.notes) === 1 ? 'advising note' : 'advising notes' }}
        <span v-if="phrase"> with '{{ phrase }}'</span>
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
    <div v-if="!loading && $_.size(results.appointments)" class="pt-4">
      <h2 id="search-results-category-header-appointments" class="page-section-header">
        {{ $_.size(results.appointments) }}{{ completeAppointmentResults ? '' : '+' }}
        {{ $_.size(results.appointments) === 1 ? 'advising appointment' : 'advising appointments' }}
        <span v-if="phrase"> with '{{ phrase }}'</span>
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
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdvisingNoteSnippet from '@/components/search/AdvisingNoteSnippet'
import AppointmentSnippet from '@/components/search/AppointmentSnippet'
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import SectionSpinner from '@/components/util/SectionSpinner'
import SelectAll from '@/components/curated/dropdown/SelectAll'
import SortableAdmits from '@/components/admit/SortableAdmits'
import SortableCourseList from '@/components/course/SortableCourseList'
import SortableStudents from '@/components/search/SortableStudents'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {search, searchAdmittedStudents} from '@/api/search'

export default {
  name: 'Search',
  components: {
    AdmitDataWarning,
    AdvisingNoteSnippet,
    AppointmentSnippet,
    SectionSpinner,
    SelectAll,
    SortableAdmits,
    SortableCourseList,
    SortableStudents,
    Spinner
  },
  mixins: [Context, Loading, Util],
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
    phrase: null,
    results: {
      admits: null,
      appointments: null,
      courses: null,
      notes: null,
      students: null,
      totalCourseCount: null,
      totalStudentCount: null
    },
    studentLimit: 50,
    studentListOptions: {
      includeCuratedCheckbox: true,
      sortBy: 'lastName',
      reverse: false
    }
  }),
  computed: {
    completeAppointmentResults() {
      return this.$_.size(this.results.appointments) < this.appointmentOptions.limit + this.appointmentOptions.offset
    },
    completeNoteResults() {
      return this.$_.size(this.results.notes) < this.noteOptions.limit + this.noteOptions.offset
    }
  },
  mounted() {
    this.phrase = this.$route.query.q
    const includeAdmits = this.toBoolean(this.$route.query.admits)
    const includeCourses = this.toBoolean(this.$route.query.courses)
    const includeNotesAndAppointments = this.toBoolean(this.$route.query.notes)
    const includeStudents = this.toBoolean(this.$route.query.students)
    if (includeNotesAndAppointments) {
      this.noteAndAppointmentOptions.advisorCsid = this.$route.query.advisorCsid
      this.noteAndAppointmentOptions.advisorUid = this.$route.query.advisorUid
      this.noteAndAppointmentOptions.studentCsid = this.$route.query.studentCsid
      this.noteAndAppointmentOptions.topic = this.$route.query.noteTopic
      this.noteAndAppointmentOptions.dateFrom = this.$route.query.noteDateFrom
      this.noteAndAppointmentOptions.dateTo = this.$route.query.noteDateTo
    }
    if (this.phrase || includeNotesAndAppointments) {
      this.alertScreenReader(`Searching for '${this.phrase}'`)
      let queries = []
      if (includeCourses || includeNotesAndAppointments || includeStudents) {
        queries.push(
          search(
            this.phrase,
            includeNotesAndAppointments,
            includeCourses,
            includeNotesAndAppointments,
            includeStudents,
            this.$_.extend({}, this.noteAndAppointmentOptions, this.appointmentOptions),
            this.$_.extend({}, this.noteAndAppointmentOptions, this.noteOptions)
          )
        )
      }
      if (includeAdmits && this.$_.trim(this.phrase)) {
        queries.push(searchAdmittedStudents(this.phrase))
      }
      Promise.all(queries).then(responses => {
        this.$_.each(responses, (response) => this.$_.merge(this.results, response))
        this.$_.each(this.results.students, student => {
          student.alertCount = student.alertCount || 0
          student.term = student.term || {}
          student.term.enrolledUnits = student.term.enrolledUnits || 0
        })
      })
        .then(() => {
          this.loaded(this.describeResults())
          const totalCount =
            this.toInt(this.results.totalCourseCount, 0) +
            this.toInt(this.results.totalStudentCount, 0)
          const focusId = totalCount ? 'page-header' : 'page-header-no-results'
          this.$putFocusNextTick(focusId)
          this.$ga.searchEvent(
            `Search phrase: '${this.phrase || ''}'`,
            `Search with admits: ${includeAdmits}; courses: ${includeCourses}; notes: ${includeNotesAndAppointments}; students: ${includeStudents}`)
        })
    } else {
      this.$router.push({path: '/'}, this.$_.noop)
    }
  },
  methods: {
    describeResults() {
      const describe = (noun, count) => count > 0 ? `${count} ${noun}${count === 1 ? '' : 's'}, ` : ''
      let alert = `Search results include ${describe('Admits', this.results.totalAdmitCount)}`
      alert += describe('student', this.results.totalStudentCount)
      alert += describe('course', this.results.totalCourseCount)
      alert += describe('note', this.$_.size(this.results.notes))
      alert += describe('appointment', this.$_.size(this.results.appointments))
      return alert
    },
    fetchMoreAppointments() {
      this.appointmentOptions.offset = this.appointmentOptions.offset + this.appointmentOptions.limit
      this.appointmentOptions.limit = 20
      this.loadingAdditionalAppointments = true
      search(
        this.phrase,
        true,
        false,
        false,
        false,
        this.$_.extend({}, this.noteAndAppointmentOptions, this.appointmentOptions),
        null
      )
        .then(data => {
          this.results.appointments = this.$_.concat(this.results.appointments, data.appointments)
          this.loadingAdditionalAppointments = false
        })
    },
    fetchMoreNotes() {
      this.noteOptions.offset = this.noteOptions.offset + this.noteOptions.limit
      this.noteOptions.limit = 20
      this.loadingAdditionalNotes = true
      search(
        this.phrase,
        false,
        false,
        true,
        false,
        null,
        this.$_.extend({}, this.noteAndAppointmentOptions, this.noteOptions)
      )
        .then(data => {
          this.results.notes = this.$_.concat(this.results.notes, data.notes)
          this.loadingAdditionalNotes = false
        })
    }
  }
}
</script>

<style>
.advising-note-search-result {
  margin: 15px 0;
}
.advising-note-search-result-header {
  font-weight: 400;
  font-size: 18px;
  margin-bottom: 5px;
}
.advising-note-search-result-header-link {
   font-weight: 600;
}
.advising-note-search-result-footer {
  color: #999;
  font-size: 14px;
}
.advising-note-search-result-snippet {
  font-size: 16px;
  line-height: 1.3em;
  margin: 5px 0;
}
.search-header-curated-cohort {
  align-items: center;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  padding: 20px 0 10px 0;
}
</style>
