<template>
  <div class="course-container">
    <Spinner />

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
                {{ 'Unit' | pluralize(section.units) }}
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
                <span :class="{'demo-mode-blur': user.inDemoMode}">
                  {{ meeting.instructors.join(', ') }}
                </span>
              </div>
              <div :id="'meetings-' + meetingIndex" class="course-details-meetings">
                <div>{{ meeting.days }}</div>
                <div>{{ meeting.time }}</div>
                <div>{{ meeting.location }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="course-terms">
        <h2 class="sr-only">Students</h2>
        <div v-if="!section.totalStudentCount" class="course-view-controls-container">
          <span class="has-error"><i class="fas fa-exclamation-triangle"></i></span>
          <span class="container-error">No students advised by your department are enrolled in this section.</span>
        </div>
        <div v-if="section.totalStudentCount" class="course-view-controls-container">
          <div>
            <CuratedGroupSelector
              v-if="!isEmpty(section.students) && (tab === 'list')"
              class="mr-2"
              :context-description="`Course ${section.displayName}`"
              :students="section.students" />
          </div>
          <div class="course-tabs-container">
            <div class="btn-group tab-btn-group pb-0" role="group" aria-label="Select results view">
              <button
                type="button"
                class="btn btn-secondary tab-button"
                aria-label="Switch to list view"
                :class="{'tab-button-selected': tab === 'list'}"
                @click="toggleView('list')">
                <i class="fas fa-list"></i> List
              </button>
              <button
                type="button"
                class="btn btn-secondary tab-button"
                aria-label="Switch to matrix view"
                :title="matrixDisabledMessage"
                :class="{'tab-button-selected': tab === 'matrix'}"
                :disabled="matrixDisabledMessage"
                @click="toggleView('matrix')">
                <i class="fas fa-table"></i> Matrix
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
                  href="#"
                  :class="{'selected': option==pagination.itemsPerPage}"
                  :title="`Show ${option} results per page`"
                  @click="resizePage(option)">
                  {{ option }}</a><span v-if="optionIndex + 1 < pagination.options.length">&nbsp;|&nbsp;</span>
              </li>
            </ul>
          </div>
        </div>

        <div v-if="tab === 'list' && section.totalStudentCount">
          <table id="course-list-view-table" class="course-list-view-table">
            <tr class="course-list-view-row">
              <th class="course-list-view-column course-list-view-column-checkbox course-list-view-column-header"></th>
              <th class="course-list-view-column course-list-view-column-avatar course-list-view-column-header">
                <span class="sr-only">Student Photo</span>
              </th>
              <th class="course-list-view-column course-list-view-column-profile course-list-view-column-header">
                <span class="sr-only">Student Profile</span>
              </th>
              <th class="course-list-view-column course-list-view-column-header">
                Course Site<span aria-hidden="true">(s)</span>
              </th>
              <th class="course-list-view-column course-list-view-column-header">Assignments Submitted</th>
              <th class="course-list-view-column course-list-view-column-header">Assignment Grades</th>
              <th class="course-list-view-column course-list-view-column-header">bCourses Activity</th>
              <th class="course-list-view-column course-list-view-column-header">
                Mid<span class="sr-only">point Grade</span>
              </th>
              <th class="course-list-view-column course-list-view-column-header">
                Final<span class="sr-only"> Grade</span>
              </th>
            </tr>
            <tr
              v-for="(student, index) in section.students"
              :key="student.uid"
              class="course-list-view-row"
              :class="{'list-group-item-info': featured===student.uid}">
              <td class="course-list-view-column course-list-view-column-checkbox">
                <CuratedStudentCheckbox :student="student" />
              </td>
              <td class="course-list-view-column course-list-view-column-avatar">
                <StudentAvatar :student="student" size="medium" />
              </td>
              <td class="course-list-view-column course-list-view-column-profile">
                <div>
                  <router-link :id="student.uid" :to="`/student/${student.uid}`">
                    <h3
                      class="course-student-name"
                      :class="{'demo-mode-blur': user.inDemoMode}">
                      {{ student.lastName }}<span v-if="student.firstName">, {{ student.firstName }}</span>
                    </h3>
                  </router-link>
                </div>
                <div :id="`row-${index}-student-sid`" class="student-sid" :class="{'demo-mode-blur': user.inDemoMode}">
                  {{ student.sid }}
                  <span v-if="student.enrollment.enrollmentStatus === 'W'" class="red-flag-status">WAITLISTED</span>
                  <span v-if="displayAsInactive(student)" class="red-flag-status">INACTIVE</span>
                </div>
                <div>
                  <span class="student-text">{{ student.level }}</span>
                </div>
                <div>
                  <div v-for="major in student.majors" :key="major" class="student-text">{{ major }}</div>
                </div>
                <div>
                  <div v-if="student.athleticsProfile" class="student-teams-container">
                    <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName" class="student-teams">
                      {{ membership.groupName }}
                    </div>
                  </div>
                </div>
              </td>

              <td class="course-list-view-column">
                <div class="course-list-view-column-canvas-sites">
                  <div
                    v-for="canvasSite in student.enrollment.canvasSites"
                    :key="canvasSite.courseCode"
                    class="course-list-view-column-canvas-sites-border">
                    <strong>{{ canvasSite.courseCode }}</strong>
                  </div>
                  <div
                    v-if="!student.enrollment.canvasSites.length"
                    class="course-list-view-column-canvas-sites-border">
                    No course site
                  </div>
                </div>
              </td>

              <td class="course-list-view-column">
                <div
                  v-if="student.enrollment.canvasSites.length"
                  class="course-list-view-column-canvas-sites">
                  <div
                    v-for="canvasSite in student.enrollment.canvasSites"
                    :key="canvasSite.canvasCourseId">
                    <span v-if="student.enrollment.canvasSites.length > 1" class="sr-only">
                      {{ canvasSite.courseCode }}
                    </span>
                    <div v-if="canvasSite.analytics.assignmentsSubmitted.courseDeciles">
                      <strong>{{ canvasSite.analytics.assignmentsSubmitted.student.raw }}</strong>
                      <div class="faint-text">
                        (Max: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[10] }})
                      </div>
                    </div>
                    <div v-if="!canvasSite.analytics.assignmentsSubmitted.courseDeciles">
                      No Data
                    </div>
                  </div>
                </div>
                <span
                  v-if="!student.enrollment.canvasSites.length"
                  class="course-list-view-column-canvas-sites"><span class="sr-only">No data</span>&mdash;</span>
              </td>

              <td class="course-list-view-column">
                <div class="course-list-view-column-canvas-sites">
                  <div
                    v-for="canvasSite in student.enrollment.canvasSites"
                    :key="canvasSite.canvasCourseId"
                    class="profile-boxplot-container">
                    <span v-if="student.enrollment.canvasSites.length > 1" class="sr-only">
                      {{ canvasSite.courseCode }}
                    </span>
                    <StudentBoxplot
                      v-if="canvasSite.analytics.currentScore.boxPlottable"
                      :dataset="canvasSite.analytics"
                      :numeric-id="student.uid + '-' + canvasSite.canvasCourseId.toString()"></StudentBoxplot>
                    <div v-if="canvasSite.analytics.currentScore.boxPlottable" class="sr-only">
                      <div>User score: {{ canvasSite.analytics.currentScore.student.raw }}</div>
                      <div>Maximum:  {{ canvasSite.analytics.currentScore.courseDeciles[10] }}</div>
                      <div>70th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[7] }}</div>
                      <div>50th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[5] }}</div>
                      <div>30th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[3] }}</div>
                      <div>Minimum: {{ canvasSite.analytics.currentScore.courseDeciles[0] }}</div>
                    </div>
                    <div v-if="!canvasSite.analytics.currentScore.boxPlottable">
                      <div v-if="canvasSite.analytics.currentScore.courseDeciles">
                        Score: <strong>{{ canvasSite.analytics.currentScore.student.raw }}</strong>
                        <div class="faint-text">
                          (Max: {{ canvasSite.analytics.currentScore.courseDeciles[10] }})
                        </div>
                      </div>
                      <div v-if="!canvasSite.analytics.currentScore.courseDeciles">
                        No Data
                      </div>
                    </div>
                  </div>
                  <span v-if="!student.enrollment.canvasSites.length"><span class="sr-only">No data</span>&mdash;</span>
                </div>
              </td>

              <td class="course-list-view-column">
                <div class="course-list-view-column-canvas-sites">
                  <div
                    v-for="canvasSite in student.enrollment.canvasSites"
                    :key="canvasSite.canvasCourseId"
                    class="profile-boxplot-container">
                    <span v-if="student.enrollment.canvasSites.length > 1" class="sr-only">
                      {{ canvasSite.courseCode }}
                    </span>
                    {{ lastActivityDays(canvasSite.analytics) }}
                  </div>
                  <span v-if="!student.enrollment.canvasSites.length"><span class="sr-only">No data</span>&mdash;</span>
                </div>
              </td>

              <td class="course-list-view-column">
                <span v-if="student.enrollment.midtermGrade" v-accessible-grade="student.enrollment.midtermGrade" class="cohort-grade"></span>
                <i
                  v-if="isAlertGrade(student.enrollment.midtermGrade)"
                  class="fas fa-exclamation-triangle boac-exclamation"></i>
                <span v-if="!student.enrollment.midtermGrade"><span class="sr-only">No data</span>&mdash;</span>
              </td>

              <td class="course-list-view-column">
                <span v-if="student.enrollment.grade" v-accessible-grade="student.enrollment.grade" class="cohort-grade"></span>
                <i
                  v-if="isAlertGrade(student.enrollment.grade)"
                  class="fas fa-exclamation-triangle boac-exclamation"></i>
                <span v-if="!student.enrollment.grade" class="cohort-grading-basis">
                  {{ student.enrollment.gradingBasis }}
                </span>
              </td>
            </tr>
          </table>

          <div class="course-pagination">
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
import _ from 'lodash';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import CuratedStudentCheckbox from '@/components/curated/CuratedStudentCheckbox';
import Loading from '@/mixins/Loading';
import Matrix from '@/components/matrix/Matrix';
import MatrixUtil from '@/components/matrix/MatrixUtil';
import Pagination from '@/components/util/Pagination';
import Scrollable from '@/mixins/Scrollable';
import Spinner from '@/components/util/Spinner';
import StudentAnalytics from '@/mixins/StudentAnalytics';
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentBoxplot from '@/components/student/StudentBoxplot';
import StudentMetadata from '@/mixins/StudentMetadata';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { getSection } from '@/api/course';

export default {
  name: 'Course',
  components: {
    CuratedGroupSelector,
    CuratedStudentCheckbox,
    Matrix,
    Pagination,
    Spinner,
    StudentAvatar,
    StudentBoxplot
  },
  mixins: [
    Loading,
    MatrixUtil,
    Scrollable,
    StudentAnalytics,
    StudentMetadata,
    UserMetadata,
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
      var section = _.clone(data);
      var subject = _.remove(section.students, student => {
        return student.uid === this.featured;
      });
      var students = _.union(subject, section.students);
      // Discrepancies in our loch-hosted SIS data dumps may occasionally result in students without enrollment
      // objects. A placeholder object keeps the front end from breaking.
      _.each(students, student => {
        if (!student.enrollment) {
          student.enrollment = { canvasSites: [] };
        }
      });
      section.students = students;
      return section;
    },
    initViewMode() {
      this.tab = _.includes(['list', 'matrix'], this.$route.query.tab)
        ? this.$route.query.tab
        : this.tab;
    },
    initPagination() {
      if (this.$route.query.p && !isNaN(this.$route.query.p)) {
        this.pagination.currentPage = parseInt(this.$route.query.p, 10);
      }
      if (this.$route.query.s && !isNaN(this.$route.query.s)) {
        var itemsPerPage = parseInt(this.$route.query.s, 10);
        if (_.includes(this.pagination.options, itemsPerPage)) {
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
      var limit = this.pagination.itemsPerPage;
      var offset =
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
      var currentItemsPerPage = this.pagination.itemsPerPage;
      var newPage = Math.round(
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
        this.exceedsMatrixThreshold(_.get(this.section, 'totalStudentCount'))
      ) {
        this.matrixDisabledMessage = this.exceedsMatrixThresholdMessage();
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
.course-list-view-column {
  line-height: 1.4em;
  padding: 5px 10px;
  vertical-align: top;
}
.course-list-view-column-avatar {
  width: 120px;
}
.course-list-view-column-canvas-sites {
  display: flex;
  flex-direction: column;
  font-size: 14px;
}
.course-list-view-column-canvas-sites > div {
  align-items: flex-start;
  flex: 0 0 50px;
}
.course-list-view-column-canvas-sites > div:not(:first-child) {
  margin-top: 5px;
}
.course-list-view-column-canvas-sites-border {
  align-self: flex-start;
  border-left: 1px solid #ddd;
  padding-left: 5px;
}
.course-list-view-column-checkbox {
  vertical-align: middle;
}
.course-list-view-column-header {
  color: #aaa;
  font-size: 12px;
  font-weight: normal;
  text-transform: uppercase;
  vertical-align: bottom;
}
.course-list-view-column-profile {
  width: 20%;
}
.course-list-view-column-profile button {
  padding: 2px 0 0 5px;
}
.course-list-view-row {
  border-bottom: 1px solid #ddd;
}
.course-list-view-table {
  width: 100%;
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
.course-pagination {
  margin-top: 20px;
}
.course-section-title {
  font-size: 16px;
  font-weight: bold;
  padding-top: 20px;
}
.course-student-name {
  color: #49b;
  font-size: 16px;
  margin: 0;
  max-width: 150px;
  padding: 0;
}
.course-tabs-container {
  flex: 0 0 200px;
  white-space: nowrap;
}
.course-term-name {
  font-size: 16px;
  font-weight: bold;
}
.course-terms {
  margin: 0 20px 0 20px;
}
.course-view-controls-container {
  align-items: baseline;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  padding: 20px 0 15px 0;
}
</style>
