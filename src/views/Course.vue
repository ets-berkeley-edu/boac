<template>
  <div class="w-100">
    <Spinner />
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
                <div v-if="!_isEmpty(meeting.instructors)" class="mt-2">
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
      <SectionSpinner :loading="!loading" />
      <div v-if="!loading">
        <h2 class="sr-only">Students</h2>
        <div v-if="!section.totalStudentCount" class="d-flex ml-3 mt-3">
          <v-icon :icon="mdiAlertRhombus" color="error" />
          <span class="container-error">No students advised by your department are enrolled in this section.</span>
        </div>
        <div v-if="section.totalStudentCount" class="align-items-start d-flex mb-2 ml-3 mt-3">
          <div>
            <CuratedGroupSelector
              v-if="!_isEmpty(section.students) && (tab === 'list')"
              :context-description="`Course ${section.displayName}`"
              domain="default"
              :students="section.students"
              class="mr-2"
            />
          </div>
          <div v-if="tab === 'list' && (section.totalStudentCount > pagination.defaultItemsPerPage)" class="align-center d-flex ml-auto mr-3">
            <div id="view-per-page-label" class="pr-1">
              {{ section.totalStudentCount }} total students &mdash; View per page:&nbsp;
            </div>
            <v-btn-group aria-labelledby="view-per-page-label">
              <div v-for="(option, index) in pagination.options" :key="index">
                <v-btn
                  :id="`view-per-page-${option}`"
                  class="px-1"
                  :class="{'font-size-16 font-weight-bold text-dark': option === pagination.itemsPerPage}"
                  :disabled="option === pagination.itemsPerPage"
                  variant="link"
                  @click="resizePage(option)"
                  @keyup.enter="resizePage(option)"
                >
                  {{ option }}
                </v-btn>
                <span v-if="index + 1 < pagination.options.length">
                  |
                </span>
              </div>
            </v-btn-group>
          </div>
        </div>
        <div v-if="tab === 'list' && section.totalStudentCount" class="ml-2 mr-2">
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
  </div>
</template>

<script setup>
import {mdiAlertRhombus} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import CourseStudents from '@/components/course/CourseStudents'
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector'
import Pagination from '@/components/util/Pagination'
import SectionSpinner from '@/components/util/SectionSpinner'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {scrollToTop} from '@/lib/utils'
import {DateTime} from 'luxon'

export default {
  name: 'Course',
  components: {
    CourseStudents,
    Pagination,
    SectionSpinner,
    CuratedGroupSelector,
    Spinner
  },
  mixins: [Context, Util],
  data: () => ({
    error: null,
    featured: null,
    meetings: undefined,
    pagination: {
      currentPage: 1,
      defaultItemsPerPage: 50,
      itemsPerPage: 50,
      options: [50, 100]
    },
    section: {
      students: []
    },
    sectionId: undefined,
    termId: undefined
  }),
  created() {
    this.sectionId = this.$route.params.sectionId
    this.termId = this.$route.params.termId
    if (this.$route.query.p && !isNaN(this.$route.query.p)) {
      this.pagination.currentPage = parseInt(this.$route.query.p, 10)
    }
    if (this.$route.query.s && !isNaN(this.$route.query.s)) {
      const itemsPerPage = parseInt(this.$route.query.s, 10)
      if (this._includes(this.pagination.options, itemsPerPage)) {
        this.pagination.itemsPerPage = itemsPerPage
      } else {
        this.$router.push({
          query: {...this.$route.query, s: this.pagination.itemsPerPage}
        })
      }
    }
    if (this.$route.query.u) {
      this.featured = this.$route.query.u
    }
  },
  mounted() {
    scrollToTop()
  },
  methods: {
    featureSearchedStudent(data) {
      const section = this._clone(data)
      const subject = this._remove(section.students, student => {
        return student.uid === this.featured
      })
      const students = this._union(subject, section.students)
      // Discrepancies in our loch-hosted SIS data dumps may occasionally result in students without enrollment
      // objects. A placeholder object keeps the front end from breaking.
      this._each(students, student => {
        if (!student.enrollment) {
          student.enrollment = {canvasSites: []}
        }
      })
      section.students = students
      return section
    },
    goToPage(page) {
      this.pagination.currentPage = page
      this.$router.push({
        query: {...this.$route.query, p: this.pagination.currentPage}
      })
    },
    resizePage(itemsPerPage) {
      const previousItemsPerPage = this.pagination.itemsPerPage
      this.pagination.itemsPerPage = itemsPerPage
      this.pagination.currentPage = Math.round(this.pagination.currentPage * (previousItemsPerPage / this.pagination.itemsPerPage))
    }
  }
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
</style>
