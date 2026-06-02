<template>
  <div v-if="!contextStore.loading">
    <div class="bg-sky-blue border-b-sm">
      <StudentProfileHeader :student="student" />
    </div>
    <h2 id="student-academic-status-header" class="sr-only">Academic Status</h2>
    <v-container
      aria-labelledby="student-academic-status-header"
      class="border-b-sm pa-0"
      fluid
      role="region"
    >
      <v-row no-gutters>
        <v-col class="border-e-sm py-2">
          <div class="sr-only">Units</div>
          <StudentProfileUnits :student="student" />
        </v-col>
        <v-col class="border-e-sm py-2">
          <div class="sr-only">GPA</div>
          <StudentProfileGPA :student="student" />
        </v-col>
      </v-row>
    </v-container>
    <div class="default-margins">
      <div class="border-b-sm">
        <AcademicTimeline :student="student" />
      </div>
      <StudentClasses class="mt-8" :student="student" />
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
import {each, get, noop} from 'lodash'
import {onBeforeRouteLeave, useRoute} from 'vue-router'
import {onMounted, reactive, ref} from 'vue'
import AcademicTimeline from '@/components/student/profile/academic-timeline/AcademicTimeline'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import StudentClasses from '@/components/student/profile/StudentClasses'
import StudentProfileGPA from '@/components/student/profile/StudentProfileGPA'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import StudentProfileUnits from '@/components/student/profile/StudentProfileUnits'
import {alertScreenReader, decodeStudentUriAnchor, putFocusNextTick, setPageTitle} from '@/lib/utils'
import {exitSession} from '@/stores/note-edit-session/note-edit-session-utils'
import {getStudentByUid} from '@/api/student'
import {setWaitlistedStatus} from '@/lib/berkeley-utils'
import {useNoteStore} from '@/stores/note-edit-session'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const noteStore = useNoteStore()
let cancelTheCancel = noop
let cancelConfirmed = noop
const currentUser = reactive(contextStore.currentUser)
const route = useRoute()
const showAreYouSureModal = ref(false)
const student = ref(undefined)
// In demo-mode we do not want to expose UID in browser location bar.
const uid = currentUser.inDemoMode ? window.atob(route.params.uid) : route.params.uid

contextStore.loadingStart()

onMounted(() => {
  getStudentByUid(uid).then(data => {
    student.value = data
    setPageTitle(currentUser.inDemoMode ? 'Student' : student.value.name)
    each(student.value.enrollmentTerms, term => {
      each(term.enrollments, course => {
        const canAccessCanvasData = currentUser.canAccessCanvasData
        setWaitlistedStatus(course)
        each(course.sections, function(section) {
          course.isOpen = false
          section.displayName = section.component + ' ' + section.sectionNumber
          section.isViewableOnCoursePage = section.primary && canAccessCanvasData
        })
      })
      if (get(term, 'termGpa.unitsTakenForGpa')) {
        student.value.termGpa = student.value.termGpa || []
        student.value.termGpa.push({
          name: get(term, 'termName'),
          gpa: get(term, 'termGpa.gpa')
        })
      }
    })
    // If custom scroll-to-note is happening then skip the default put-focus-on-h1.
    const focusTarget = decodeStudentUriAnchor()
    contextStore.loadingComplete('page-header', !!focusTarget)
  })
})

onBeforeRouteLeave((to, from, next) => {
  if (noteStore.mode) {
    cancelConfirmed = () => {
      exitSession(true)
      next()
    }
    cancelTheCancel = () => {
      showAreYouSureModal.value = false
      alertScreenReader('Canceled. Save changes before leaving the page.')
      putFocusNextTick('edit-note-subject')
      next(false)
    }
    showAreYouSureModal.value = true
  } else {
    exitSession(true)
    next()
  }
})
</script>
