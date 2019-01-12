<template>
  <div class="m-3">
    <Spinner/>
    <div v-if="error">
      <h1 role="alert" aria-live="passive">Error</h1>
      <div class="faint-text">
        <span role="alert" aria-live="passive" v-if="error.message">{{ error.message }}</span>
        <span role="alert" aria-live="passive" v-if="!error.message">Sorry, there was an error retrieving data.</span>
      </div>
    </div>
    <div v-if="!loading && !error && !results.totalStudentCount && !results.totalCourseCount">
      <h1 role="alert" aria-live="passive">No results matching '{{ phrase }}'</h1>
      <div>Suggestions:</div>
      <ul>
        <li>Keep your search term simple.</li>
        <li>Check your spelling and try again.</li>
        <li>Search classes by section title, e.g., <strong>AMERSTD 10</strong>.</li>
        <li>Abbreviations of section titles may not return results; <strong>COMPSCI 161</strong> instead of <strong>CS 161</strong>.</li>
      </ul>
    </div>
    <div tabindex="0" focus-on="!loading && results.totalStudentCount">
      <div v-if="!loading && !error && results.totalStudentCount">
        <h1>{{ 'student' | pluralize(results.totalStudentCount) }} matching '{{ phrase }}'</h1>
        <div v-if="results.totalStudentCount > limit">
          Showing the first {{ limit }} students.
        </div>
      </div>
    </div>
    <div class="cohort-column-results" v-if="!loading && !error && results.totalStudentCount">
      <div class="search-header-curated-cohort">
        <CuratedGroupSelector :students="results.students"/>
      </div>
      <div>
        <SortableStudents :students="results.students" :options="studentListOptions"/>
      </div>
    </div>
    <SortableCourseList :searchPhrase="phrase"
                        :courses="results.courses"
                        :totalCourseCount="results.totalCourseCount"
                        :renderPrimaryHeader="!!(!results.totalStudentCount && results.totalCourseCount)"
                        v-if="!loading"/>
  </div>
</template>

<script>
import _ from 'lodash';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import Loading from '@/mixins/Loading';
import SortableCourseList from '@/components/course/SortableCourseList';
import SortableStudents from '@/components/search/SortableStudents';
import Spinner from '@/components/util/Spinner';
import UserMetadata from '@/mixins/UserMetadata';
import { search } from '@/api/student';

export default {
  name: 'Search',
  beforeRouteUpdate(to, from, next) {
    let phrase = _.trim(to.query.q);
    let includeCourses = _.trim(to.query.includeCourses);
    if (phrase) {
      this.startLoading();
      this.performSearch(phrase, includeCourses);
    }
    next();
  },
  mixins: [Loading, UserMetadata],
  components: {
    SortableCourseList,
    CuratedGroupSelector,
    SortableStudents,
    Spinner
  },
  data: () => ({
    error: null,
    inactiveAsc: undefined,
    includeCourses: undefined,
    isInactiveCoe: undefined,
    limit: 50,
    phrase: null,
    results: {
      courses: null,
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
    this.includeCourses = this.$route.query.includeCourses;
    this.performSearch();
  },
  methods: {
    performSearch(phrase, includeCourses) {
      this.phrase = phrase || this.phrase;
      this.includeCourses = _.isNil(includeCourses)
        ? this.includeCourses
        : includeCourses;
      if (this.phrase) {
        // In arrow function below, 'this' does NOT reference Search component. Using 'self' as an alias is sufficient.
        const self = this;
        search(
          this.phrase,
          this.includeCourses,
          this.isAscUser ? true : null,
          this.isCoeUser ? false : null
        )
          .then(data => {
            self.results.courses = data.courses;
            self.results.students = data.students;
            _.each(self.results.students, student => {
              student.alertCount = student.alertCount || 0;
              student.term = student.term || {};
              student.term.enrolledUnits = student.term.enrolledUnits || 0;
            });
            self.results.totalCourseCount = data.totalCourseCount;
            self.results.totalStudentCount = data.totalStudentCount;
          })
          .then(() => {
            self.loaded();
          });
      }
    }
  }
};
</script>
