<template>
  <div>
    <Spinner/>
    <div v-if="!loading">
      <div class="light-blue-background border-bottom">
        <StudentProfileHeader :student="student"/>
      </div>
      <h2 class="sr-only">Academic Status</h2>
      <div class="flex-row border-bottom">
        <div class="w-50">
          <h3 class="sr-only">Units</h3>
          <StudentProfileUnits :student="student"/>
        </div>
        <div class="border-left w-50">
          <h3 class="sr-only">GPA</h3>
          <StudentProfileGPA :student="student"/>
        </div>
      </div>
      <div class="m-3">
        <AcademicTimeline :student="student"/>
      </div>
      <div>
        <StudentClasses :student="student"/>
      </div>
    </div>
  </div>
</template>

<script>
import AcademicTimeline from '@/components/student/profile/AcademicTimeline';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import StudentClasses from '@/components/student/profile/StudentClasses';
import StudentProfileGPA from '@/components/student/profile/StudentProfileGPA';
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader';
import StudentProfileUnits from '@/components/student/profile/StudentProfileUnits';
import Util from '@/mixins/Util';
import { getStudentDetails } from '@/api/student';

export default {
  name: 'Student',
  mixins: [Loading, Util],
  components: {
    AcademicTimeline,
    Spinner,
    StudentClasses,
    StudentProfileGPA,
    StudentProfileHeader,
    StudentProfileUnits
  },
  data: () => ({
    showAllTerms: false,
    student: {
      termGpa: []
    }
  }),
  created() {
    const uid = this.get(this.$route, 'params.uid');
    getStudentDetails(uid).then(data => {
      if (data) {
        this.setPageTitle(data.name);
        this.assign(this.student, data);
        this.each(this.student.enrollmentTerms, this.parseEnrollmentTerm);
        this.loaded();
      } else {
        this.$router.push({ path: '/404' });
      }
    });
  },
  methods: {
    decorateCourse(course) {
      // course_code is often valuable (eg, 'ECON 1 - LEC 001'), occasionally not (eg, CCN). Use it per strict criteria:
      const useCourseCode = /^[A-Z].*[A-Za-z]{3} \d/.test(course.courseCode);
      return this.merge(course, {
        displayName: useCourseCode ? course.courseCode : course.courseName,
        title: useCourseCode ? course.courseName : null,
        canvasSites: [course]
      });
    },
    parseEnrollmentTerm(term) {
      // Merge in unmatched canvas sites
      const unmatched = this.map(
        term.unmatchedCanvasSites,
        this.decorateCourse
      );
      term.enrollments = this.concat(term.enrollments, unmatched);
      this.each(term.enrollments, this.parseCourse);
      if (this.get(term, 'termGpa.unitsTakenForGpa')) {
        this.student.termGpa.push({
          name: this.get(term, 'termName'),
          gpa: this.get(term, 'termGpa.gpa')
        });
      }
    },
    parseCourse(course) {
      this.each(course.sections, function(section) {
        course.waitlisted =
          course.waitlisted || section.enrollmentStatus === 'W';
        course.isOpen = false;
        section.displayName = section.component + ' ' + section.sectionNumber;
        section.isViewableOnCoursePage = section.primary;
      });
    }
  }
};
</script>

<style>
.student-column {
  flex: 0 0 120px;
  margin-left: 15px;
}
.student-name {
  color: #49b;
  font-size: 16px;
  margin: 0;
}
.student-sid {
  font-size: 11px;
  font-weight: bold;
  margin: 5px 0;
}
.student-teams {
  color: #000;
  font-size: 13px;
}
.student-teams-container {
  margin-top: 5px;
}
.student-text {
  color: #aaa;
  font-size: 13px;
}
</style>

<style scoped>
.light-blue-background {
  background: #e3f5ff;
}
</style>
