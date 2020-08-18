<template>
  <div class="course-container">
    <Spinner alert-prefix="Course" />

    <div v-if="!loading && error">
      <h1 class="page-section-header">Error</h1>
      <div class="faint-text">
        <span v-if="error.message">{{ error.message }}</span>
        <span v-if="!error.message">Sorry, there was an error retrieving data.</span>
      </div>
    </div>

    <div v-if="!loading && !error" class="course-container-inner">
      <a
        v-if="section.totalStudentCount > pagination.itemsPerPage"
        id="skip-to-pagination-widget"
        href="#pagination-widget"
        class="sr-only">Skip to pagination widget</a>
      <div>
        <div class="course-container-summary">
          <div class="course-column-description">
            <h1
              id="course-header"
              ref="pageHeader"
              class="course-header"
              tabindex="0">
              {{ section.displayName }}
            </h1>
            <div class="course-details-section">
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
              <span role="alert" aria-live="polite">
                {{ section.title }}
              </span>
            </div>
          </div>
          <div class="course-column-schedule">
            <h2 class="sr-only">Schedule</h2>
            <div class="course-term-name">{{ section.termName }}</div>
            <div v-for="(meeting, meetingIndex) in section.meetings" :key="meetingIndex">
              <div v-if="!isEmpty(meeting.instructors)" class="course-details-instructors">
                <span :id="'instructors-' + meetingIndex" class="course-instructors-header">
                  {{ meeting.instructors.length > 1 ? 'Instructors:' : 'Instructor:' }}
                </span>
                {{ meeting.instructors.join(', ') }}
              </div>
              <div :id="'meetings-' + meetingIndex" class="course-details-meetings">
                <div>{{ meeting.days }}</div>
                <div>{{ meeting.time }}</div>
                <div>{{ meeting.location }}<span v-if="meeting.instructionModeName"><span v-if="meeting.location"> &mdash; </span>{{ meeting.instructionModeName }}</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div>
        <h2 class="sr-only">Students</h2>
        <div v-if="!section.totalStudentCount" class="d-flex ml-3 mt-3">
          <span class="has-error"><font-awesome icon="exclamation-triangle" /></span>
          <span class="container-error">No students advised by your department are enrolled in this section.</span>
        </div>
        <div v-if="section.totalStudentCount" class="d-flex justify-content-start align-items-baseline m-3">
          <div>
            <CuratedGroupSelector
              v-if="!isEmpty(section.students) && (tab === 'list')"
              :context-description="`Course ${section.displayName}`"
              :ga-event-tracker="$ga.courseEvent"
              :students="section.students"
              class="mr-2" />
          </div>
          <div class="course-tabs-container">
            <div class="btn-group tab-btn-group pb-0" role="group" aria-label="Select results view">
              <button
                id="btn-tab-list"
                :class="{'tab-button-selected': tab === 'list'}"
                type="button"
                class="btn btn-secondary tab-button"
                aria-label="Switch to list view"
                @click="toggleView('list')"
                @keyup.enter="toggleView('list')">
                <font-awesome icon="list" /> List
              </button>
              <button
                id="btn-tab-matrix"
                :title="matrixDisabledMessage"
                :class="{'tab-button-selected': tab === 'matrix'}"
                :disabled="matrixDisabledMessage"
                type="button"
                class="btn btn-secondary tab-button"
                aria-label="Switch to matrix view"
                @click="toggleView('matrix')"
                @keyup.enter="toggleView('matrix')">
                <font-awesome icon="table" /> Matrix
              </button>
            </div>
          </div>
          <div
            v-if="tab === 'list' && (section.totalStudentCount > pagination.defaultItemsPerPage)"
            class="flex-container course-page-size">
            {{ section.totalStudentCount }} total students &mdash; View per page:&nbsp;
            <ul class="flex-container">
              <li v-for="(option, optionIndex) in pagination.options" :key="optionIndex">
                <a
                  :class="{'selected': option === pagination.itemsPerPage}"
                  :title="`Show ${option} results per page`"
                  href="#"
                  @click="resizePage(option)"
                  @keyup.enter="resizePage(option)">
                  {{ option }}</a><span v-if="optionIndex + 1 < pagination.options.length">&nbsp;|&nbsp;</span>
              </li>
            </ul>
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
                :total-rows="section.totalStudentCount" />
            </div>
          </div>
        </div>
        <div v-if="tab === 'matrix' && !loading && !error" id="matrix-outer" class="matrix-outer">
          <Matrix :featured="featured" :section="section" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CourseStudents from '@/components/course/CourseStudents';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import Loading from '@/mixins/Loading';
import Matrix from '@/components/matrix/Matrix';
import MatrixUtil from '@/components/matrix/MatrixUtil';
import Pagination from '@/components/util/Pagination';
import Scrollable from '@/mixins/Scrollable';
import Spinner from '@/components/util/Spinner';
import Util from '@/mixins/Util';
import { getSection } from '@/api/course';

export default {
  name: 'Course',
  components: {
    CourseStudents,
    CuratedGroupSelector,
    Matrix,
    Pagination,
    Spinner,
  },
  mixins: [
    Loading,
    MatrixUtil,
    Scrollable,
    Util
  ],
  data: () => ({
    error: null,
    featured: null,
    matrixDisabledMessage: null,
    pagination: {
      currentPage: 1,
      defaultItemsPerPage: 50,
      itemsPerPage: 50,
      options: [50, 100]
    },
    section: {
      students: []
    },
    tab: 'list'
  }),
  created() {
    this.initViewMode();
    this.initPagination();
    if (this.tab === 'matrix') {
      this.loadMatrixView();
    } else {
      this.loadListView();
    }
  },
  mounted() {
    this.scrollToTop();
  },
  methods: {
    featureSearchedStudent(data) {
      const section = this.clone(data);
      const subject = this.remove(section.students, student => {
        return student.uid === this.featured;
      });
      const students = this.union(subject, section.students);
      // Discrepancies in our loch-hosted SIS data dumps may occasionally result in students without enrollment
      // objects. A placeholder object keeps the front end from breaking.
      this.each(students, student => {
        if (!student.enrollment) {
          student.enrollment = { canvasSites: [] };
        }
      });
      section.students = students;
      return section;
    },
    initViewMode() {
      this.tab = this.includes(['list', 'matrix'], this.$route.query.tab)
        ? this.$route.query.tab
        : this.tab;
    },
    initPagination() {
      if (this.$route.query.p && !isNaN(this.$route.query.p)) {
        this.pagination.currentPage = parseInt(this.$route.query.p, 10);
      }
      if (this.$route.query.s && !isNaN(this.$route.query.s)) {
        const itemsPerPage = parseInt(this.$route.query.s, 10);
        if (this.includes(this.pagination.options, itemsPerPage)) {
          this.pagination.itemsPerPage = itemsPerPage;
        } else {
          this.$router.push({
            query: { ...this.$route.query, s: this.pagination.itemsPerPage }
          });
        }
      }
      if (this.$route.query.u) {
        this.featured = this.$route.query.u;
      }
    },
    loadListView() {
      const limit = this.pagination.itemsPerPage;
      const offset =
        this.pagination.currentPage === 0
          ? 0
          : (this.pagination.currentPage - 1) * limit;
      getSection(
        this.$route.params.termId,
        this.$route.params.sectionId,
        offset,
        limit,
        this.featured
      ).then(data => {
        if (data) {
          this.updateCourseData(data);
          this.loaded();
        } else {
          this.$router.push({ path: '/404' });
        }
      });
    },
    loadMatrixView() {
      getSection(this.$route.params.termId, this.$route.params.sectionId).then(
        data => {
          this.updateCourseData(data);
          this.loaded();
        }
      );
    },
    goToPage(page) {
      this.pagination.currentPage = page;
      this.$router.push({
        query: { ...this.$route.query, p: this.pagination.currentPage }
      });
    },
    resizePage(selectedItemsPerPage) {
      const currentItemsPerPage = this.pagination.itemsPerPage;
      const newPage = Math.round(
        this.pagination.currentPage *
          (currentItemsPerPage / selectedItemsPerPage)
      );
      this.$router.push({
        query: {
          ...this.$route.query,
          p: newPage,
          s: selectedItemsPerPage
        }
      });
    },
    toggleView(tabName) {
      this.$router.push({
        query: { ...this.$route.query, tab: tabName }
      });
    },
    updateCourseData(data) {
      this.setPageTitle(data.displayName);
      this.section = this.featureSearchedStudent(data);
      if (
        this.exceedsMatrixThreshold(this.get(this.section, 'totalStudentCount'))
      ) {
        this.matrixDisabledMessage = `Sorry, the matrix view is only available when total student count is below ${this.$config.disableMatrixViewThreshold}. Please narrow your search.`;
      } else {
        var plottableStudents = this.partitionPlottableStudents();
        if (plottableStudents[0].length === 0) {
          this.matrixDisabledMessage =
            'No student data is available to display.';
        } else {
          this.matrixDisabledMessage = null;
        }
      }
    }
  }
};
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
.course-container {
  width: 100%;
}
.course-container-inner {
  display: flex;
  flex-direction: column;
}
.course-container-summary {
  display: flex;
  flex-direction: row;
}
.course-details-instructors {
  margin-top: 15px;
}
.course-details-meetings {
  font-size: 16px;
}
.course-details-section {
  font-size: 14px;
}
.course-header {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 5px 0;
}
.course-instructors-header {
  font-size: 16px;
  font-weight: bold;
}
.course-page-size {
  margin-left: auto;
}
.course-page-size a {
  text-decoration: none;
}
.course-page-size a.selected {
  color: #000;
  font-weight: bold;
}
.course-section-title {
  font-size: 16px;
  font-weight: bold;
  padding-top: 20px;
}
.course-tabs-container {
  flex: 0 0 200px;
  white-space: nowrap;
}
.course-term-name {
  font-size: 16px;
  font-weight: bold;
}
</style>
