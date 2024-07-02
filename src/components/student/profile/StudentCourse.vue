<template>
  <div class="student-course" :class="{'student-course-expanded': detailsVisible}">
    <div
      :id="`term-${termId}-course-${index}`"
      role="row"
      class="student-course-row"
    >
      <div role="cell" class="student-course-column-name overflow-hidden">
        <v-btn
          :id="`term-${termId}-course-${index}-toggle`"
          :aria-expanded="detailsVisible ? 'true' : 'false'"
          :aria-controls="`term-${termId}-course-${index}-details`"
          class="align-center d-flex pl-0"
          color="primary"
          density="compact"
          variant="text"
          @click="() => detailsVisible = !detailsVisible"
        >
          <v-icon :icon="detailsVisible ? mdiMenuDown : mdiMenuRight" />
          <span class="sr-only">{{ detailsVisible ? 'Hide' : 'Show' }} {{ course.displayName }} class details for {{ student.name }}</span>
          <div
            :id="`term-${termId}-course-${index}-name`"
            class="text-left truncate-with-ellipsis student-course-name"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
          >
            {{ course.displayName }}
          </div>
        </v-btn>
        <div
          v-if="course.waitlisted"
          :id="`waitlisted-for-${termId}-${course.sections.length ? course.sections[0].ccn : course.displayName}`"
          class="ml-4 red-flag-status student-course-waitlisted text-uppercase"
          :class="{'my-2 position-absolute': detailsVisible}"
        >
          Waitlisted
        </div>
      </div>
      <div role="cell" class="align-center d-flex pl-1 student-course-column-grade text-nowrap">
        <span
          v-if="course.midtermGrade"
          :id="`term-${termId}-course-${index}-midterm-grade`"
          v-accessible-grade="course.midtermGrade"
        />
        <span
          v-if="!course.midtermGrade"
          :id="`term-${termId}-course-${index}-midterm-grade`"
        ><span class="sr-only">No data</span>&mdash;</span>
        <v-icon
          v-if="isAlertGrade(course.midtermGrade) && !course.grade"
          :id="`term-${termId}-course-${index}-has-midterm-grade-alert`"
          :icon="mdiAlertRhombus"
          class="boac-exclamation"
        />
      </div>
      <div role="cell" class="align-center d-flex student-course-column-grade text-nowrap">
        <span
          v-if="course.grade"
          :id="`term-${termId}-course-${index}-final-grade`"
          v-accessible-grade="course.grade"
        />
        <span
          v-if="!course.grade"
          :id="`term-${termId}-course-${index}-final-grade`"
          class="font-italic text-muted"
        >{{ course.gradingBasis }}</span>
        <v-icon
          v-if="isAlertGrade(course.grade)"
          :id="`term-${termId}-course-${index}-has-grade-alert`"
          class="boac-exclamation ml-1"
          color="warning"
          :icon="mdiAlert"
        />
        <IncompleteGradeAlertIcon
          v-if="sectionsWithIncompleteStatus.length"
          :course="course"
          :index="index"
          :term-id="termId"
        />
        <span v-if="!course.grade && !course.gradingBasis" :id="`term-${termId}-course-${index}-final-grade`"><span class="sr-only">No data</span>&mdash;</span>
      </div>
      <div role="cell" class="student-course-column-units font-size-14 text-nowrap pt-1 pl-1">
        <span :id="`term-${termId}-course-${index}-units`">{{ numFormat(course.units, '0.0') }}</span>
      </div>
    </div>
    <transition
      :id="`term-${termId}-course-${index}-details`"
      role="row"
      @before-enter="onShow"
    >
      <div v-if="detailsVisible">
        <div
          :id="`term-${termId}-course-${index}-details-name`"
          class="student-course-details-name"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
        >
          {{ course.displayName }}
        </div>
        <div class="student-course-sections">
          <span
            v-for="(section, sectionIndex) in course.sections"
            :key="sectionIndex"
          >
            <span v-if="section.displayName" :class="{'demo-mode-blur': currentUser.inDemoMode}">
              <span v-if="sectionIndex === 0"></span><!--
                --><router-link
                v-if="section.isViewableOnCoursePage"
                :id="`term-${termId}-section-${section.ccn}`"
                :to="`/course/${termId}/${section.ccn}?u=${student.uid}`"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
              ><span class="sr-only">Link to {{ course.displayName }}, </span>{{ section.displayName }}</router-link><!--
                --><span v-if="!section.isViewableOnCoursePage">{{ section.displayName }}</span><!--
                --><span v-if="sectionIndex < course.sections.length - 1"> | </span><!--
                --><span v-if="sectionIndex === course.sections.length - 1"></span>
            </span>
          </span>
        </div>
        <div :id="`term-${termId}-course-${index}-title`" :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ course.title }}</div>
        <div v-if="course.courseRequirements">
          <div v-for="requirement in course.courseRequirements" :key="requirement" class="student-course-requirements">
            <v-icon class="text-warning" :icon="mdiStar" /> {{ requirement }}
          </div>
        </div>
        <div v-if="currentUser.canAccessCanvasData">
          <div
            v-for="(canvasSite, canvasSiteIdx) in course.canvasSites"
            :key="canvasSiteIdx"
            class="student-bcourses-wrapper"
          >
            <h5
              :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}`"
              class="student-bcourses-site-code"
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
            >
              <span class="sr-only">Course Site</span>
              {{ canvasSite.courseCode }}
            </h5>
            <table class="student-bcourses">
              <tr class="d-flex flex-column d-sm-table-row py-2">
                <th class="student-bcourses-legend" scope="row">
                  Assignments Submitted
                </th>
                <td class="student-bcourses-summary">
                  <span v-if="canvasSite.analytics.assignmentsSubmitted.displayPercentile" :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}-submitted`">
                    <strong>{{ canvasSite.analytics.assignmentsSubmitted.displayPercentile }}</strong> percentile
                  </span>
                  <span
                    v-if="!canvasSite.analytics.assignmentsSubmitted.displayPercentile"
                    :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}-submitted`"
                    class="font-italic text-muted"
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
                  <div v-if="!canvasSite.analytics.assignmentsSubmitted.boxPlottable" :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}-assignments-score`">
                    <span v-if="canvasSite.analytics.assignmentsSubmitted.courseDeciles">
                      Score:
                      <strong>{{ canvasSite.analytics.assignmentsSubmitted.student.raw }}</strong>
                      <span class="text-muted text-nowrap">
                        (Maximum: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[10] }})
                      </span>
                    </span>
                    <span
                      v-if="!canvasSite.analytics.assignmentsSubmitted.courseDeciles"
                      class="font-italic text-muted"
                    >
                      No Data
                    </span>
                  </div>
                </td>
              </tr>
              <tr class="d-flex flex-column d-sm-table-row py-2">
                <th class="student-bcourses-legend" scope="row">
                  Assignment Grades
                </th>
                <td class="student-bcourses-summary">
                  <span v-if="canvasSite.analytics.currentScore.displayPercentile" :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}-grades`">
                    <strong>{{ canvasSite.analytics.currentScore.displayPercentile }}</strong> percentile
                  </span>
                  <span
                    v-if="!canvasSite.analytics.currentScore.displayPercentile"
                    :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}-grades`"
                    class="font-italic text-muted"
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
                  <div v-if="!canvasSite.analytics.currentScore.boxPlottable" :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}-grades-score`">
                    <span v-if="canvasSite.analytics.currentScore.courseDeciles">
                      Score:
                      <strong>{{ canvasSite.analytics.currentScore.student.raw }}</strong>
                      <span class="text-muted text-nowrap">
                        (Maximum: {{ canvasSite.analytics.currentScore.courseDeciles[10] }})
                      </span>
                    </span>
                    <span
                      v-if="!canvasSite.analytics.currentScore.courseDeciles"
                      class="font-italic text-muted text-nowrap"
                    >
                      No Data
                    </span>
                  </div>
                </td>
              </tr>
              <tr v-if="config.currentEnrollmentTermId === parseInt(termId, 10)" class="d-flex flex-column d-sm-table-row py-2">
                <th class="student-bcourses-legend" scope="row">
                  Last bCourses Activity
                </th>
                <td colspan="2">
                  <div v-if="!canvasSite.analytics.lastActivity.student.raw" :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}-activity`">
                    <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</span> has never visited this course site.
                  </div>
                  <div v-if="canvasSite.analytics.lastActivity.student.raw" :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}-activity`">
                    <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</span>
                    last visited the course site {{ lastActivityDays(canvasSite.analytics).toLowerCase() }}.
                    {{ lastActivityInContext(canvasSite.analytics) }}
                  </div>
                </td>
              </tr>
            </table>
          </div>
          <div v-if="isEmpty(course.canvasSites)" :id="`term-${termId}-course-${index}-no-sites`" class="font-italic text-muted">
            No additional information
          </div>
        </div>
        <div
          v-for="section in sectionsWithIncompleteStatus"
          :key="section.ccn"
          class="align-items-center d-flex pb-2"
        >
          <div class="align-center bg-danger d-flex mr-2 pill-alerts px-2 text-uppercase text-nowrap">
            <v-icon class="mr-1" :icon="mdiInformationSlabBox" />
            <span class="font-size-12">Incomplete Grade</span>
          </div>
          <div :id="`term-${termId}-section-${section.ccn}-has-incomplete-grade`" class="font-size-14">
            {{ sectionsWithIncompleteStatus.length > 1 ? `${section.displayName} :` : '' }}
            {{ getIncompleteGradeDescription(course.displayName, [section]) }}
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import IncompleteGradeAlertIcon from '@/components/student/IncompleteGradeAlertIcon'
import StudentBoxplot from '@/components/student/StudentBoxplot'
import {
  getIncompleteGradeDescription,
  getSectionsWithIncompleteStatus,
  isAlertGrade,
  lastActivityDays
} from '@/berkeley'
import {mdiAlert, mdiAlertRhombus, mdiInformationSlabBox, mdiMenuDown, mdiMenuRight, mdiStar} from '@mdi/js'
import {numFormat} from '@/lib/utils'
import {onMounted, onUnmounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {isEmpty} from 'lodash'

const contextStore = useContextStore()
const config = contextStore.config
const currentUser = contextStore.currentUser

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
  termId: {
    required: true,
    type: String
  },
  year: {
    required: true,
    type: String
  }
})
const detailsVisible = ref(false)
const eventWhenShow = `show-student-${props.student.uid}-course`
const sectionsWithIncompleteStatus = ref(getSectionsWithIncompleteStatus(props.course.sections))

onMounted(() => {
  contextStore.setEventHandler(eventWhenShow, ({index, termId}) => detailsVisible.value = index === props.index && termId === props.termId)
})

onUnmounted(() => {
  contextStore.removeEventHandler(eventWhenShow)
})

const lastActivityInContext = analytics => {
  let describe = ''
  if (analytics.courseEnrollmentCount) {
    const total = analytics.courseEnrollmentCount
    const percentAbove = (100 - analytics.lastActivity.student.roundedUpPercentile) / 100
    describe += `${Math.round(percentAbove * total)} out of ${total} enrolled students have done so more recently.`
  }
  return describe
}

const onShow = () => {
  contextStore.broadcast(eventWhenShow, {index: props.index, termId: props.termId})
}
</script>

<style scoped>
.profile-boxplot-container {
  min-width: 13em;
}
.student-bcourses {
  line-height: 1.1;
  margin-bottom: 10px;
  max-width: 35em;
  width: 100%;
}
.student-bcourses td,
.student-bcourses th {
  font-size: 14px;
  padding: 0 10px 7px 0;
  text-align: left;
  vertical-align: top;
}
.student-bcourses-legend {
  color: #666;
  font-weight: normal;
  min-width: 11em;
  white-space: nowrap;
  width: 35%;
}
.student-bcourses-site-code {
  font-size: 16px;
  margin: 15px 0 7px 0;
  font-weight: 400;
}
.student-bcourses-summary {
  min-width: 8.5em;
  width: 30%;
}
.student-bcourses-wrapper {
  margin-top: 15px;
}
.student-course {
  display: flex;
  flex-direction: column;
  padding: 3px 10px 0 !important;
  position: relative
}
.student-course-column-grade {
  width: 15%;
}
.student-course-column-name {
  width: 60%;
}
.student-course-column-units {
  text-align: right;
  width: 15%;
}
.student-course-details {
  align-self: center;
  background-color: #f3fbff;
  padding: 10px 0 10px 20px;
  position: relative;
  top: -1px;
  width: 100%;
  z-index: 1;
}
.student-course-details-name {
  color: #666;
  font-size: 16px;
  font-weight: 700;
  margin: 5px 0 0;
}
.student-course-expanded {
  background-color: #f3fbff;
  border: 1px #ccc solid;
}
.student-course-expanded .student-course-row {
  background-color: #f3fbff;
  z-index: 2;
}
.student-course-name {
  height: 1.1em;
  line-height: 1.1;
  max-width: 90%;
  overflow: hidden;
}
.student-course-requirements {
  font-size: 14px;
  white-space: nowrap;
}
.student-course-row {
  display: flex;
  flex-direction: row;
  height: 2.2em;
  line-height: 1.1;
  margin: 0 -10px;
  padding: 0 10px 0 4px;
}
.student-course-sections {
  display: inline-block;
  font-size: 14px;
  font-weight: 400;
  white-space: nowrap;
}
.student-course-waitlisted {
  font-size: 14px;
  line-height: .8;
}
.student-term:first-child .student-course-details {
  align-self: flex-start;
}
.student-term:last-child .student-course-details {
  align-self: flex-end;
}
</style>
