<template>
  <div class="m-3">
    <Spinner/>
    <div v-if="!loading && !results.totalStudentCount && !results.totalCourseCount">
      <h1 id="page-header-no-results"
          role="alert"
          aria-live="passive">No results matching '{{ phrase }}'</h1>
      <div>Suggestions:</div>
      <ul>
        <li>Keep your search term simple.</li>
        <li>Check your spelling and try again.</li>
        <li>Search classes by section title, e.g., <strong>AMERSTD 10</strong>.</li>
        <li>Abbreviations of section titles may not return results; <strong>COMPSCI 161</strong> instead of <strong>CS 161</strong>.</li>
      </ul>
    </div>
    <div tabindex="0"
         v-if="!loading && results.totalStudentCount">
      <h1 id="page-header">{{ 'student' | pluralize(results.totalStudentCount) }} matching '{{ phrase }}'</h1>
      <div v-if="results.totalStudentCount > limit">
        Showing the first {{ limit }} students.
      </div>
    </div>
    <div class="cohort-column-results" v-if="!loading && results.totalStudentCount">
      <div class="search-header-curated-cohort">
        <CuratedGroupSelector :students="results.students"/>
      </div>
      <div>
        <SortableStudents :students="results.students" :options="studentListOptions"/>
      </div>
    </div>
    <div v-if="!loading && results.totalCourseCount">
      <SortableCourseList :searchPhrase="phrase"
                          :courses="results.courses"
                          :totalCourseCount="results.totalCourseCount"
                          :renderPrimaryHeader="!results.totalStudentCount && !!results.totalCourseCount"/>
    </div>
  </div>
</template>

<script>
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import Loading from '@/mixins/Loading';
import SortableCourseList from '@/components/course/SortableCourseList';
import SortableStudents from '@/components/search/SortableStudents';
import Spinner from '@/components/util/Spinner';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { search } from '@/api/student';

export default {
  name: 'Search',
  mixins: [Loading, UserMetadata, Util],
  components: {
    SortableCourseList,
    CuratedGroupSelector,
    SortableStudents,
    Spinner
  },
  data: () => ({
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
    const includeCourses = this.$route.query.includeCourses;
    if (this.phrase) {
      search(
        this.phrase,
        this.isNil(includeCourses) ? false : includeCourses,
        this.isAscUser ? false : null,
        this.isCoeUser ? false : null
      )
        .then(data => {
          this.results.courses = data.courses;
          this.results.students = data.students;
          this.each(this.results.students, student => {
            student.alertCount = student.alertCount || 0;
            student.term = student.term || {};
            student.term.enrolledUnits = student.term.enrolledUnits || 0;
          });
          this.results.totalCourseCount = data.totalCourseCount;
          this.results.totalStudentCount = data.totalStudentCount;
        })
        .then(() => {
          this.loaded();
          const focusId =
            this.results.totalCourseCount || this.results.totalStudentCount
              ? 'page-header'
              : 'page-header-no-results';
          this.putFocusNextTick(focusId);
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
