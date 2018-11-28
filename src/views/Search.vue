<template>
<div>
  <Spinner/>
  <SortableStudents v-bind:students="students"/>
</div>
</template>

<script>
import _ from 'lodash';
import { search } from '@/api/student';
import Spinner from '@/components/Spinner.vue';
import Loading from '@/mixins/Loading.vue';
import SmartRef from '@/components/SmartRef';
import SortableStudents from '@/components/search/SortableStudents';

export default {
  name: 'Search',
  mixins: [Loading],
  components: {
    SmartRef,
    SortableStudents,
    Spinner
  },
  data: () => ({
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

<style scoped>
.foo {
  font-size: 16px;
}
</style>
