<template>
  <div>
    <div v-for="(canvasSite, canvasSiteId) in course.canvasSites" :key="canvasSiteId">
      <table class="bcourses" :class="{'stacked-table': $vuetify.display.width <= mobileBreakpoint}">
        <caption
          :id="`term-${termId}-course-${index}-site-${canvasSiteId}`"
          class="text-left bcourses-site-code"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
        >
          <span class="sr-only">Course Site</span>
          {{ canvasSite.courseCode }}
        </caption>
        <tbody>
          <tr class="py-2 d-block d-sm-table-row">
            <th class="bcourses-legend text-no-wrap" scope="row">
              Assignments Submitted
            </th>
            <td class="bcourses-summary d-flex d-sm-table-cell py-1 py-sm-0">
              <span v-if="canvasSite.analytics.assignmentsSubmitted.displayPercentile" :id="`term-${termId}-course-${index}-site-${canvasSiteId}-submitted`">
                <strong>{{ canvasSite.analytics.assignmentsSubmitted.displayPercentile }}</strong> percentile
              </span>
              <span
                v-if="!canvasSite.analytics.assignmentsSubmitted.displayPercentile"
                :id="`term-${termId}-course-${index}-site-${canvasSiteId}-submitted`"
                class="font-italic text-medium-emphasis"
              >
                No Assignments
              </span>
            </td>
            <td class="profile-boxplot-container d-flex d-sm-table-cell py-1 py-sm-0">
              <StudentBoxplot
                v-if="canvasSite.analytics.assignmentsSubmitted.boxPlottable"
                :id="`term-${termId}-course-${index}-site-${canvasSiteId}-submitted-boxplot`"
                axis-description="assignments submitted"
                :chart-description="`${student.name}'s assignments submitted in ${canvasSite.courseCode}`"
                :chart-summary="`${student.name} is in the ${canvasSite.analytics.assignmentsSubmitted.displayPercentile} percentile with ${canvasSite.analytics.assignmentsSubmitted.student.raw} assignments submitted.`"
                :dataset="canvasSite.analytics.assignmentsSubmitted"
                :numeric-id="canvasSite.canvasCourseId.toString()"
                :student-name="student.name"
              />
              <div v-if="!canvasSite.analytics.assignmentsSubmitted.boxPlottable" :id="`term-${termId}-course-${index}-site-${canvasSiteId}-assignments-score`">
                <span v-if="canvasSite.analytics.assignmentsSubmitted.courseDeciles">
                  Score:
                  <strong>{{ canvasSite.analytics.assignmentsSubmitted.student.raw }}<span class="sr-only">.</span></strong>
                  <span class="text-medium-emphasis text-no-wrap">
                    (Maximum: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[10] }})
                  </span>
                </span>
                <span
                  v-if="!canvasSite.analytics.assignmentsSubmitted.courseDeciles"
                  class="font-italic text-medium-emphasis"
                >
                  No Data
                </span>
              </div>
            </td>
          </tr>
          <tr class="pt-2 d-block d-sm-table-row">
            <th class="bcourses-legend text-no-wrap" scope="row">
              Assignment Grades
            </th>
            <td class="bcourses-summary d-flex d-sm-table-cell py-1 py-sm-0">
              <span v-if="canvasSite.analytics.currentScore.displayPercentile" :id="`term-${termId}-course-${index}-site-${canvasSiteId}-grades`">
                <strong>{{ canvasSite.analytics.currentScore.displayPercentile }}</strong> percentile
              </span>
              <span
                v-if="!canvasSite.analytics.currentScore.displayPercentile"
                :id="`term-${termId}-course-${index}-site-${canvasSiteId}-grades`"
                class="font-italic text-medium-emphasis"
              >
                No Grades
              </span>
            </td>
            <td class="profile-boxplot-container d-flex d-sm-table-cell py-1 py-sm-0">
              <StudentBoxplot
                v-if="canvasSite.analytics.currentScore.boxPlottable"
                :id="`term-${termId}-course-${index}-site-${canvasSiteId}-grades-boxplot`"
                axis-description="assignment grades"
                :chart-description="`${student.name}'s assignment grades in ${canvasSite.courseCode}`"
                :chart-summary="`${student.name} is in the ${canvasSite.analytics.currentScore.displayPercentile} percentile with a grade of ${canvasSite.analytics.currentScore.student.raw}.`"
                :dataset="canvasSite.analytics.currentScore"
                :numeric-id="canvasSite.canvasCourseId.toString()"
                :student-name="student.name"
              />
              <div v-if="!canvasSite.analytics.currentScore.boxPlottable" :id="`term-${termId}-course-${index}-site-${canvasSiteId}-grades-score`">
                <span v-if="canvasSite.analytics.currentScore.courseDeciles">
                  Score:
                  <strong>{{ canvasSite.analytics.currentScore.student.raw }}</strong>
                  <span class="text-medium-emphasis text-no-wrap">
                    (Maximum: {{ canvasSite.analytics.currentScore.courseDeciles[10] }})
                  </span>
                </span>
                <span
                  v-if="!canvasSite.analytics.currentScore.courseDeciles"
                  class="font-italic text-medium-emphasis text-no-wrap"
                >
                  No Data
                </span>
              </div>
            </td>
          </tr>
          <tr v-if="config.currentEnrollmentTermId === parseInt(termId, 10)" class="d-flex d-sm-table-row flex-column pt-2">
            <th class="bcourses-legend" scope="row">
              Last bCourses Activity
            </th>
            <td colspan="2">
              <div v-if="!canvasSite.analytics.lastActivity.student.raw" :id="`term-${termId}-course-${index}-site-${canvasSiteId}-activity`">
                <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</span> has never visited this course site.
              </div>
              <div v-if="canvasSite.analytics.lastActivity.student.raw" :id="`term-${termId}-course-${index}-site-${canvasSiteId}-activity`">
                <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</span>
                last visited the course site {{ lastActivityDays(canvasSite.analytics).toLowerCase() }}.
                {{ lastActivityInContext(canvasSite.analytics) }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="isEmpty(course.canvasSites)" :id="`term-${termId}-course-${index}-no-sites`" class="font-italic text-medium-emphasis">
      No additional information
    </div>
  </div>
</template>

<script setup lang="ts">
import {isEmpty} from 'lodash'
import {lastActivityDays} from '@/lib/berkeley-utils'
import StudentBoxplot from '@/components/student/StudentBoxplot.vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
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
})

const contextStore = useContextStore()
const config = contextStore.config
const currentUser = contextStore.currentUser
const mobileBreakpoint = 600
const termId = props.term.termId
type Analytics = {
  assignmentsSubmitted: object,
  courseEnrollmentCount: number,
  currentScore: object,
  lastActivity: {
    boxPlottable: boolean,
    courseDeciles: number[],
    courseMean: object,
    displayPercentile: string,
    student: {
      matrixyPercentile: number,
      percentile: number
      raw: number,
      roundedUpPercentile: number
    }
  }
}

const lastActivityInContext = (analytics: Analytics) => {
  let describe = ''
  if (analytics.courseEnrollmentCount) {
    const total = analytics.courseEnrollmentCount
    const percentAbove = (100 - analytics.lastActivity.student.roundedUpPercentile) / 100
    describe += `${Math.round(percentAbove * total)} out of ${total} enrolled students have done so more recently.`
  }
  return describe
}
</script>

<style scoped>
.bcourses {
  background-color: rgb(var(--v-theme-pale-blue));
}
.bcourses td, .bcourses th {
  font-size: 14px;
  padding: 0 10px 0 0;
  text-align: left;
}
.bcourses-legend {
  opacity: var(--v-medium-emphasis-opacity);
  min-width: 11em;
}
.bcourses-site-code {
  font-size: 15px;
  margin: 8px 0 3px 0;
}
.bcourses-summary {
  min-width: 8.5em;
}
.profile-boxplot-container {
  align-content: end;
  min-width: 10em;
}
</style>
