<template>
  <div class="m-3">
    <Spinner />
    <div v-if="!loading && !results.totalStudentCount && !results.totalCourseCount && !size(results.notes)">
      <h1
        id="page-header-no-results"
        class="page-section-header"
        role="alert"
        aria-live="passive">
        No results matching '{{ phrase }}'
      </h1>
      <div>Suggestions:</div>
      <ul>
        <li>Keep your search term simple.</li>
        <li>Check your spelling and try again.</li>
        <li>Search classes by section title, e.g., <strong>AMERSTD 10</strong>.</li>
        <li>Abbreviations of section titles may not return results; <strong>COMPSCI 161</strong> instead of <strong>CS 161</strong>.</li>
      </ul>
    </div>
    <div
      v-if="!loading && results.totalStudentCount"
      tabindex="0">
      <h1 id="page-header" class="page-section-header">
        {{ 'student' | pluralize(results.totalStudentCount) }} matching '{{ phrase }}'
      </h1>
      <div v-if="results.totalStudentCount > limit">
        Showing the first {{ limit }} students.
      </div>
    </div>
    <div v-if="!loading && results.totalStudentCount" class="cohort-column-results">
      <div class="search-header-curated-cohort">
        <CuratedGroupSelector
          context-description="Search"
          :students="results.students" />
      </div>
      <div>
        <SortableStudents :students="results.students" :options="studentListOptions" />
      </div>
    </div>
    <div v-if="!loading && results.totalCourseCount">
      <SortableCourseList
        :search-phrase="phrase"
        :courses="results.courses"
        :total-course-count="results.totalCourseCount"
        :render-primary-header="!results.totalStudentCount && !!results.totalCourseCount && !size(results.notes)" />
    </div>
    <div v-if="!loading && size(results.notes)">
      <h2
        id="search-results-category-header-notes"
        class="page-section-header">
        {{ size(results.notes) }}{{ size(results.notes) === 20 ? '+' : '' }}
        {{ size(results.notes) === 1 ? 'advising note' : 'advising notes' }}
        with '{{ phrase }}'
      </h2>
      <AdvisingNoteSnippet
        v-for="advisingNote in results.notes"
        :key="advisingNote.noteId"
        :note="advisingNote" />
    </div>
  </div>
</template>

<script>
import AdvisingNoteSnippet from '@/components/search/AdvisingNoteSnippet';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import Loading from '@/mixins/Loading';
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
    SortableCourseList,
    SortableStudents,
    Spinner
  },
  mixins: [GoogleAnalytics, Loading, UserMetadata, Util],
  data: () => ({
    limit: 50,
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
  created() {
    this.phrase = this.$route.query.q;
    const includeCourses = this.$route.query.courses;
    const includeNotes = this.$route.query.notes;
    const includeStudents = this.$route.query.students;
    if (this.phrase) {
      search(
        this.phrase,
        this.isNil(includeCourses) ? false : includeCourses,
        this.isNil(includeNotes) ? false : includeNotes,
        this.isNil(includeStudents) ? false : includeStudents,
        this.isAscUser ? false : null,
        this.isCoeUser ? false : null
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
          this.gaEvent(
            'Search',
            'results',
            includeCourses ? 'classes and students' : 'students',
            totalCount
          );
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
