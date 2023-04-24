<template>
  <div class="cohort-course-activity-wrapper">
    <table class="cohort-course-activity-table">
      <tr>
        <th class="cohort-course-activity-header cohort-course-activity-course-name">CLASS</th>
        <th v-if="$currentUser.canAccessCanvasData" class="cohort-course-activity-header">
          <span aria-hidden="true" class="text-uppercase">bCourses Activity</span>
          <span class="sr-only">Most recent B Courses activity</span>
        </th>
        <th class="cohort-course-activity-header">
          <span aria-hidden="true" class="text-uppercase">Mid</span>
          <span class="sr-only">Midpoint grade</span>
        </th>
        <th class="cohort-course-activity-header">
          <span class="text-uppercase">Final<span class="sr-only"> grade</span></span>
        </th>
      </tr>
      <tr v-for="(enrollment, index) in termEnrollments" :key="index">
        <td class="cohort-course-activity-data cohort-course-activity-course-name">
          <span :id="`row-${rowIndex}-student-enrollment-name-${index}`">{{ enrollment.displayName }}</span>
          <span
            v-if="enrollment.waitlisted"
            :id="`student-${student.uid}-waitlisted-for-${enrollment.sections.length ? enrollment.sections[0].ccn : enrollment.displayName}`"
            aria-hidden="true"
            class="pl-1 red-flag-status"
          >(W)</span>
          <span v-if="enrollment.waitlisted" class="sr-only">
            Waitlisted
          </span>
        </td>
        <td v-if="$currentUser.canAccessCanvasData" class="cohort-course-activity-data">
          <div
            v-for="(canvasSite, cIndex) in enrollment.canvasSites"
            :key="cIndex"
            class="cohort-boxplot-container"
          >
            <span
              v-if="enrollment.canvasSites.length > 1"
              class="sr-only"
            >
              {{ `Course site ${cIndex + 1} of ${enrollment.canvasSites.length}` }}
            </span>
            {{ lastActivityDays(canvasSite.analytics) }}
          </div>
          <div v-if="!$_.get(enrollment, 'canvasSites').length">
            <span class="sr-only">No data </span>&mdash;
          </div>
        </td>
        <td class="cohort-course-activity-data">
          <span v-if="enrollment.midtermGrade" v-accessible-grade="enrollment.midtermGrade" class="font-weight-bold"></span>
          <font-awesome v-if="isAlertGrade(enrollment.midtermGrade)" icon="exclamation-triangle" class="boac-exclamation" />
          <span v-if="!enrollment.midtermGrade"><span class="sr-only">No data</span>&mdash;</span>
        </td>
        <td class="cohort-course-activity-data">
          <span
            v-if="enrollment.grade"
            v-accessible-grade="enrollment.grade"
            class="font-weight-bold"
          ></span>
          <font-awesome
            v-if="isAlertGrade(enrollment.grade)"
            icon="exclamation-triangle"
            class="boac-exclamation ml-1"
          />
          <IncompleteGradeAlertIcon
            v-if="getSectionsWithIncompleteStatus(enrollment.sections).length"
            :course="enrollment"
            :index="index"
            :term-id="termId"
          />
          <span
            v-if="!enrollment.grade"
            class="cohort-grading-basis"
          >{{ enrollment.gradingBasis }}</span>
          <span v-if="!enrollment.grade && !enrollment.gradingBasis"><span class="sr-only">No data</span>&mdash;</span>
        </td>
      </tr>
      <tr v-if="!termEnrollments.length">
        <td class="cohort-course-activity-data cohort-course-activity-course-name faint-text">
          No {{ termNameForSisId(termId) }} enrollments
        </td>
        <td v-if="$currentUser.canAccessCanvasData" class="cohort-course-activity-data">
          <span class="sr-only">No data</span>&mdash;
        </td>
        <td class="cohort-course-activity-data">
          <span class="sr-only">No data</span>&mdash;
        </td>
        <td class="cohort-course-activity-data">
          <span class="sr-only">No data</span>&mdash;
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley'
import IncompleteGradeAlertIcon from '@/components/student/IncompleteGradeAlertIcon'
import StudentAnalytics from '@/mixins/StudentAnalytics'
import StudentMetadata from '@/mixins/StudentMetadata'

export default {
  name: 'StudentRowCourseActivity',
  mixins: [Berkeley, StudentAnalytics, StudentMetadata],
  components: {IncompleteGradeAlertIcon},
  props: {
    rowIndex: {
      required: true,
      type: Number
    },
    student: {
      required: true,
      type: Object
    },
    termId: {
      required: true,
      type: String
    }
  },
  data: () => ({
    termEnrollments: []
  }),
  created() {
    const termEnrollments = this.$_.get(this.student.term, 'enrollments', [])
    this.$_.each(termEnrollments, this.setWaitlistedStatus)
    this.termEnrollments = termEnrollments
  }
}
</script>

<style scoped>
.cohort-boxplot-container {
  align-items: flex-end;
  display: flex;
}
.cohort-course-activity-course-name {
  width: 180px;
}
.cohort-course-activity-data {
  font-size: 14px;
  line-height: 1.4em;
  padding: 0 0 5px 15px;
  vertical-align: top;
}
.cohort-course-activity-header {
  color: #aaa;
  font-size: 13px;
  font-weight: normal;
  padding: 0 0 5px 15px;
  vertical-align: top;
}
.cohort-course-activity-table {
  margin: auto;
  min-width: 340px;
  width: 85%;
}
.cohort-course-activity-wrapper {
  flex-basis: auto;
  flex-grow: 0.6;
  margin-left: 0;
  min-width: 340px;
}
</style>
