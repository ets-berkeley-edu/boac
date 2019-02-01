<template>
  <div class="student-terms-container" id="student-terms-container">
    <h2 class="student-section-header">Classes</h2>
    <div class="student-term"
         v-for="(term, index) in (showAllTerms ? student.enrollmentTerms : student.enrollmentTerms.slice(0,1))"
         :key="index">
      <div class="term-no-enrollments"
           v-if="index === 0 && !student.hasCurrentTermEnrollments && (currentEnrollmentTermId > parseInt(term.termId))">
        <h3 class="student-term-header">{{ currentEnrollmentTerm }}</h3>
        <div class="term-no-enrollments-description">No enrollments</div>
      </div>

      <h3 class="student-term-header">{{term.termName}}</h3>
        <div v-for="(course, courseIndex) in term.enrollments" :key="courseIndex" class="student-course">
          <div class="student-course-heading">
            <div class="student-course-heading-start">
              <div class="student-course-heading-start-inner">
                <div class="student-course-heading-title-wrapper text-muted">
                  <span class="sr-only">Row {{courseIndex + 1}} of {{term.enrollments.length}}</span>
                  <div>
                    <h4 class="student-course-title">{{course.displayName}}</h4>
                  </div>
                  <b-btn :id="`term-${term.termId}-course-${courseIndex}-toggle`"
                         v-b-toggle="`course-canvas-data-${term.termId}-${courseIndex}`"
                         class="student-course-collapse-button"
                         variant="link">
                    <i class="when-course-closed fas fa-caret-right"></i>
                    <span class="when-course-closed sr-only">Show course details</span>
                    <i class="when-course-open fas fa-caret-down"></i>
                    <span class="when-course-open sr-only">Hide course details</span>
                  </b-btn>
                </div>
                <div>
                  <div class="student-course-sections">
                    <span v-for="(section, sectionIndex) in course.sections"
                          :key="sectionIndex">
                      <span v-if="section.displayName">
                        <span v-if="sectionIndex === 0">(</span><!--
                        --><router-link :id="`term-${term.termId}-section-${section.ccn}`"
                           :to="`/course/${term.termId}/${section.ccn}?u=${student.uid}`"
                           v-if="section.isViewableOnCoursePage">{{section.displayName}}</router-link><!--
                        --><span v-if="!section.isViewableOnCoursePage">
                             {{section.displayName}}</span><!--
                        --><span v-if="sectionIndex < course.sections.length - 1"> | </span><!--
                        --><span v-if="sectionIndex === course.sections.length - 1">)</span>
                      </span>
                    </span>
                  </div>
                  <span class="student-waitlisted red-flag-status" v-if="course.waitlisted">WAITLISTED</span>
                </div>
              </div>
              <div class="student-course-name">{{course.title}}</div>
            </div>
            <div class="student-course-heading-end">
              <div class="student-course-heading-units" v-if="'units' in course">
                {{ 'Unit' | pluralize(course.units) }}
              </div>
              <div class="student-course-heading-grades" v-if="'grade' in course || 'gradingBasis' in course">
                <div class="student-course-heading-grade">
                  Final:
                  <span class="student-course-grade"
                        v-if="course.grade">{{course.grade}}</span>
                  <span class="student-course-grading-basis"
                        v-if="!course.grade">{{course.gradingBasis}}</span>
                  <span class="student-course-grade"
                        v-if="!course.grade && !course.gradingBasis"><span class="sr-only">No data</span>&mdash;</span>
                </div>
                <div class="student-course-heading-grade" v-if="currentEnrollmentTermId === parseInt(term.termId)">
                  Mid:
                  <span class="student-course-grade"
                        v-if="course.midtermGrade">{{course.midtermGrade}}</span>
                  <span class="student-course-grade"
                        v-if="!course.midtermGrade"><span class="sr-only">No data</span>&mdash;</span>
                </div>
              </div>
            </div>
          </div>
          <b-collapse class="panel-body" :id="`course-canvas-data-${term.termId}-${courseIndex}`">
            <div v-for="(canvasSite, index) in course.canvasSites" :key="index" class="student-bcourses-wrapper">
              <h5 class="student-bcourses-site-code">
                <span class="sr-only">Course Site</span>
                {{canvasSite.courseCode}}
              </h5>
              <table class="student-bcourses">
                <tr>
                  <th class="student-bcourses-legend" scope="row">
                    Assignments Submitted
                  </th>
                  <td class="student-bcourses-summary">
                    <span v-if="canvasSite.analytics.assignmentsSubmitted.displayPercentile">
                      <strong>{{canvasSite.analytics.assignmentsSubmitted.displayPercentile}}</strong> percentile
                    </span>
                    <span class="student-bcourses-no-data"
                          v-if="!canvasSite.analytics.assignmentsSubmitted.displayPercentile">
                      No Assignments
                    </span>
                  </td>
                  <td>
                    <span v-if="canvasSite.analytics.assignmentsSubmitted.courseDeciles">
                      Score:
                      <strong>{{canvasSite.analytics.assignmentsSubmitted.student.raw}}</strong>
                      <span class="student-bcourses-maximum">
                        (Maximum: {{canvasSite.analytics.assignmentsSubmitted.courseDeciles[10]}})
                      </span>
                    </span>
                    <span class="student-bcourses-no-data"
                          v-if="!canvasSite.analytics.assignmentsSubmitted.courseDeciles">
                      No Data
                    </span>
                  </td>
                </tr>
                <tr>
                  <th class="student-bcourses-legend" scope="row">
                    Assignment Grades
                  </th>
                  <td class="student-bcourses-summary">
                    <span v-if="canvasSite.analytics.currentScore.displayPercentile">
                      <strong>{{canvasSite.analytics.currentScore.displayPercentile}}</strong> percentile
                    </span>
                    <span class="student-bcourses-no-data"
                          v-if="!canvasSite.analytics.currentScore.displayPercentile">
                      No Grades
                    </span>
                  </td>
                  <td class="profile-boxplot-container">
                    <StudentBoxplot :dataset="canvasSite.analytics"
                                    :numericId="canvasSite.canvasCourseId.toString()"
                                    v-if="canvasSite.analytics.currentScore.boxPlottable"/>
                    <div class="sr-only" v-if="canvasSite.analytics.currentScore.boxPlottable">
                      <div>User score: {{canvasSite.analytics.currentScore.student.raw}}</div>
                      <div>Maximum: {{canvasSite.analytics.currentScore.courseDeciles[10]}}</div>
                      <div>70th Percentile: {{canvasSite.analytics.currentScore.courseDeciles[7]}}</div>
                      <div>50th Percentile: {{canvasSite.analytics.currentScore.courseDeciles[5]}}</div>
                      <div>30th Percentile: {{canvasSite.analytics.currentScore.courseDeciles[3]}}</div>
                      <div>Minimum: {{canvasSite.analytics.currentScore.courseDeciles[0]}}</div>
                    </div>
                    <div v-if="!canvasSite.analytics.currentScore.boxPlottable">
                      <span class="student-bcourses-no-data"
                            v-if="canvasSite.analytics.currentScore.courseDeciles">
                        Score:
                        <strong>{{canvasSite.analytics.currentScore.student.raw}}</strong>
                        <span class="student-bcourses-maximum">
                          (Maximum: {{canvasSite.analytics.currentScore.courseDeciles[10]}})
                        </span>
                      </span>
                      <span class="student-bcourses-no-data"
                            v-if="!canvasSite.analytics.currentScore.courseDeciles">
                        No Data
                      </span>
                    </div>
                   </td>
                </tr>
                <tr v-if="currentEnrollmentTermId === parseInt(term.termId)">
                  <th class="student-bcourses-legend" scope="row">
                    Last bCourses Activity
                  </th>
                  <td colspan="2">
                    <div v-if="!canvasSite.analytics.lastActivity.student.raw">
                      <span :class="{'demo-mode-blur': user.inDemoMode}">{{student.name}}</span> has never visited this course site.
                    </div>
                    <div v-if="canvasSite.analytics.lastActivity.student.raw">
                      <span :class="{'demo-mode-blur': user.inDemoMode}">{{student.name}}</span>
                      last visited the course site {{lastActivityDays(canvasSite.analytics).toLowerCase()}}.
                      {{lastActivityInContext(canvasSite.analytics)}}
                    </div>
                  </td>
                </tr>
              </table>
            </div>
            <div class="student-bcourses-wrapper student-course-notation" v-if="isEmpty(course.canvasSites)">
              No additional information
            </div>
          </b-collapse>
        </div>
        <div class="student-course-heading student-course" v-if="term.enrolledUnits">
          <div class="student-course-heading-start"></div>
          <div class="student-course-heading-end">
            <div class="student-course-heading-units-total">
              Total {{term.enrolledUnits}}
            </div>
          </div>
        </div>
        <div class="student-course student-course-dropped"
             is-open="true"
             v-if="!isEmpty(term.droppedSections)">
          <div v-for="(droppedSection, index) in term.droppedSections" :key="index">
            <div class="student-course-dropped-title">
              {{droppedSection.displayName}} - {{droppedSection.component}} {{droppedSection.sectionNumber}}
            <div class="student-course-notation">
              <i class="fas fa-exclamation-triangle student-course-dropped-icon"></i> Dropped
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="get(student, 'enrollmentTerms.length') > 1" class="toggle-previous-semesters-wrapper">
      <button class="btn btn-link toggle-btn-link" @click="showAllTerms = !showAllTerms">
        <i :class="{'fas fa-caret-right': !showAllTerms, 'fas fa-caret-up': showAllTerms}"></i>
        <span v-if="!showAllTerms">View Previous Semesters</span>
        <span v-if="showAllTerms">Hide Previous Semesters</span>
      </button>
    </div>
    <div v-if="isEmpty(student.enrollmentTerms)">
      No courses
      <div v-if="student.sisProfile.withdrawalCancel">
        <span class="red-flag-small">
          {{student.sisProfile.withdrawalCancel.description}} ({{student.sisProfile.withdrawalCancel.reason}}) {{student.sisProfile.withdrawalCancel.date | date}}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import StudentAnalytics from '@/mixins/StudentAnalytics';
import StudentBoxplot from '@/components/student/StudentBoxplot';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'StudentClasses',
  mixins: [Context, StudentAnalytics, UserMetadata, Util],
  components: {
    StudentBoxplot
  },
  props: {
    student: Object
  },
  data: () => ({
    currentEnrollmentTerm: undefined,
    showAllTerms: false
  }),
  created() {
    this.currentEnrollmentTerm = this.find(
      this.get(this.student, 'enrollmentTerms'),
      {
        termId: this.currentEnrollmentTermId.toString()
      }
    );
  }
};
</script>

<style>
.profile-boxplot-container {
  align-items: flex-end;
  display: flex;
}
.profile-boxplot-container .highcharts-tooltip {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  line-height: 1.4em;
  min-width: 200px;
  padding: 0;
  z-index: 1;
}
.profile-boxplot-container .highcharts-tooltip::after {
  background: #fff;
  border: 1px solid #aaa;
  border-width: 0 1px 1px 0;
  content: '';
  display: block;
  height: 10px;
  position: absolute;
  top: 75px;
  left: -6px;
  transform: rotate(135deg);
  width: 10px;
}
.profile-boxplot-container g.highcharts-tooltip {
  display: none !important;
}
.profile-boxplot-container .highcharts-tooltip span {
  position: relative !important;
  top: 0 !important;
  left: 0 !important;
  width: auto !important;
}
</style>

<style scoped>
.collapsed > .when-course-open,
:not(.collapsed) > .when-course-closed {
  display: none;
}
.student-bcourses {
  line-height: 1.1;
  margin-bottom: 20px;
  width: 80%;
}
.student-bcourses td,
.student-bcourses th {
  font-size: 14px;
  padding: 0 25px 5px 0;
  text-align: left;
  vertical-align: top;
}
.student-bcourses-legend {
  color: #999;
  font-weight: normal;
  white-space: nowrap;
  width: 15em;
}
.student-bcourses-maximum {
  color: #666;
}
.student-bcourses-no-data {
  color: #666;
  font-style: italic;
}
.student-bcourses-site-code {
  font-size: 15px;
  margin-bottom: 5px;
}
.student-bcourses-summary {
  width: 12em;
}
.student-bcourses-wrapper {
  margin-top: 15px;
}
.student-course {
  border-top: 1px solid #999;
  margin-top: 20px;
}
.student-course-collapse-button {
  color: #337ab7;
  height: 15px;
  line-height: 1;
  margin-right: 10px;
  padding: 0;
  width: 12px;
}
.student-course-dropped {
  margin-top: 15px;
  padding-top: 15px;
}
.student-course-dropped-icon {
  color: #f0ad4e;
}
.student-course-dropped-title {
  font-weight: bold;
}
.student-course-grade {
  font-weight: bold;
}
.student-course-grading-basis {
  font-style: italic;
}
.student-course-heading {
  color: #777;
  display: flex;
  justify-content: space-between;
  flex-direction: row;
  font-weight: 500;
  line-height: 1.1;
  margin-top: 15px;
  width: 100%;
}
.student-course-heading-end {
  display: flex;
  flex: 0 0 200px;
}
.student-course-heading-grade {
  white-space: nowrap;
}
.student-course-heading-grades {
  display: flex;
  flex: 0 0 100px;
  flex-direction: column;
}
.student-course-heading-start {
  display: flex;
  flex-direction: column;
}
.student-course-heading-start-inner {
  align-items: baseline;
  display: flex;
  justify-content: flex-start;
}
.student-course-heading-title-wrapper {
  display: flex;
  flex-direction: row-reverse;
}
.student-course-heading-units {
  flex: 0 0 100px;
  white-space: nowrap;
}
.student-course-heading-units-total {
  color: #777;
  font-size: 16px;
  font-weight: 500;
  margin-top: 15px;
}
.student-course-name {
  font-size: 16px;
  font-weight: 400;
  margin: 5px 0 0;
}
.student-course-notation {
  color: #999;
  margin-bottom: 10px;
}
.student-course-title {
  font-size: 16px;
  margin: 0;
  padding-right: 5px;
  white-space: nowrap;
}
.student-course-sections {
  display: inline-block;
  font-weight: 400;
  white-space: nowrap;
}
.student-status-table td {
  padding: 3px 0;
  white-space: nowrap;
}
.student-status-table th {
  padding: 15px 0 3px 0;
}
.student-term {
  margin: 30px 0 10px 0;
}
.student-term .panel-group {
  margin-bottom: 10px;
}
.student-term-header {
  font-size: 20px;
  font-weight: 400;
  margin: 20px 0 15px 0;
  color: #999;
}
.student-terms {
  flex: 1;
  margin-left: 20px;
}
.student-terms-container {
  margin: 20px;
}
.student-waitlisted {
  padding-left: 5px;
}
.term-no-enrollments {
  border-bottom: 1px solid #999;
  margin-bottom: 30px;
  padding-bottom: 20px;
}
.term-no-enrollments-description {
  border-top: 1px solid #999;
  padding-top: 20px;
}
.toggle-previous-semesters-wrapper {
  text-align: center;
}
</style>
