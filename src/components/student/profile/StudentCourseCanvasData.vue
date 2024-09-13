<template>
  <div>
    <div v-for="(canvasSite, canvasSiteId) in course.canvasSites" :key="canvasSiteId">
      <h5
        :id="`term-${termId}-course-${index}-site-${canvasSiteId}`"
        class="bcourses-site-code"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
      >
        <span class="sr-only">Course Site</span>
        {{ canvasSite.courseCode }}
      </h5>
      <table class="bcourses">
        <tbody>
          <tr class="d-sm-table-row py-2">
            <th class="bcourses-legend text-no-wrap" scope="row">
              Assignments Submitted
            </th>
            <td class="bcourses-summary">
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
            <td class="profile-boxplot-container">
              <StudentBoxplot
                v-if="canvasSite.analytics.assignmentsSubmitted.boxPlottable"
                :chart-description="`Boxplot of ${student.name}'s assignments submitted in ${canvasSite.courseCode}`"
                :dataset="canvasSite.analytics.assignmentsSubmitted"
                :numeric-id="canvasSite.canvasCourseId.toString()"
              />
              <div v-if="canvasSite.analytics.assignmentsSubmitted.boxPlottable" class="sr-only">
                <div>User score: {{ canvasSite.analytics.assignmentsSubmitted.student.raw }}</div>
                <div>Maximum: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[10] }}</div>
                <div>70th Percentile: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[7] }}</div>
                <div>50th Percentile: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[5] }}</div>
                <div>30th Percentile: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[3] }}</div>
                <div>Minimum: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[0] }}</div>
              </div>
              <div v-if="!canvasSite.analytics.assignmentsSubmitted.boxPlottable" :id="`term-${termId}-course-${index}-site-${canvasSiteId}-assignments-score`">
                <span v-if="canvasSite.analytics.assignmentsSubmitted.courseDeciles">
                  Score:
                  <strong>{{ canvasSite.analytics.assignmentsSubmitted.student.raw }}</strong>
                  <span class="text-medium-emphasis text-nowrap">
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
          <tr class="d-flex d-sm-table-row flex-column pt-2">
            <th class="bcourses-legend" scope="row">
              Assignment Grades
            </th>
            <td class="bcourses-summary">
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
            <td class="profile-boxplot-container">
              <StudentBoxplot
                v-if="canvasSite.analytics.currentScore.boxPlottable"
                :chart-description="`Boxplot of ${student.name}'s assignment grades in ${canvasSite.courseCode}`"
                :dataset="canvasSite.analytics.currentScore"
                :numeric-id="canvasSite.canvasCourseId.toString()"
              />
              <div v-if="canvasSite.analytics.currentScore.boxPlottable" class="sr-only">
                <div>User score: {{ canvasSite.analytics.currentScore.student.raw }}</div>
                <div>Maximum: {{ canvasSite.analytics.currentScore.courseDeciles[10] }}</div>
                <div>70th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[7] }}</div>
                <div>50th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[5] }}</div>
                <div>30th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[3] }}</div>
                <div>Minimum: {{ canvasSite.analytics.currentScore.courseDeciles[0] }}</div>
              </div>
              <div v-if="!canvasSite.analytics.currentScore.boxPlottable" :id="`term-${termId}-course-${index}-site-${canvasSiteId}-grades-score`">
                <span v-if="canvasSite.analytics.currentScore.courseDeciles">
                  Score:
                  <strong>{{ canvasSite.analytics.currentScore.student.raw }}</strong>
                  <span class="text-medium-emphasis text-nowrap">
                    (Maximum: {{ canvasSite.analytics.currentScore.courseDeciles[10] }})
                  </span>
                </span>
                <span
                  v-if="!canvasSite.analytics.currentScore.courseDeciles"
                  class="font-italic text-medium-emphasis text-nowrap"
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
import {lastActivityDays} from '@/berkeley'
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
const termId = props.term.termId

const lastActivityInContext = (analytics: any) => {
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
.bcourses td,
.bcourses th {
  font-size: 14px;
  padding: 0 10px 0 0;
  text-align: left;
  vertical-align: top;
}
.bcourses-legend {
  color: #666;
  min-width: 11em;
  width: 35%;
}
.bcourses-site-code {
  font-size: 15px;
  margin: 8px 0 3px 0;
  font-weight: 450;
}
.bcourses-summary {
  min-width: 8.5em;
  width: 30%;
}
.profile-boxplot-container {
  min-width: 13em;
}
</style>
