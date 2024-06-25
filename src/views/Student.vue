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
          :to="degreeCheckPath"
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
import AcademicTimeline from '@/components/student/profile/AcademicTimeline'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import StudentClasses from '@/components/student/profile/StudentClasses'
import StudentProfileGPA from '@/components/student/profile/StudentProfileGPA'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import StudentProfileUnits from '@/components/student/profile/StudentProfileUnits'
import {alertScreenReader, scrollToTop, setPageTitle, studentRoutePath} from '@/lib/utils'
import {exitSession} from '@/stores/note-edit-session/utils'
import {each, find, get, noop} from 'lodash'
import {getStudentByUid} from '@/api/student'
import {onBeforeRouteLeave, useRoute} from 'vue-router'
import {computed, onMounted, reactive, ref} from 'vue'
import {setWaitlistedStatus} from '@/berkeley'
import {useNoteStore} from '@/stores/note-edit-session'
import {useContextStore} from '@/stores/context'

let cancelTheCancel = noop
let cancelConfirmed = noop
const contextStore = useContextStore()
const currentUser = reactive(contextStore.currentUser)
let degreeCheckPath
const loading = computed(() => contextStore.loading)
const noteStore = useNoteStore()
const route = useRoute()
const showAreYouSureModal = ref(false)
let student
// In demo-mode we do not want to expose UID in browser location bar.
const uid = currentUser.inDemoMode ? window.atob(route.params.uid) : route.params.uid

onMounted(() => {
  contextStore.loadingStart()
  getStudentByUid(uid).then(data => {
    student = data
    setPageTitle(currentUser.inDemoMode ? 'Student' : student.name)
    each(student.enrollmentTerms, term => {
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
        student.termGpa = student.termGpa || []
        student.termGpa.push({
          name: get(term, 'termName'),
          gpa: get(term, 'termGpa.gpa')
        })
      }
    })
    const currentDegreeCheck = find(student.degreeChecks, 'isCurrent')
    if (currentDegreeCheck) {
      degreeCheckPath = `/student/degree/${currentDegreeCheck.id}`
    } else if (currentUser.canEditDegreeProgress) {
      degreeCheckPath = `${studentRoutePath(student.uid, currentUser.inDemoMode)}/degree/create`
    } else {
      degreeCheckPath = `${studentRoutePath(student.uid, currentUser.inDemoMode)}/degree/history`
    }
    contextStore.loadingComplete(`${student.name} loaded`)
    if (!location.hash) {
      scrollToTop()
    }
  })
})

onBeforeRouteLeave((to, from, next) => {
  if (noteStore.mode) {
    alertScreenReader('Are you sure you want to discard unsaved changes?')
    cancelConfirmed = () => {
      exitSession(true)
      return next()
    }
    cancelTheCancel = () => {
      alertScreenReader('Please save changes before exiting the page.')
      showAreYouSureModal.value = false
      next(false)
    }
    showAreYouSureModal.value = true
  } else {
    exitSession(true)
    next()
  }
})
</script>
