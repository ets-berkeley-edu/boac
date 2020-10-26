<template>
  <div id="student-terms-container" class="m-3">
    <h2 class="student-section-header">Classes</h2>
    <div
      v-for="(term, index) in (showAllTerms ? student.enrollmentTerms : relevantTerms)"
      :key="index"
      class="student-term">
      <div
        v-if="index === 0 && !student.hasCurrentTermEnrollments && ($config.currentEnrollmentTermId > parseInt(term.termId))"
        class="term-no-enrollments">
        <h3 class="student-term-header">{{ $config.currentEnrollmentTerm }}</h3>
        <div class="term-no-enrollments-description">No enrollments</div>
        <StudentWithdrawalCancel
          v-if="student.sisProfile.withdrawalCancel"
          :withdrawal="student.sisProfile.withdrawalCancel"
          :term-id="$config.currentEnrollmentTermId" />
      </div>
      <h3 :id="`term-header-${index}`" tabindex="0" class="student-term-header">{{ term.termName }}</h3>
      <StudentAcademicStanding :standing="term.academicStanding" :term-id="term.termId" />
      <StudentWithdrawalCancel
        v-if="student.sisProfile.withdrawalCancel"
        :withdrawal="student.sisProfile.withdrawalCancel"
        :term-id="term.termId" />
      <div v-for="(course, courseIndex) in term.enrollments" :key="courseIndex" class="student-course">
        <div class="student-course-heading">
          <div class="student-course-heading-start">
            <div class="student-course-heading-start-inner">
              <div class="student-course-heading-title-wrapper text-muted">
                <span class="sr-only">Row {{ courseIndex + 1 }} of {{ term.enrollments.length }}</span>
                <div>
                  <h4 class="student-course-title">{{ course.displayName }}</h4>
                </div>
                <b-btn
                  v-if="$currentUser.canAccessCanvasData && !student.fullProfilePending"
                  :id="`term-${term.termId}-course-${courseIndex}-toggle`"
                  v-b-toggle="`course-canvas-data-${term.termId}-${courseIndex}`"
                  class="student-course-collapse-button"
                  variant="link">
                  <font-awesome icon="caret-right" class="when-course-closed" />
                  <span class="when-course-closed sr-only">Show {{ course.displayName }} class details for {{ student.name }}</span>
                  <font-awesome icon="caret-down" class="when-course-open" />
                  <span class="when-course-open sr-only">Hide {{ course.displayName }} class details for {{ student.name }}</span>
                </b-btn>
              </div>
              <div>
                <div class="student-course-sections">
                  <span
                    v-for="(section, sectionIndex) in course.sections"
                    :key="sectionIndex">
                    <span v-if="section.displayName">
                      <span v-if="sectionIndex === 0">(</span><!--
                        --><router-link
                      v-if="section.isViewableOnCoursePage"
                      :id="`term-${term.termId}-section-${section.ccn}`"
                      :to="`/course/${term.termId}/${section.ccn}?u=${student.uid}`"><span class="sr-only">Link to {{ course.displayName }}, </span>{{ section.displayName }}</router-link><!--
                        --><span v-if="!section.isViewableOnCoursePage">{{ section.displayName }}</span><!--
                        --><span v-if="sectionIndex < course.sections.length - 1"> | </span><!--
                        --><span v-if="sectionIndex === course.sections.length - 1">)</span>
                    </span>
                  </span>
                </div>
                <span
                  v-if="course.waitlisted"
                  :id="`student-${student.uid}-waitlisted-for-${term.termId}-${course.sections.length ? course.sections[0].ccn : course.displayName}`"
                  class="pl-1 red-flag-status">WAITLISTED</span>
              </div>
            </div>
            <div class="student-course-name">{{ course.title }}</div>
          </div>
          <div class="student-course-heading-end">
            <div v-if="'units' in course" class="student-course-heading-units">
              {{ pluralize('Unit', course.units) }}
            </div>
            <div v-if="'grade' in course || 'gradingBasis' in course" class="student-course-heading-grades">
              <div class="text-nowrap">
                Final:
                <span
                  v-if="course.grade"
                  v-accessible-grade="course.grade"
                  class="font-weight-bold"></span>
                <span
                  v-if="!course.grade"
                  class="font-italic">{{ course.gradingBasis }}</span>
                <span
                  v-if="!course.grade && !course.gradingBasis"
                  class="font-weight-bold"><span class="sr-only">No data</span>&mdash;</span>
              </div>
              <div v-if="$config.currentEnrollmentTermId === parseInt(term.termId)" class="text-nowrap">
                Mid:
                <span
                  v-if="course.midtermGrade"
                  v-accessible-grade="course.midtermGrade"
                  class="font-weight-bold"></span>
                <span
                  v-if="!course.midtermGrade"
                  class="font-weight-bold"><span class="sr-only">No data</span>&mdash;</span>
              </div>
            </div>
          </div>
        </div>
        <b-collapse
          v-if="$currentUser.canAccessCanvasData && !student.fullProfilePending"
          :id="`course-canvas-data-${term.termId}-${courseIndex}`"
          class="panel-body">
          <div v-for="(canvasSite, csIndex) in course.canvasSites" :key="csIndex" class="student-bcourses-wrapper">
            <h5 class="student-bcourses-site-code">
              <span class="sr-only">Course Site</span>
              {{ canvasSite.courseCode }}
            </h5>
            <table class="student-bcourses">
              <tr>
                <th class="student-bcourses-legend" scope="row">
                  Assignments Submitted
                </th>
                <td class="student-bcourses-summary">
                  <span v-if="canvasSite.analytics.assignmentsSubmitted.displayPercentile">
                    <strong>{{ canvasSite.analytics.assignmentsSubmitted.displayPercentile }}</strong> percentile
                  </span>
                  <span
                    v-if="!canvasSite.analytics.assignmentsSubmitted.displayPercentile"
                    class="font-italic text-muted">
                    No Assignments
                  </span>
                </td>
                <td class="profile-boxplot-container">
                  <StudentBoxplot
                    v-if="canvasSite.analytics.assignmentsSubmitted.boxPlottable"
                    :dataset="canvasSite.analytics.assignmentsSubmitted"
                    :numeric-id="canvasSite.canvasCourseId.toString()" />
                  <div v-if="canvasSite.analytics.assignmentsSubmitted.boxPlottable" class="sr-only">
                    <div>User score: {{ canvasSite.analytics.assignmentsSubmitted.student.raw }}</div>
                    <div>Maximum: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[10] }}</div>
                    <div>70th Percentile: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[7] }}</div>
                    <div>50th Percentile: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[5] }}</div>
                    <div>30th Percentile: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[3] }}</div>
                    <div>Minimum: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[0] }}</div>
                  </div>
                  <div v-if="!canvasSite.analytics.assignmentsSubmitted.boxPlottable">
                    <span v-if="canvasSite.analytics.assignmentsSubmitted.courseDeciles">
                      Score:
                      <strong>{{ canvasSite.analytics.assignmentsSubmitted.student.raw }}</strong>
                      <span class="text-muted">
                        (Maximum: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[10] }})
                      </span>
                    </span>
                    <span
                      v-if="!canvasSite.analytics.assignmentsSubmitted.courseDeciles"
                      class="font-italic text-muted">
                      No Data
                    </span>
                  </div>
                </td>
              </tr>
              <tr>
                <th class="student-bcourses-legend" scope="row">
                  Assignment Grades
                </th>
                <td class="student-bcourses-summary">
                  <span v-if="canvasSite.analytics.currentScore.displayPercentile">
                    <strong>{{ canvasSite.analytics.currentScore.displayPercentile }}</strong> percentile
                  </span>
                  <span
                    v-if="!canvasSite.analytics.currentScore.displayPercentile"
                    class="font-italic text-muted">
                    No Grades
                  </span>
                </td>
                <td class="profile-boxplot-container">
                  <StudentBoxplot
                    v-if="canvasSite.analytics.currentScore.boxPlottable"
                    :dataset="canvasSite.analytics.currentScore"
                    :numeric-id="canvasSite.canvasCourseId.toString()" />
                  <div v-if="canvasSite.analytics.currentScore.boxPlottable" class="sr-only">
                    <div>User score: {{ canvasSite.analytics.currentScore.student.raw }}</div>
                    <div>Maximum: {{ canvasSite.analytics.currentScore.courseDeciles[10] }}</div>
                    <div>70th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[7] }}</div>
                    <div>50th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[5] }}</div>
                    <div>30th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[3] }}</div>
                    <div>Minimum: {{ canvasSite.analytics.currentScore.courseDeciles[0] }}</div>
                  </div>
                  <div v-if="!canvasSite.analytics.currentScore.boxPlottable">
                    <span
                      v-if="canvasSite.analytics.currentScore.courseDeciles"
                      class="font-italic text-muted">
                      Score:
                      <strong>{{ canvasSite.analytics.currentScore.student.raw }}</strong>
                      <span class="text-muted">
                        (Maximum: {{ canvasSite.analytics.currentScore.courseDeciles[10] }})
                      </span>
                    </span>
                    <span
                      v-if="!canvasSite.analytics.currentScore.courseDeciles"
                      class="font-italic text-muted">
                      No Data
                    </span>
                  </div>
                </td>
              </tr>
              <tr v-if="$config.currentEnrollmentTermId === parseInt(term.termId)">
                <th class="student-bcourses-legend" scope="row">
                  Last bCourses Activity
                </th>
                <td colspan="2">
                  <div v-if="!canvasSite.analytics.lastActivity.student.raw">
                    <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.name }}</span> has never visited this course site.
                  </div>
                  <div v-if="canvasSite.analytics.lastActivity.student.raw">
                    <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.name }}</span>
                    last visited the course site {{ lastActivityDays(canvasSite.analytics).toLowerCase() }}.
                    {{ lastActivityInContext(canvasSite.analytics) }}
                  </div>
                </td>
              </tr>
            </table>
          </div>
          <div v-if="$_.isEmpty(course.canvasSites)" class="student-bcourses-wrapper student-course-notation">
            No additional information
          </div>
        </b-collapse>
      </div>
      <div v-if="term.enrolledUnits" class="student-course-heading student-course">
        <div class="student-course-heading-start"></div>
        <div class="student-course-heading-end">
          <div class="student-course-heading-units-total">
            <span>Total {{ term.enrolledUnits }}</span>
            <span class="sr-only">units</span>
            <!--
            TODO: Until SISRP-48560 is resolved we will suppress unitsMin and unitsMax data in BOA.
            <span
              v-if="$config.currentEnrollmentTermId === parseInt(term.termId) && get(student, 'sisProfile.currentTerm.unitsMin')"
              class="student-course-heading-units-override">
              <span>Min&nbsp;Approved </span><span :id="`term-${term.termId}-min-units`">{{ student.sisProfile.currentTerm.unitsMin }}</span>
            </span>
            <span
              v-if="$config.currentEnrollmentTermId === parseInt(term.termId) && get(student, 'sisProfile.currentTerm.unitsMax')"
              class="student-course-heading-units-override">
              <span>Max&nbsp;Approved </span><span :id="`term-${term.termId}-max-units`">{{ student.sisProfile.currentTerm.unitsMax }}</span>
            </span>
            -->
          </div>
        </div>
      </div>
      <div
        v-if="!$_.isEmpty(term.droppedSections)"
        class="student-course mt-3 pt-1"
        is-open="true">
        <div v-for="(droppedSection, dsIndex) in term.droppedSections" :key="dsIndex" class="ml-4">
          <div class="font-weight-bold">
            {{ droppedSection.displayName }} - {{ droppedSection.component }} {{ droppedSection.sectionNumber }}
            <div class="student-course-notation">
              <font-awesome icon="exclamation-triangle" class="student-course-dropped-icon" /> Dropped
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="$_.get(student, 'enrollmentTerms.length') > $_.size(relevantTerms)" class="text-center">
      <b-btn
        id="toggle-show-all-terms"
        variant="link"
        @click.prevent="toggleShowAllTerms">
        <font-awesome :icon="showAllTerms ? 'caret-up' : 'caret-right'" />
        <span class="no-wrap pl-1">{{ showAllTerms ? 'Hide' : 'Show' }} Previous Semesters</span>
      </b-btn>
    </div>
    <div v-if="$_.isEmpty(student.enrollmentTerms)">
      No courses
      <StudentWithdrawalCancel v-if="student.sisProfile.withdrawalCancel" :withdrawal="student.sisProfile.withdrawalCancel" />
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import StudentAcademicStanding from '@/components/student/profile/StudentAcademicStanding'
import StudentAnalytics from '@/mixins/StudentAnalytics'
import StudentBoxplot from '@/components/student/StudentBoxplot'
import StudentWithdrawalCancel from '@/components/student/profile/StudentWithdrawalCancel'
import Util from '@/mixins/Util'

export default {
  name: 'StudentClasses',
  components: {
    StudentAcademicStanding,
    StudentWithdrawalCancel,
    StudentBoxplot
  },
  mixins: [Context, StudentAnalytics, Util],
  props: {
    student: Object
  },
  data: () => ({
    relevantTerms: undefined,
    showAllTerms: false
  }),
  created() {
    const currentTermIndex = this.$_.findIndex(this.student.enrollmentTerms, term => {
      return term.termId === this.$_.toString(this.$config.currentEnrollmentTermId)
    })
    const index = currentTermIndex < 0 ? 0 : currentTermIndex
    this.relevantTerms = this.student.enrollmentTerms.slice(0, index + 1)
  },
  methods: {
    toggleShowAllTerms() {
      this.showAllTerms = !this.showAllTerms
      this.putFocusNextTick(this.showAllTerms ? 'term-header-1' : 'term-header-0')
    }
  }
}
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
.student-course-dropped-icon {
  color: #f0ad4e;
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
.student-course-heading-units-override {
  font-weight: 400;
  margin-top: 5px;
}
.student-course-heading-units-total {
  color: #777;
  display: flex;
  flex: 0 0 200px;
  flex-direction: column;
  font-size: 16px;
  font-weight: 500;
  margin-top: 15px;
  white-space: nowrap;
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
  display: inline-block;
  font-size: 20px;
  font-weight: 600;
  margin: 0 15px 0 0;
  color: #666;
}
.term-no-enrollments {
  border-bottom: 1px solid #999;
  margin-bottom: 30px;
  padding-bottom: 20px;
}
.term-no-enrollments-description {
  border-top: 1px solid #999;
  margin-top: 20px;
  padding-top: 20px;
}
</style>
