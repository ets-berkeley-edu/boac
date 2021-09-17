<template>
  <div>
    <Spinner />
    <div v-if="!loading">
      <div class="light-blue-background border-bottom">
        <StudentProfileHeader :student="student" />
      </div>
      <h2 class="sr-only">Academic Status</h2>
      <div class="flex-row flex-wrap border-bottom mx-3">
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
          :show-modal="showAreYouSureModal"
          modal-header="Discard unsaved note?"
        />
      </div>
      <div>
        <StudentClasses :student="student" />
      </div>
    </div>
  </div>
</template>

<script>
import AcademicTimeline from '@/components/student/profile/AcademicTimeline'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import Scrollable from '@/mixins/Scrollable'
import Spinner from '@/components/util/Spinner'
import StudentClasses from '@/components/student/profile/StudentClasses'
import NoteEditSession from '@/mixins/NoteEditSession'
import StudentProfileGPA from '@/components/student/profile/StudentProfileGPA'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import StudentProfileUnits from '@/components/student/profile/StudentProfileUnits'
import Util from '@/mixins/Util'
import {getStudentByUid} from '@/api/student'

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
  mixins: [Berkeley, Context, Loading, Scrollable, NoteEditSession, Util],
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
    this.confirmExitAndEndSession(next)
  },
  created() {
    let uid = this.$_.get(this.$route, 'params.uid')
    if (this.$currentUser.inDemoMode) {
      // In demo-mode we do not want to expose SID in browser location bar.
      uid = window.atob(uid)
    }
    getStudentByUid(uid).then(student => {
      this.setPageTitle(this.$currentUser.inDemoMode ? 'Student' : student.name)
      this.$_.assign(this.student, student)
      this.$_.each(this.student.enrollmentTerms, this.parseEnrollmentTerm)
      this.loaded(`${this.student.name} loaded`, this.anchor)
    })
  },
  mounted() {
    if (!this.anchor) {
      this.scrollToTop()
    }
  },
  methods: {
    confirmExitAndEndSession(next) {
      if (this.noteMode) {
        this.alertScreenReader('Are you sure you want to discard unsaved changes?')
        this.cancelConfirmed = () => {
          this.exitSession()
          return next()
        }
        this.cancelTheCancel = () => {
          this.alertScreenReader('Please save changes before exiting the page.')
          this.showAreYouSureModal = false
          next(false)
        }
        this.showAreYouSureModal = true
      } else {
        this.exitSession()
        next()
      }
    },
    decorateCourse(course) {
      // course_code is often valuable (eg, 'ECON 1 - LEC 001'), occasionally not (eg, CCN). Use it per strict criteria:
      const useCourseCode = /^[A-Z].*[A-Za-z]{3} \d/.test(course.courseCode)
      return this.$_.merge(course, {
        displayName: useCourseCode ? course.courseCode : course.courseName,
        title: useCourseCode ? course.courseName : null,
        canvasSites: [course]
      })
    },
    parseEnrollmentTerm(term) {
      // Merge in unmatched canvas sites
      const unmatched = this.$_.map(
        term.unmatchedCanvasSites,
        this.decorateCourse
      )
      term.enrollments = this.$_.concat(term.enrollments, unmatched)
      this.$_.each(term.enrollments, this.parseCourse)
      if (this.$_.get(term, 'termGpa.unitsTakenForGpa')) {
        this.student.termGpa.push({
          name: this.$_.get(term, 'termName'),
          gpa: this.$_.get(term, 'termGpa.gpa')
        })
      }
    },
    parseCourse(course) {
      const canAccessCanvasData = this.$currentUser.canAccessCanvasData
      const fullProfileAvailable = !this.student.fullProfilePending
      this.setWaitlistedStatus(course)
      this.$_.each(course.sections, function(section) {
        course.isOpen = false
        section.displayName = section.component + ' ' + section.sectionNumber
        section.isViewableOnCoursePage = section.primary && canAccessCanvasData && fullProfileAvailable
      })
    }
  }
}
</script>
