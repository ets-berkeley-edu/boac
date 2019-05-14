<template>
  <div>
    <Spinner />
    <div v-if="!loading">
      <div class="light-blue-background border-bottom">
        <StudentProfileHeader :student="student" />
      </div>
      <h2 class="sr-only">Academic Status</h2>
      <div class="flex-row border-bottom">
        <div class="w-50">
          <h3 class="sr-only">Units</h3>
          <StudentProfileUnits :student="student" />
        </div>
        <div class="border-left w-50">
          <h3 class="sr-only">GPA</h3>
          <StudentProfileGPA :student="student" />
        </div>
      </div>
      <div class="m-3">
        <AcademicTimeline :student="student" />
        <AreYouSureModal
          v-if="showAreYouSureModal"
          :function-cancel="cancelTheCancel"
          :function-confirm="cancelConfirmed"
          modal-header="Discard unsaved note?"
          :show-modal="showAreYouSureModal" />
      </div>
      <div>
        <StudentClasses :student="student" />
      </div>
    </div>
  </div>
</template>

<script>
import AcademicTimeline from '@/components/student/profile/AcademicTimeline';
import AreYouSureModal from '@/components/util/AreYouSureModal';
import Context from '@/mixins/Context';
import Loading from '@/mixins/Loading';
import NoteEditSession from '@/mixins/NoteEditSession';
import Scrollable from '@/mixins/Scrollable';
import Spinner from '@/components/util/Spinner';
import StudentClasses from '@/components/student/profile/StudentClasses';
import StudentProfileGPA from '@/components/student/profile/StudentProfileGPA';
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader';
import StudentProfileUnits from '@/components/student/profile/StudentProfileUnits';
import Util from '@/mixins/Util';
import { getStudent } from '@/api/student';

export default {
  name: 'Student',
  components: {
    AcademicTimeline,
    AreYouSureModal,
    Spinner,
    StudentClasses,
    StudentProfileGPA,
    StudentProfileHeader,
    StudentProfileUnits
  },
  mixins: [Context, Loading, NoteEditSession, Scrollable, Util],
  data: () => ({
    cancelTheCancel: undefined,
    cancelConfirmed: undefined,
    showAllTerms: false,
    showAreYouSureModal: false,
    student: {
      termGpa: []
    }
  }),
  computed: {
    anchor: () => location.hash
  },
  beforeRouteLeave(to, from, next) {
    if (this.newNoteMode || this.editingNoteId) {
      this.alertScreenReader("Are you sure you want to discard unsaved changes?");
      this.cancelConfirmed = () => {
        this.editExistingNoteId(null);
        next();
      };
      this.cancelTheCancel = () => {
        this.alertScreenReader("Please save changes before exiting the page.");
        this.showAreYouSureModal = false;
        next(false);
      };
      this.showAreYouSureModal = true;
    } else {
      next();
    }
  },
  created() {
    const uid = this.get(this.$route, 'params.uid');
    getStudent(uid).then(data => {
      if (data) {
        this.setPageTitle(this.user.inDemoMode ? 'Student' : data.name);
        this.assign(this.student, data);
        this.each(this.student.enrollmentTerms, this.parseEnrollmentTerm);
        this.loaded();
      } else {
        this.$router.push({ path: '/404' });
      }
    });
  },
  mounted() {
    if (!this.anchor) {
      this.scrollToTop();
    }
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
.student-section-header {
  font-size: 24px;
  font-weight: bold;
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
