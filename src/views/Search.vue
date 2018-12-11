<template>
  <div class="p-3">
    <Spinner/>
    <div v-if="error">
      <h1 role="alert" aria-live="passive">Error</h1>
      <div class="faint-text">
        <span role="alert" aria-live="passive" v-if="error.message">{{ error.message }}</span>
        <span role="alert" aria-live="passive" v-if="!error.message">Sorry, there was an error retrieving data.</span>
      </div>
    </div>
    <div v-if="!loading && !error && !totalStudentCount && !totalCourseCount">
      <h1 role="alert" aria-live="passive">No results matching '{{ phrase }}'</h1>
      <div>Suggestions:</div>
      <ul>
        <li>Keep your search term simple.</li>
        <li>Check your spelling and try again.</li>
        <li>Search classes by section title, e.g., <strong>AMERSTD 10</strong>.</li>
        <li>Abbreviations of section titles may not return results; <strong>COMPSCI 161</strong> instead of <strong>CS 161</strong>.</li>
      </ul>
    </div>
    <div tabindex="0" focus-on="!loading && totalStudentCount">
      <div v-if="!loading && !error && totalStudentCount">
        <h1>{{ 'student' | pluralize(totalStudentCount) }} matching '{{ phrase }}'</h1>
        <div v-if="totalStudentCount > limit">
          Showing the first {{limit}} students.
        </div>
      </div>
    </div>
    <div class="cohort-column-results" v-if="!loading && !error && totalStudentCount">
      <div class="search-header-curated-cohort">
        <CuratedGroupSelector :students="students"/>
      </div>
      <div>
        <SortableStudents :students="students" :options="studentListOptions"/>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import { search } from '@/api/student';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import Spinner from '@/components/Spinner.vue';
import Loading from '@/mixins/Loading.vue';
import SortableStudents from '@/components/search/SortableStudents';

export default {
  name: 'Search',
  beforeRouteUpdate(to, from, next) {
    this.phrase = _.trim(to.query.q);
    if (this.phrase) {
      this.students = null;
      this.startLoading();
      this.performSearch();
    }
    next();
  },
  mixins: [Loading],
  components: {
    CuratedGroupSelector,
    SortableStudents,
    Spinner
  },
  data: () => ({
    error: null,
    phrase: null,
    includeCourses: false,
    inactiveAsc: false,
    courses: null,
    totalCourseCount: null,
    studentListOptions: {
      sortBy: 'sortableName',
      includeCuratedCheckbox: true,
      reverse: false
    },
    students: null,
    totalStudentCount: null,
    limit: 50
  }),
  created() {
    this.phrase = this.$route.query.q;
    this.performSearch();
  },
  methods: {
    performSearch() {
      this.phrase = _.trim(this.phrase);
      if (this.phrase) {
        // In arrow function below, 'this' does NOT reference Search component. Using 'self' as an alias is sufficient.
        const self = this;
        search(
          this.phrase,
          this.includeCourses,
          this.inactiveAsc,
          'last_name',
          0,
          this.limit
        )
          .then(data => {
            self.courses = data.courses;
            self.students = data.students;
            _.each(self.students, student => {
              student.alertCount = student.alertCount || 0;
              student.term = student.term || {};
              student.term.enrolledUnits = student.term.enrolledUnits || 0;
            });
            self.totalCourseCount = data.totalCourseCount;
            self.totalStudentCount = data.totalStudentCount;
          })
          .then(() => {
            self.loaded();
          });
      }
    }
  }
};
</script>
