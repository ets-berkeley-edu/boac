<template>
  <div class="w-100">
    <Spinner />
    <div v-if="!loading && !isToggling && error">
      <h1 class="page-section-header">Error</h1>
      <div class="faint-text">
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
              <h1 id="course-header" class="course-header">
                {{ section.displayName }}
              </h1>
              <div class="font-size-14">
                <h2 class="sr-only">Details</h2>
                {{ section.instructionFormat }}
                {{ section.sectionNum }}
                <span v-if="section.instructionFormat">&mdash;</span>
                <span v-if="section.units === null">Unknown Units</span>
                <span v-if="section.units !== null">
                  {{ pluralize('Unit', section.units) }}
                </span>
              </div>
              <div v-if="section.title" class="course-section-title">
                {{ section.title }}
              </div>
            </div>
            <div class="course-column-schedule">
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
                      ({{ moment(meeting.startDate).format('MMM D') }} to {{ moment(meeting.endDate).format('MMM D') }})
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
      <SectionSpinner :loading="!loading && isToggling" />
      <div v-if="!loading && !isToggling">
        <h2 class="sr-only">Students</h2>
        <div v-if="!section.totalStudentCount" class="d-flex ml-3 mt-3">
          <span class="has-error"><font-awesome icon="exclamation-triangle" /></span>
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
          <div v-if="!matrixDisabledMessage" class="d-flex mb-2 text-nowrap">
            <b-button-group
              id="tabs-button-group"
              :aria-label="`You are in ${tab} view. Click button to enter ${tab === 'list' ? 'matrix' : 'list'} view.`"
            >
              <b-button
                id="btn-tab-list"
                class="tab-button"
                :class="{'tab-button-selected': tab === 'list'}"
                :disabled="tab === 'list'"
                variant="secondary"
                @click="toggleView('list')"
                @keyup.enter="toggleView('list')"
              >
                <font-awesome icon="list" /> List
              </b-button>
              <b-button
                id="btn-tab-matrix"
                class="tab-button"
                :class="{'tab-button-selected': tab === 'matrix'}"
                :disabled="tab === 'matrix'"
                variant="secondary"
                @click="toggleView('matrix')"
                @keyup.enter="toggleView('matrix')"
              >
                <font-awesome icon="table" /> Matrix
              </b-button>
            </b-button-group>
          </div>
          <div v-if="tab === 'list' && (section.totalStudentCount > pagination.defaultItemsPerPage)" class="align-items-center d-flex ml-auto mr-3">
            <div id="view-per-page-label" class="pr-1">
              {{ section.totalStudentCount }} total students &mdash; View per page:&nbsp;
            </div>
            <b-button-group aria-labelledby="view-per-page-label">
              <div v-for="(option, index) in pagination.options" :key="index">
                <b-button
                  :id="`view-per-page-${option}`"
                  class="px-1"
                  :class="{'font-size-16 font-weight-bold text-dark': option === pagination.itemsPerPage}"
                  :disabled="option === pagination.itemsPerPage"
                  variant="link"
                  @click="resizePage(option)"
                  @keyup.enter="resizePage(option)"
                >
                  {{ option }}
                </b-button>
                <span v-if="index + 1 < pagination.options.length">
                  |
                </span>
              </div>
            </b-button-group>
          </div>
        </div>
        <div v-if="tab === 'list' && section.totalStudentCount" class="ml-2 mr-2">
          <CourseStudents :featured="featured" :section="section" />
          <div class="m-4">
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
        <div v-if="tab === 'matrix' && !isToggling && !loading && !error" id="matrix-outer" class="ml-3 mt-3">
          <Matrix :featured="featured" :section="section" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CourseStudents from '@/components/course/CourseStudents'
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector'
import Matrix from '@/components/matrix/Matrix'
import Pagination from '@/components/util/Pagination'
import SectionSpinner from '@/components/util/SectionSpinner'
import Spinner from '@/components/util/Spinner'
import store from '@/store'
import Util from '@/mixins/Util'
import {getSection} from '@/api/course'
import {hasMatrixPlottableProperty} from '@/berkeley'
import {scrollToTop} from '@/utils'

export default {
  name: 'Course',
  components: {
    CourseStudents,
    Matrix,
    Pagination,
    SectionSpinner,
    CuratedGroupSelector,
    Spinner
  },
  mixins: [Context, Util],
  data: () => ({
    error: null,
    featured: null,
    isToggling: false,
    matrixDisabledMessage: null,
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
    tab: 'list',
    termId: undefined
  }),
  created() {
    this.sectionId = this.$route.params.sectionId
    this.termId = this.$route.params.termId
    this.tab = this._includes(['list', 'matrix'], this.$route.query.tab) ? this.$route.query.tab : this.tab
    this.initPagination()
    this.toggleView(this.tab, 'course-header')
  },
  mounted() {
    scrollToTop()
  },
  methods: {
    exceedsMatrixThreshold(studentCount) {
      return (
        parseInt(studentCount, 10) >
        parseInt(this.config.disableMatrixViewThreshold, 10)
      )
    },
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
    initPagination() {
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
    loadListView() {
      const limit = this.pagination.itemsPerPage
      const offset = this.pagination.currentPage === 0 ? 0 : (this.pagination.currentPage - 1) * limit
      this.$ga.course('view', this.section.displayName)
      return getSection(this.termId, this.sectionId, offset, limit, this.featured)
    },
    loadMatrixView() {
      this.$ga.course('matrix', this.section.displayName)
      return getSection(this.termId, this.sectionId)
    },
    partitionPlottableStudents() {
      const xAxisMeasure = this._get(this, 'selectedAxes.x') || 'analytics.currentScore'
      const yAxisMeasure = this._get(this, 'selectedAxes.y') || 'cumulativeGPA'
      return this._partition(
        this.section.students,
        student =>
          hasMatrixPlottableProperty(student, xAxisMeasure) &&
          hasMatrixPlottableProperty(student, yAxisMeasure)
      )
    },
    resizePage(itemsPerPage) {
      this.isToggling = true
      const previousItemsPerPage = this.pagination.itemsPerPage
      this.pagination.itemsPerPage = itemsPerPage
      this.pagination.currentPage = Math.round(this.pagination.currentPage * (previousItemsPerPage / this.pagination.itemsPerPage))
      this.toggleView(this.tab)
    },
    toggleView(tabName, focusAfter) {
      this.isToggling = true
      this.tab = tabName
      this.$announcer.polite(`Loading ${this.tab} view of ${this.section.title || this.section.displayName}`)

      const done = data => {
        this.setPageTitle(data.displayName)
        this.section = this.featureSearchedStudent(data)
        this.meetings = this._orderBy(this.section.meetings, ['startDate'], ['asc'])
        let totalStudentCount = this._get(this.section, 'totalStudentCount')
        if (this.exceedsMatrixThreshold(totalStudentCount)) {
          this.matrixDisabledMessage = `Sorry, the matrix view is only available when total student count is below ${this.config.disableMatrixViewThreshold}. Please narrow your search.`
        } else {
          if (this.partitionPlottableStudents()[0].length === 0) {
            this.matrixDisabledMessage = 'No student data is available to display.'
          } else {
            this.matrixDisabledMessage = null
          }
        }
        this.isToggling = false
        let message = `Course ${data.displayName} loaded in ${tabName} view. `
        if (tabName === 'matrix' || totalStudentCount < this.pagination.itemsPerPage) {
          message += `Showing all ${totalStudentCount} students.`
        } else {
          message += `Showing ${this.pagination.itemsPerPage} of ${totalStudentCount} total students.`
        }
        store.dispatch('context/loadingComplete')
        this.$announcer.polite(message)
        this.putFocusNextTick(focusAfter || `btn-tab-${this.tab === 'list' ? 'matrix' : 'list'}`)
      }
      const loadView = tabName === 'matrix' ? this.loadMatrixView : this.loadListView
      loadView().then(done)
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
.tab-button {
  background-color: #6bd;
  border: 1px solid transparent;
  color: #fff;
  font-size: 14px;
  opacity: 1;
}
.tab-button:hover {
  color: #cef;
}
.tab-button:disabled {
  cursor: not-allowed;
}
.tab-button-selected {
  background-color: #49b;
}
.tab-button-selected:active,
.tab-button-selected:focus {
  color: #fff;
  outline: none !important;
}
</style>
