<template>
  <div class="cohort-container">
    <Spinner/>
    <div v-if="error">
      <h1 role="alert" aria-live="passive" class="page-section-header">Error</h1>
      <div class="faint-text">
        <span role="alert" aria-live="passive" v-if="error.message">{{ error.message }}</span>
        <span role="alert" aria-live="passive" v-if="!error.message">Sorry, there was an error retrieving data.</span>
      </div>
    </div>
    <div v-if="!loading && !error && !totalStudentCount && !totalCourseCount">
      <h1 role="alert" aria-live="passive" class="page-section-header">No results matching '{{ phrase }}'</h1>
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
        <h1 class="page-section-header">
          {{ 'student' | pluralize(totalStudentCount) }} matching '{{ phrase }}'
        </h1>
        <div v-if="totalStudentCount > limit">
          Showing the first {{limit}} students.
        </div>
      </div>
    </div>
    <div class="cohort-column-results" data-ng-if="!loading && !error && totalStudentCount">
      <div class="search-header-curated-cohort">
        <CuratedGroupSelector :students="students"/>
      </div>
      <div>
        <SortableStudents :students="students"/>
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
        search(
          this.phrase,
          this.includeCourses,
          this.inactiveAsc,
          'last_name',
          0,
          this.limit
        )
          .then(data => {
            this.courses = data.courses;
            this.students = data.students;
            _.each(this.students, student => {
              student.alertCount = student.alertCount || 0;
              student.term = student.term || {};
              student.term.enrolledUnits = student.term.enrolledUnits || 0;
            });
            this.totalCourseCount = data.totalCourseCount;
            this.totalStudentCount = data.totalStudentCount;
          })
          .then(() => {
            this.loaded();
          });
      }
    }
  }
};
</script>
