<template>
  <div v-if="!loading && error">
    <h1 class="page-section-header">Error</h1>
    <div class="text-grey">
      <span v-if="error.message">{{ error.message }}</span>
      <span v-if="!error.message">Sorry, there was an error retrieving data.</span>
    </div>
  </div>
  <div v-if="!error && !loading">
    <a
      v-if="section.totalStudentCount > itemsPerPage"
      id="skip-to-pagination-widget"
      href="#pagination-widget"
      class="sr-only"
    >
      Skip to pagination widget
    </a>
    <div class="d-flex">
      <div class="course-column-description">
        <h1
          id="course-header"
          class="course-header"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
        >
          {{ section.displayName }}
        </h1>
        <div class="font-size-14">
          <h2 class="sr-only">Details</h2>
          {{ section.instructionFormat }}
          {{ section.sectionNum }}
          <span v-if="section.instructionFormat">&mdash;</span>
          <span v-if="section.units === null">Unknown Units</span>
          <span v-if="section.units">
            {{ pluralize('Unit', section.units) }}
          </span>
        </div>
        <div
          v-if="section.title"
          class="course-section-title"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
        >
          {{ section.title }}
        </div>
      </div>
      <div class="course-column-schedule" :class="{'demo-mode-blur': currentUser.inDemoMode}">
        <h2 class="sr-only">Schedule</h2>
        <div class="course-term-name">{{ section.termName }}</div>
        <div v-for="(meeting, meetingIndex) in meetings" :key="meetingIndex">
          <div v-if="size(meeting.instructors)" class="mt-2">
            <span :id="'instructors-' + meetingIndex" class="course-schedule-header">
              {{ meeting.instructors.length > 1 ? 'Instructors:' : 'Instructor:' }}
            </span>
            {{ meeting.instructors.join(', ') }}
          </div>
          <div :id="'meetings-' + meetingIndex" class="font-size-16">
            <div>
              {{ meeting.days }}
              <span v-if="meetings.length > 1">
                ({{ DateTime.fromJSDate(meeting.startDate).toFormat('MMM D') }} to {{ DateTime.fromJSDate(meeting.endDate).toFormat('MMM D') }})
              </span>
            </div>
            <div>{{ meeting.time }}</div>
            <div>{{ meeting.location }}<span v-if="meeting.instructionModeName"><span v-if="meeting.location"> &mdash; </span>{{ meeting.instructionModeName }}</span></div>
          </div>
        </div>
        <div id="course-class-number">
          <span class="course-schedule-header">Class Number:</span> {{ section.sectionId }}
        </div>
      </div>
    </div>
  </div>
  <SectionSpinner :loading="!loading && isToggling" />
  <div v-if="!isToggling && !loading">
    <h2 class="sr-only">Students</h2>
    <div class="ml-4 mt-4">
      <CuratedGroupSelector
        v-if="size(section.students) > 1"
        :context-description="`Course ${section.displayName}`"
        domain="default"
        :students="section.students"
      />
    </div>
    <div class="align-center d-flex flex-wrap justify-space-between">
      <div class="mt-2 ml-4">
        <div v-if="section.totalStudentCount > itemsPerPage">
          <Pagination
            :click-handler="goToPage"
            :init-page-number="currentPage"
            :limit="20"
            :per-page="itemsPerPage"
            :total-rows="section.totalStudentCount"
          />
        </div>
      </div>
      <div v-if="section.totalStudentCount" class="align-center d-flex mx-4">
        <div v-if="section.totalStudentCount <= defaultItemsPerPage" class="font-weight-500 ml-auto mb-4 mr-3 mt-1">
          {{ section.totalStudentCount }} total students
        </div>
        <div
          v-if="section.totalStudentCount > defaultItemsPerPage"
          class="align-center d-flex font-size-16 ml-auto"
        >
          <div id="view-per-page-label" class="pr-2">
            <span class="font-weight-medium">{{ section.totalStudentCount }} total students</span> &mdash; View per page:&nbsp;
          </div>
          <v-btn-toggle
            v-model="itemsPerPage"
            aria-labelledby="view-per-page-label"
            class="border-sm"
            color="primary"
            density="compact"
            divided
            mandatory
          >
            <v-btn
              v-for="option in PAGINATION_OPTIONS"
              :id="`view-per-page-${option}`"
              :key="option"
              :class="{'border-color-primary font-weight-bold text-primary': option !== itemsPerPage}"
              :text="option.toString()"
              :value="option"
            />
          </v-btn-toggle>
        </div>
      </div>
    </div>
    <div v-if="!section.totalStudentCount" class="d-flex ma-3">
      <v-icon :icon="mdiAlertRhombus" color="error" />
      <span class="container-error">No students advised by your department are enrolled in this section.</span>
    </div>
    <div v-if="section.totalStudentCount" class="mx-2 mt-3">
      <CourseStudents :featured="featured" :section="section" />
      <div v-if="section.totalStudentCount > itemsPerPage" class="ml-4 mt-6">
        <Pagination
          :click-handler="goToPage"
          :init-page-number="currentPage"
          :limit="20"
          :per-page="itemsPerPage"
          :total-rows="section.totalStudentCount"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import CourseStudents from '@/components/course/CourseStudents'
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector.vue'
import ga from '@/lib/ga'
import Pagination from '@/components/util/Pagination'
import SectionSpinner from '@/components/util/SectionSpinner.vue'
import {computed, onMounted, ref, watch} from 'vue'
import {DateTime} from 'luxon'
import {each, orderBy, size, toString} from 'lodash'
import {getSection} from '@/api/course'
import {mdiAlertRhombus} from '@mdi/js'
import {pluralize, scrollToTop, setPageTitle, updateWindowLocationParam} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const DEFAULT_ITEMS_PER_PAGE = 50
const PAGINATION_OPTIONS = [DEFAULT_ITEMS_PER_PAGE, 100]
const contextStore = useContextStore()
const params = useRoute().params
const query = useRoute().query

const currentUser = contextStore.currentUser
const error = ref(null)
const featured = toString(query.u)
const currentPage = ref(isNaN(query.p) ? 1 : parseInt(query.p, 10))
const defaultItemsPerPage = ref(DEFAULT_ITEMS_PER_PAGE)
const isToggling = ref(false)
const loading = computed(() => contextStore.loading)
const meetings = ref(undefined)
const perPageQuery = isNaN(query.s) ? DEFAULT_ITEMS_PER_PAGE : parseInt(query.s, 10)
const itemsPerPage = ref(PAGINATION_OPTIONS.includes(perPageQuery) ? perPageQuery : DEFAULT_ITEMS_PER_PAGE)
const section = ref({students: []})

contextStore.loadingStart()

watch(itemsPerPage, (newValue, oldValue) => {
  goToPage(Math.round(currentPage.value * (oldValue / newValue)))
})

onMounted(() => {
  reload(params.sectionId, params.termId).then(() => {
    contextStore.loadingComplete()
    scrollToTop()
  })
})

const goToPage = page => {
  isToggling.value = true
  contextStore.broadcast('hide-footer', true)
  currentPage.value = page
  updateWindowLocationParam('p', page)
  reload(section.value.sectionId, section.value.termId).then(() => {
    isToggling.value = false
    scrollToTop()
    contextStore.broadcast('hide-footer', false)
  })
}

const reload = (sectionId, termId) => {
  const limit = itemsPerPage.value
  const offset = currentPage.value === 0 ? 0 : (currentPage.value - 1) * limit
  return getSection(termId, sectionId, offset, limit, featured).then(
    data => {
      section.value = data
      meetings.value = orderBy(data.meetings, ['startDate'])
      const students = data.students.sort(s => s.uid === featured ? -1 : 0)
      const displayName = data.displayName
      // Discrepancies in our loch-hosted SIS data dumps may occasionally result in students without enrollment
      // objects. A placeholder object keeps the front end from breaking.
      each(students, student => !student.enrollment && (student.enrollment = {canvasSites: []}))
      const totalStudentCount = data.totalStudentCount
      const message = totalStudentCount < itemsPerPage.value ?
        `Showing all ${totalStudentCount} students.` :
        `Showing ${itemsPerPage.value} of ${totalStudentCount} total students.`
      contextStore.loadingComplete(`Course ${displayName} has loaded ${message}`)
      ga.course('view', displayName)
      setPageTitle(displayName)
    },
    e => error.value = e,
  )
}
</script>

<style scoped>
.container-error {
  padding: 0 10px 0 10px;
}
.course-column-description {
  background-color: #e3f5ff;
  flex: 3 0 0;
  padding: 10px 10px 10px 20px;
}
.course-column-schedule {
  background-color: #8bbdda;
  color: #fff;
  flex: 2 0 0;
  padding: 10px 10px 20px 20px;
}
.course-header {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 5px 0;
}
.course-schedule-header {
  font-size: 16px;
  font-weight: bold;
}
.course-section-title {
  font-size: 16px;
  font-weight: bold;
  padding-top: 20px;
}
.course-term-name {
  font-size: 16px;
  font-weight: bold;
}
</style>
