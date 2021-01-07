<template>
  <div class="student-course">
    <div role="row" class="student-course-row" :class="{'student-course-expanded': detailsVisible}">
      <div role="cell" class="student-course-column-name">
        <b-btn
          v-if="$currentUser.canAccessCanvasData && !student.fullProfilePending"
          :id="`term-${term.termId}-course-${index}-toggle`"
          v-b-toggle="`course-details-${term.termId}-${index}`"
          class="d-flex flex-row-reverse justify-content-between student-course-collapse-button"
          variant="link"
          :aria-expanded="detailsVisible ? 'true' : 'false'"
          :aria-controls="`course-details-${term.termId}-${index}`"
          @click="detailsVisible = !detailsVisible">
          <span>{{ course.displayName }}</span>
          <font-awesome icon="caret-right" class="student-course-collapse-icon when-course-closed mr-1" />
          <span class="when-course-closed sr-only">Show {{ course.displayName }} class details for {{ student.name }}</span>
          <font-awesome icon="caret-down" class="student-course-collapse-icon when-course-open mr-1" />
          <span class="when-course-open sr-only">Hide {{ course.displayName }} class details for {{ student.name }}</span>
        </b-btn>
      </div>
      <div role="cell" class="student-course-column-mid-grade text-nowrap">
        <span
          v-if="course.midtermGrade"
          v-accessible-grade="course.midtermGrade"></span>
        <span
          v-if="!course.midtermGrade"><span class="sr-only">No data</span>&mdash;</span>
      </div>
      <div role="cell" class="student-course-column-final-grade text-nowrap">
        <span
          v-if="course.grade"
          v-accessible-grade="course.grade"></span>
        <span
          v-if="!course.grade"
          class="font-italic text-muted">{{ course.gradingBasis }}</span>
        <span
          v-if="!course.grade && !course.gradingBasis"><span class="sr-only">No data</span>&mdash;</span>
      </div>
      <div role="cell" class="student-course-column-units text-nowrap">
        {{ course.units }}
      </div>
    </div>
    <b-collapse
      :id="`course-details-${term.termId}-${index}`"
      role="row"
      class="student-course-details">
      <div class="student-course-name">{{ course.displayName }}</div>
      <div class="student-course-sections">
        <span
          v-for="(section, sectionIndex) in course.sections"
          :key="sectionIndex">
          <span v-if="section.displayName">
            <span v-if="sectionIndex === 0"></span><!--
              --><router-link
            v-if="section.isViewableOnCoursePage"
            :id="`term-${term.termId}-section-${section.ccn}`"
            :to="`/course/${term.termId}/${section.ccn}?u=${student.uid}`"><span class="sr-only">Link to {{ course.displayName }}, </span>{{ section.displayName }}</router-link><!--
              --><span v-if="!section.isViewableOnCoursePage">{{ section.displayName }}</span><!--
              --><span v-if="sectionIndex < course.sections.length - 1"> | </span><!--
              --><span v-if="sectionIndex === course.sections.length - 1"></span>
          </span>
        </span>
      </div>
      <div>{{ course.title }}</div>
      <div v-if="$currentUser.canAccessCanvasData && !student.fullProfilePending">
        <div
          v-for="(canvasSite, csIndex) in course.canvasSites"
          :key="csIndex"
          class="student-bcourses-wrapper">
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
                  :chart-description="`Boxplot of ${student.name}'s assignments submitted in ${canvasSite.courseCode}`"
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
                  :chart-description="`Boxplot of ${student.name}'s assignment grades in ${canvasSite.courseCode}`"
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
      </div>
    </b-collapse>
  </div>
</template>
<script>
import StudentAnalytics from '@/mixins/StudentAnalytics'
import StudentBoxplot from '@/components/student/StudentBoxplot'
import Util from '@/mixins/Util'

export default {
  name: 'StudentCourse',
  components: {
    StudentBoxplot
  },
  mixins: [StudentAnalytics, Util],
  props: {
    course: {
      required: true,
      type: Object
    },
    index: {
      required: true,
      type: Number
    },
    student: {
      required: true,
      type: Object
    },
    term: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    detailsVisible: false
  }),
}
</script>

<style scoped>
.collapsed > .when-course-open,
.not-collapsed > .when-course-closed {
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
  font-size: 16px;
  margin: 15px 0 5px 0;
  font-weight: 400;
}
.student-bcourses-summary {
  width: 12em;
}
.student-bcourses-wrapper {
  margin-top: 15px;
}
.student-course {
  position: relative
}
.student-course-collapse-button {
  color: #337ab7;
  font-weight: bold;
  height: 15px;
  line-height: 1;
  padding: 0;
}
.student-course-collapse-icon {
  width: 15px;
}
.student-course-details {
  background-color: #f3fbff;
  border: 1px #ccc solid;
  border-top: none;
  padding: 10px 10px 0 30px;
  position: relative;
  top: -10px;
  width: 100%;
  z-index: 1;
}
.student-course-expanded {
  background-color: #f3fbff;
  border: 1px #ccc solid;
}
.student-course-name {
  color: #666;
  font-size: 16px;
  font-weight: 700;
  margin: 5px 0 0;
}
.student-course-row {
  display: flex;
  flex-direction: row;
  line-height: 1.1;
  padding: 8px 10px;
  width: 100%;
}
.student-course-sections {
  display: inline-block;
  font-size: 14px;
  font-weight: 400;
  white-space: nowrap;
}
</style>
