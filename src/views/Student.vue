<template>
  <div v-if="!loading">
    <div class="light-blue-background border-b-sm">
      <StudentProfileHeader :student="student" />
    </div>
    <h2 class="sr-only">Academic Status</h2>
    <div class="border-b-sm d-flex flex-wrap w-100">
      <div class="border-e-sm" :class="$vuetify.display.mdAndUp ? 'w-50' : 'w-100'">
        <h3 class="sr-only">Units</h3>
        <StudentProfileUnits :student="student" />
      </div>
      <div :class="$vuetify.display.mdAndUp ? 'w-50' : 'w-100'">
        <h3 class="sr-only">GPA</h3>
        <StudentProfileGPA :student="student" />
      </div>
    </div>
    <div class="default-margins">
      <div class="border-b-sm pb-3">
        <AcademicTimeline :student="student" />
      </div>
      <div v-if="currentUser.canReadDegreeProgress" class="float-end mr-3 mt-3">
        <router-link
          id="view-degree-checks-link"
          class="font-weight-medium"
          target="_blank"
          :to="getDegreeCheckPath()"
        >
          <div class="align-center d-flex">
            <div>
              Degree Checks<span class="sr-only"> of {{ student.name }} (will open new browser tab)</span>
            </div>
            <v-icon class="ml-1" :icon="mdiOpenInNew" size="18" />
          </div>
        </router-link>
      </div>
      <StudentClasses class="mt-5" :student="student" />
    </div>
    <AreYouSureModal
      v-model="showAreYouSureModal"
      :function-cancel="cancelTheCancel"
      :function-confirm="cancelConfirmed"
      modal-header="Discard unsaved note?"
    />
  </div>
</template>

<script setup>
import {mdiOpenInNew} from '@mdi/js'
</script>

<script>
import AcademicTimeline from '@/components/student/profile/AcademicTimeline'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Context from '@/mixins/Context'
import StudentClasses from '@/components/student/profile/StudentClasses'
import NoteEditSession from '@/mixins/NoteEditSession'
import StudentProfileGPA from '@/components/student/profile/StudentProfileGPA'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import StudentProfileUnits from '@/components/student/profile/StudentProfileUnits'
import Util from '@/mixins/Util'
import {alertScreenReader, scrollToTop} from '@/lib/utils'
import {exitSession} from '@/stores/note-edit-session/utils'
import {find} from 'lodash'
import {getStudentByUid} from '@/api/student'
import {setWaitlistedStatus} from '@/berkeley'
import {useNoteStore} from '@/stores/note-edit-session'

export default {
  name: 'Student',
  components: {
    AcademicTimeline,
    AreYouSureModal,
    StudentClasses,
    StudentProfileGPA,
    StudentProfileHeader,
    StudentProfileUnits
  },
  mixins: [Context, NoteEditSession, Util],
  beforeRouteLeave(to, from, next) {
    if (useNoteStore().mode) {
      alertScreenReader('Are you sure you want to discard unsaved changes?')
      this.cancelConfirmed = () => {
        exitSession(true)
        return next()
      }
      this.cancelTheCancel = () => {
        alertScreenReader('Please save changes before exiting the page.')
        this.showAreYouSureModal = false
        next(false)
      }
      this.showAreYouSureModal = true
    } else {
      exitSession(true)
      next()
    }
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
    getDegreeCheckPath() {
      const currentDegreeCheck = find(this.student.degreeChecks, 'isCurrent')
      if (currentDegreeCheck) {
        return `/student/degree/${currentDegreeCheck.id}`
      } else if (this.currentUser.canEditDegreeProgress) {
        return `${this.studentRoutePath(this.student.uid, this.currentUser.inDemoMode)}/degree/create`
      } else {
        return `${this.studentRoutePath(this.student.uid, this.currentUser.inDemoMode)}/degree/history`
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
