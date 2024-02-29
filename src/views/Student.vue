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
import Context from '@/mixins/Context'
import Spinner from '@/components/util/Spinner'
import StudentClasses from '@/components/student/profile/StudentClasses'
import NoteEditSession from '@/mixins/NoteEditSession'
import StudentProfileGPA from '@/components/student/profile/StudentProfileGPA'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import StudentProfileUnits from '@/components/student/profile/StudentProfileUnits'
import Util from '@/mixins/Util'
import {exitSession} from '@/stores/note-edit-session/utils'
import {getStudentByUid} from '@/api/student'
import {scrollToTop} from '@/lib/utils'
import {setWaitlistedStatus} from '@/berkeley'
import {useNoteStore} from '@/stores/note-edit-session'

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
  mixins: [Context, NoteEditSession, Util],
  beforeRouteLeave(to, from, next) {
    this.confirmExitAndEndSession(next)
  },
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
  created() {
    let uid = this._get(this.$route, 'params.uid')
    if (this.currentUser.inDemoMode) {
      // In demo-mode we do not want to expose SID in browser location bar.
      uid = window.atob(uid)
    }
    getStudentByUid(uid).then(student => {
      this.setPageTitle(this.currentUser.inDemoMode ? 'Student' : student.name)
      this._assign(this.student, student)
      this._each(this.student.enrollmentTerms, this.parseEnrollmentTerm)
      this.loadingComplete(`${this.student.name} loaded`)
    })
  },
  mounted() {
    if (!this.anchor) {
      scrollToTop()
    }
  },
  methods: {
    confirmExitAndEndSession(next) {
      if (useNoteStore().mode) {
        this.alertScreenReader('Are you sure you want to discard unsaved changes?')
        this.cancelConfirmed = () => {
          exitSession(true)
          return next()
        }
        this.cancelTheCancel = () => {
          this.alertScreenReader('Please save changes before exiting the page.')
          this.showAreYouSureModal = false
          next(false)
        }
        this.showAreYouSureModal = true
      } else {
        exitSession(true)
        next()
      }
    },
    parseEnrollmentTerm(term) {
      this._each(term.enrollments, this.parseCourse)
      if (this._get(term, 'termGpa.unitsTakenForGpa')) {
        this.student.termGpa.push({
          name: this._get(term, 'termName'),
          gpa: this._get(term, 'termGpa.gpa')
        })
      }
    },
    parseCourse(course) {
      const canAccessCanvasData = this.currentUser.canAccessCanvasData
      setWaitlistedStatus(course)
      this._each(course.sections, function(section) {
        course.isOpen = false
        section.displayName = section.component + ' ' + section.sectionNumber
        section.isViewableOnCoursePage = section.primary && canAccessCanvasData
      })
    }
  }
}
</script>
