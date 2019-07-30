<template>
  <div class="m-3">
    <Spinner />
    <div v-if="!loading && !results.totalStudentCount && !results.totalCourseCount && !size(results.notes)">
      <h1
        id="page-header-no-results"
        class="page-section-header"
        aria-live="polite">
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
    <div
      v-if="!loading && results.totalStudentCount"
      tabindex="0">
      <h1 id="student-results-page-header" class="page-section-header">
        {{ 'student' | pluralize(results.totalStudentCount) }}<span v-if="phrase">  matching '{{ phrase }}'</span>
      </h1>
      <div v-if="results.totalStudentCount > studentLimit">
        Showing the first {{ studentLimit }} students.
      </div>
    </div>
    <div v-if="!loading && results.totalStudentCount" class="cohort-column-results">
      <div class="search-header-curated-cohort">
        <CuratedGroupSelector
          context-description="Search"
          :ga-event-tracker="gaSearchEvent"
          :students="results.students" />
      </div>
      <div>
        <SortableStudents :students="results.students" :options="studentListOptions" />
      </div>
    </div>
    <div v-if="!loading && results.totalCourseCount" class="pt-4">
      <SortableCourseList
        :search-phrase="phrase"
        :courses="results.courses"
        :total-course-count="results.totalCourseCount"
        :render-primary-header="!results.totalStudentCount && !!results.totalCourseCount && !size(results.notes)" />
    </div>
    <div v-if="!loading && size(results.notes)" class="pt-4">
      <h2
        id="search-results-category-header-notes"
        class="page-section-header">
        {{ size(results.notes) }}{{ completeNoteResults ? '' : '+' }}
        {{ size(results.notes) === 1 ? 'advising note' : 'advising notes' }}
        <span v-if="phrase"> with '{{ phrase }}'</span>
      </h2>
      <AdvisingNoteSnippet
        v-for="advisingNote in results.notes"
        :key="advisingNote.id"
        :note="advisingNote" />
      <div class="text-center">
        <b-btn
          v-if="!completeNoteResults"
          id="fetch-more-notes"
          variant="link"
          @click.prevent="fetchMoreNotes()">
          Show additional advising notes
        </b-btn>
        <SectionSpinner name="Notes" :loading="loadingAdditionalNotes" />
      </div>
    </div>
  </div>
</template>

<script>
import AdvisingNoteSnippet from '@/components/search/AdvisingNoteSnippet';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import Loading from '@/mixins/Loading';
import SectionSpinner from '@/components/util/SectionSpinner';
import SortableCourseList from '@/components/course/SortableCourseList';
import SortableStudents from '@/components/search/SortableStudents';
import Spinner from '@/components/util/Spinner';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { search } from '@/api/search';

export default {
  name: 'Search',
  components: {
    AdvisingNoteSnippet,
    CuratedGroupSelector,
    SectionSpinner,
    SortableCourseList,
    SortableStudents,
    Spinner
  },
  mixins: [Loading, UserMetadata, Util],
  data: () => ({
    studentLimit: 50,
    loadingAdditionalNotes: undefined,
    noteOptions: {
      authorCsid: undefined,
      studentCsid: undefined,
      topic: undefined,
      dateFrom: undefined,
      dateTo: undefined,
      limit: 100,
      offset: 0
    },
    phrase: null,
    results: {
      courses: null,
      notes: null,
      students: null,
      totalCourseCount: null,
      totalStudentCount: null
    },
    studentListOptions: {
      includeCuratedCheckbox: true,
      sortBy: 'lastName',
      reverse: false
    }
  }),
  computed: {
    completeNoteResults() {
      return this.size(this.results.notes) < this.noteOptions.limit + this.noteOptions.offset;
    }
  },
  mounted() {
    this.phrase = this.$route.query.q;
    const includeCourses = this.$route.query.courses;
    const includeNotes = this.$route.query.notes;
    const includeStudents = this.$route.query.students;
    if (includeNotes) {
      this.noteOptions.authorCsid = this.$route.query.authorCsid;
      this.noteOptions.studentCsid = this.$route.query.studentCsid;
      this.noteOptions.topic = this.$route.query.noteTopic;
      this.noteOptions.dateFrom = this.$route.query.noteDateFrom;
      this.noteOptions.dateTo = this.$route.query.noteDateTo;
    }
    if (this.phrase || includeNotes) {
      search(
        this.phrase,
        this.isNil(includeCourses) ? false : includeCourses,
        this.isNil(includeNotes) ? false : includeNotes,
        this.isNil(includeStudents) ? false : includeStudents,
        this.noteOptions,
      )
        .then(data => {
          this.assign(this.results, data);
          this.each(this.results.students, student => {
            student.alertCount = student.alertCount || 0;
            student.term = student.term || {};
            student.term.enrolledUnits = student.term.enrolledUnits || 0;
          });
        })
        .then(() => {
          this.loaded();
          const totalCount =
            this.toInt(this.results.totalCourseCount, 0) +
            this.toInt(this.results.totalStudentCount, 0);
          const focusId = totalCount ? 'page-header' : 'page-header-no-results';
          this.putFocusNextTick(focusId);
          this.gaSearchEvent({
            action: 'results',
            name: includeCourses ? 'classes and students' : 'students'
          });
        });
    }
  },
  methods: {
    fetchMoreNotes() {
      this.noteOptions.offset = this.noteOptions.offset + this.noteOptions.limit;
      this.noteOptions.limit = 20;
      this.loadingAdditionalNotes = true;
      search(
        this.phrase,
        false,
        true,
        false,
        this.noteOptions,
      )
        .then(data => {
          this.results.notes = this.concat(this.results.notes, data.notes);
          this.loadingAdditionalNotes = false;
        });
    }
  }
};
</script>

<style scoped>
.search-header-curated-cohort {
  align-items: center;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  padding: 20px 0 10px 0;
}
</style>
