<template>
  <div class="student-course" :class="{'student-course-expanded': detailsVisible}">
    <div
      :id="`term-${termId}-course-${index}`"
      role="row"
      class="student-course-row"
    >
      <div role="cell" class="student-course-column-name">
        <b-btn
          :id="`term-${termId}-course-${index}-toggle`"
          v-b-toggle="`term-${termId}-course-${index}-details`"
          class="d-flex flex-row-reverse justify-content-between student-course-collapse-button"
          variant="link"
          :aria-expanded="detailsVisible ? 'true' : 'false'"
          :aria-controls="`term-${termId}-course-${index}-details`"
        >
          <span :id="`term-${termId}-course-${index}-name`" class="text-left mx-2">{{ course.displayName }}</span>
          <font-awesome icon="caret-right" class="caret when-course-closed" />
          <span class="when-course-closed sr-only">Show {{ course.displayName }} class details for {{ student.name }}</span>
          <font-awesome icon="caret-down" class="caret when-course-open" />
          <span class="when-course-open sr-only">Hide {{ course.displayName }} class details for {{ student.name }}</span>
        </b-btn>
        <div
          v-if="course.waitlisted"
          :id="`waitlisted-for-${termId}-${course.sections.length ? course.sections[0].ccn : course.displayName}`"
          class="red-flag-status text-uppercase font-size-14 mt-1"
        >
          Waitlisted
        </div>
      </div>
      <div role="cell" class="student-course-column-mid-grade text-nowrap">
        <span
          v-if="course.midtermGrade"
          :id="`term-${termId}-course-${index}-midterm-grade`"
          v-accessible-grade="course.midtermGrade"
        ></span>
        <span
          v-if="!course.midtermGrade"
          :id="`term-${termId}-course-${index}-midterm-grade`"
        ><span class="sr-only">No data</span>&mdash;</span>
      </div>
      <div role="cell" class="student-course-column-final-grade text-nowrap">
        <span
          v-if="course.grade"
          :id="`term-${termId}-course-${index}-final-grade`"
          v-accessible-grade="course.grade"
        ></span>
        <span
          v-if="!course.grade"
          :id="`term-${termId}-course-${index}-final-grade`"
          class="font-italic text-muted"
        >{{ course.gradingBasis }}</span>
        <span v-if="!course.grade && !course.gradingBasis" :id="`term-${termId}-course-${index}-final-grade`"><span class="sr-only">No data</span>&mdash;</span>
      </div>
      <div role="cell" class="student-course-column-units text-nowrap">
        <span :id="`term-${termId}-course-${index}-units`">{{ course.units }}</span>
      </div>
    </div>
    <b-collapse :id="`term-${termId}-course-${index}-spacer`" :visible="showSpacer">
      <div :style="{height: spacerHeight + 'px'}" />
    </b-collapse>
    <b-collapse
      :id="`term-${termId}-course-${index}-details`"
      ref="details"
      role="row"
      class="student-course-details"
      accordion="student-course-detail-accordion"
      @show="onShow"
      @shown="onShown"
      @hide="onHide"
      @hidden="onHidden"
    >
      <div :id="`term-${termId}-course-${index}-details-name`" class="student-course-name">{{ course.displayName }}</div>
      <div class="student-course-sections">
        <span
          v-for="(section, sectionIndex) in course.sections"
          :key="sectionIndex"
        >
          <span v-if="section.displayName">
            <span v-if="sectionIndex === 0"></span><!--
              --><router-link
              v-if="section.isViewableOnCoursePage"
              :id="`term-${termId}-section-${section.ccn}`"
              :to="`/course/${termId}/${section.ccn}?u=${student.uid}`"
            ><span class="sr-only">Link to {{ course.displayName }}, </span>{{ section.displayName }}</router-link><!--
              --><span v-if="!section.isViewableOnCoursePage">{{ section.displayName }}</span><!--
              --><span v-if="sectionIndex < course.sections.length - 1"> | </span><!--
              --><span v-if="sectionIndex === course.sections.length - 1"></span>
          </span>
        </span>
      </div>
      <div :id="`term-${termId}-course-${index}-title`">{{ course.title }}</div>
      <div v-if="$currentUser.canAccessCanvasData && !student.fullProfilePending">
        <div
          v-for="(canvasSite, canvasSiteIdx) in course.canvasSites"
          :key="canvasSiteIdx"
          class="student-bcourses-wrapper"
        >
          <h5 :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}`" class="student-bcourses-site-code">
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
                    <span class="text-muted">
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
                  <span
                    v-if="canvasSite.analytics.currentScore.courseDeciles"
                    class="font-italic text-muted"
                  >
                    Score:
                    <strong>{{ canvasSite.analytics.currentScore.student.raw }}</strong>
                    <span class="text-muted">
                      (Maximum: {{ canvasSite.analytics.currentScore.courseDeciles[10] }})
                    </span>
                  </span>
                  <span
                    v-if="!canvasSite.analytics.currentScore.courseDeciles"
                    class="font-italic text-muted"
                  >
                    No Data
                  </span>
                </div>
              </td>
            </tr>
            <tr v-if="$config.currentEnrollmentTermId === parseInt(termId, 10)">
              <th class="student-bcourses-legend" scope="row">
                Last bCourses Activity
              </th>
              <td colspan="2">
                <div v-if="!canvasSite.analytics.lastActivity.student.raw" :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}-activity`">
                  <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.name }}</span> has never visited this course site.
                </div>
                <div v-if="canvasSite.analytics.lastActivity.student.raw" :id="`term-${termId}-course-${index}-site-${canvasSiteIdx}-activity`">
                  <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.name }}</span>
                  last visited the course site {{ lastActivityDays(canvasSite.analytics).toLowerCase() }}.
                  {{ lastActivityInContext(canvasSite.analytics) }}
                </div>
              </td>
            </tr>
          </table>
        </div>
        <div v-if="$_.isEmpty(course.canvasSites)" :id="`term-${termId}-course-${index}-no-sites`" class="font-italic text-muted">
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
    termId: {
      required: true,
      type: String
    },
    year: {
      required: true,
      type: String
    }
  },
  data: () => ({
    detailsVisible: false,
    spacerHeight: 0
  }),
  mounted() {
    this.$root.$on(`year-${this.year}-course-${this.index}-show`, () => this.spacerHeight = 120)
    this.$root.$on(`year-${this.year}-course-${this.index}-shown`, offsetHeight => this.spacerHeight = offsetHeight)
    this.$root.$on(`year-${this.year}-course-${this.index}-hide`, () => this.spacerHeight = 0)
  },
  beforeDestroy() {
    this.$root.$off(`year-${this.year}-course-${this.index}-show`)
    this.$root.$off(`year-${this.year}-course-${this.index}-shown`)
    this.$root.$off(`year-${this.year}-course-${this.index}-hide`)
  },
  computed: {
    showSpacer: vm => !vm.detailsVisible && !!vm.spacerHeight
  },
  methods: {
    onHide() {
      this.$root.$emit(`year-${this.year}-course-${this.index}-hide`)
    },
    onHidden() {
      this.detailsVisible = false
    },
    onShow() {
      this.$root.$emit(`year-${this.year}-course-${this.index}-show`)
      this.detailsVisible = true
    },
    onShown() {
      this.$root.$emit(`year-${this.year}-course-${this.index}-shown`, this.$refs.details.$el.offsetHeight)
    }
  }
}
</script>

<style scoped>
@media (min-width: 1200px) {
  .student-course-details {
    border: 1px #ccc solid;
    margin: 0 -11px;
    padding: 10px 30px !important;
    width: 316% !important;
  }
  .student-course-expanded {
    border-bottom: 0 !important;
  }
}
.caret {
  width: 10px;
}
.collapsed > .when-course-open,
.not-collapsed > .when-course-closed {
  display: none;
}
.student-bcourses {
  line-height: 1.1;
  margin-bottom: 10px;
}
.student-bcourses td,
.student-bcourses th {
  font-size: 14px;
  padding: 0 25px 5px 0;
  text-align: left;
  vertical-align: top;
}
.student-bcourses-legend {
  color: #666;
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
  display: flex;
  flex-direction: column;
  padding: 0 10px !important;
  position: relative
}
.student-course-collapse-button {
  color: #337ab7;
  font-weight: bold;
  height: 15px;
  line-height: 1;
  padding: 0;
}
.student-course-details {
  align-self: center;
  background-color: #f3fbff;
  padding: 10px 20px;
  position: relative;
  top: -1px;
  width: 100%;
  z-index: 1;
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
  color: #666;
  font-size: 16px;
  font-weight: 700;
  margin: 5px 0 0;
}
.student-course-row {
  display: flex;
  flex-direction: row;
  line-height: 1.1;
  margin: 0 -10px;
  padding: 8px 10px;
}
.student-course-sections {
  display: inline-block;
  font-size: 14px;
  font-weight: 400;
  white-space: nowrap;
}
.student-term:first-child .student-course-details {
  align-self: flex-start;
}
.student-term:last-child .student-course-details {
  align-self: flex-end;
}
</style>
