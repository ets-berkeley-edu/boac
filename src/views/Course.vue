<template>
  <div v-if="!loading && error">
    <h1 class="page-section-header">Error</h1>
    <div class="text-grey">
      <span v-if="error.message">{{ error.message }}</span>
      <span v-if="!error.message">Sorry, there was an error retrieving data.</span>
    </div>
  </div>
  <div v-if="!error">
    <div v-if="!loading">
      <a
        v-if="section.totalStudentCount > pagination.itemsPerPage"
        id="skip-to-pagination-widget"
        href="#pagination-widget"
        class="sr-only"
      >Skip to pagination widget</a>
      <div>
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
    </div>
    <div v-if="!loading">
      <h2 class="sr-only">Students</h2>
      <div v-if="!section.totalStudentCount" class="d-flex ml-3 mt-3">
        <v-icon :icon="mdiAlertRhombus" color="error" />
        <span class="container-error">No students advised by your department are enrolled in this section.</span>
      </div>
      <div v-if="section.totalStudentCount" class="align-center d-flex mt-3 mx-3">
        <div v-if="section.totalStudentCount <= pagination.defaultItemsPerPage" class="font-weight-500 ml-auto mb-4 mr-3 mt-1">
          {{ section.totalStudentCount }} total students
        </div>
        <div
          v-if="section.totalStudentCount > pagination.defaultItemsPerPage"
          class="align-center d-flex ml-auto mr-3"
        >
          <div id="view-per-page-label">
            {{ section.totalStudentCount }} total students &mdash; View per page:&nbsp;
          </div>
          <v-btn-group
            aria-labelledby="view-per-page-label"
            density="compact"
            variant="flat"
          >
            <div v-for="(option, index) in PAGINATION_OPTIONS" :key="index">
              <v-btn
                :id="`view-per-page-${option}`"
                :class="{'font-weight-bold text-dark': option === pagination.itemsPerPage}"
                class="items-per-page-btn"
                :disabled="option === pagination.itemsPerPage"
                :text="option.toString()"
                @click="resizePage(option)"
                @keyup.enter="resizePage(option)"
              />
              <span v-if="index + 1 < PAGINATION_OPTIONS.length">
                |
              </span>
            </div>
          </v-btn-group>
        </div>
      </div>
      <div v-if="section.totalStudentCount" class="ml-2 mr-2">
        <CourseStudents :featured="featured" :section="section" />
        <div class="ma-4">
          <div v-if="section.totalStudentCount > pagination.itemsPerPage">
            <Pagination
              :click-handler="goToPage"
              :init-page-number="pagination.currentPage"
              :limit="20"
              :per-page="pagination.itemsPerPage"
              :total-rows="section.totalStudentCount"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import CourseStudents from '@/components/course/CourseStudents'
import ga from '@/lib/ga'
import Pagination from '@/components/util/Pagination'
import router from '@/router'
import {DateTime} from 'luxon'
import {computed, onMounted, reactive, ref} from 'vue'
import {each, orderBy, size, toString} from 'lodash'
import {getSection} from '@/api/course'
import {mdiAlertRhombus} from '@mdi/js'
import {pluralize, scrollToTop, setPageTitle} from '@/lib/utils'
import {useRoute} from 'vue-router'
import {useContextStore} from '@/stores/context'

const DEFAULT_ITEMS_PER_PAGE = 50
const PAGINATION_OPTIONS = [DEFAULT_ITEMS_PER_PAGE, 100]
const contextStore = useContextStore()
const params = useRoute().params
const query = useRoute().query

const currentUser = contextStore.currentUser
const error = ref(null)
const featured = toString(query.u)
const itemsPerPage = isNaN(query.s) ? DEFAULT_ITEMS_PER_PAGE : parseInt(query.s, 10)
const loading = computed(() => contextStore.loading)
const meetings = ref(undefined)
const pagination = reactive({
  currentPage: isNaN(query.p) ? 1 : parseInt(query.p, 10),
  defaultItemsPerPage: DEFAULT_ITEMS_PER_PAGE,
  itemsPerPage: PAGINATION_OPTIONS.includes(itemsPerPage) ? itemsPerPage : DEFAULT_ITEMS_PER_PAGE
})
const section = ref({students: []})

onMounted(() => {
  contextStore.loadingStart()
  const limit = pagination.itemsPerPage
  const offset = pagination.currentPage === 0 ? 0 : (pagination.currentPage - 1) * limit
  getSection(params.termId, params.sectionId, offset, limit, featured).then(
    data => {
      section.value = data
      meetings.value = orderBy(data.meetings, ['startDate'])
      const students = data.students.sort(s => s.uid === featured ? -1 : 0)
      const displayName = data.displayName
      // Discrepancies in our loch-hosted SIS data dumps may occasionally result in students without enrollment
      // objects. A placeholder object keeps the front end from breaking.
      each(students, student => !student.enrollment && (student.enrollment = {canvasSites: []}))
      const totalStudentCount = data.totalStudentCount
      const message = totalStudentCount < pagination.itemsPerPage ? `Showing all ${totalStudentCount} students.` : `Showing ${pagination.itemsPerPage} of ${totalStudentCount} total students.`
      contextStore.loadingComplete(`Course ${displayName} has loaded ${message}`)
      ga.course('view', displayName)
      setPageTitle(displayName)
    },
    e => error.value = e,
  ).then(() => {
    contextStore.loadingComplete()
    scrollToTop()
  })
})

const goToPage = page => {
  pagination.currentPage = page
  router.push({
    query: {...params, p: pagination.currentPage}
  })
}

const resizePage = itemsPerPage => {
  const previousItemsPerPage = pagination.itemsPerPage
  pagination.itemsPerPage = itemsPerPage
  pagination.currentPage = Math.round(pagination.currentPage * (previousItemsPerPage / pagination.itemsPerPage))
}
</script>

<style scoped>
.container-error {
  padding: 0 10px 0 10px;
}
.course-column-description {
  background-color: #e3f5ff;
  flex: 3 0 0;
  padding: 10px 10px 20px 10px;
}
.course-column-schedule {
  background-color: #8bbdda;
  color: #fff;
  flex: 2 0 0;
  padding: 10px 10px 20px 10px;
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
.items-per-page-btn {
  padding: 0;
  width: 12px !important;
}
</style>
