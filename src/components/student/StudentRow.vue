<template>
  <div
    class="d-flex flex-wrap"
    @focusin="hover = true"
    @focusout="hover = false"
    @mouseover="hover = true"
    @mouseleave="hover = false"
  >
    <span :id="`row-index-of-${student.sid}`" hidden aria-hidden="true">{{ rowIndex }}</span>
    <span :id="`student-sid-of-row-${rowIndex}`" hidden aria-hidden="true">{{ student.sid }}</span>
    <div class="align-items-center d-flex">
      <div v-if="listType === 'curatedGroupForOwner'">
        <button
          :id="`row-${rowIndex}-remove-student-from-curated-group`"
          class="btn btn-link pl-0"
          @click="onClickRemoveStudent(student)"
          @keyup.enter="onClickRemoveStudent(student)"
        >
          <font-awesome icon="times-circle" class="font-size-24" />
          <span class="sr-only">Remove {{ student.firstName }} {{ student.lastName }}</span>
        </button>
      </div>
      <div>
        <div class="align-items-center d-flex">
          <div v-if="listType === 'cohort'" class="mr-2">
            <CuratedStudentCheckbox domain="default" :student="student" />
          </div>
          <div>
            <StudentAvatar
              :alert-count="student.alertCount"
              size="medium"
              :student="student"
            />
          </div>
        </div>
        <div v-if="listType === 'cohort'" class="float-right manage-curated-student mb-1">
          <ManageStudent
            domain="default"
            :is-button-variant-link="true"
            :sr-only="!hover"
            :student="student"
          />
        </div>
      </div>
    </div>
    <div class="cohort-student-bio-container mb-1">
      <div class="cohort-student-name-container">
        <div>
          <router-link
            v-if="student.uid"
            :id="`link-to-student-${student.uid}`"
            :to="studentRoutePath(student.uid, $currentUser.inDemoMode)"
          >
            <h3
              v-if="sortedBy !== 'first_name'"
              :id="`row-${rowIndex}-student-name`"
              :class="{'demo-mode-blur': $currentUser.inDemoMode}"
              class="student-name"
              v-html="lastNameFirst(student)"
            />
            <h3
              v-if="sortedBy === 'first_name'"
              :id="`row-${rowIndex}-student-name`"
              :class="{'demo-mode-blur': $currentUser.inDemoMode}"
              class="student-name"
            >
              {{ student.firstName }} {{ student.lastName }}
            </h3>
          </router-link>
          <span v-if="!student.uid">
            <span
              v-if="sortedBy === 'first_name'"
              :id="`student-${student.sid}-has-no-uid`"
              class="font-weight-500 student-name"
              :class="{'demo-mode-blur': $currentUser.inDemoMode}"
              v-html="lastNameFirst(student)"
            />
            <span
              v-if="sortedBy !== 'first_name'"
              :id="`student-${student.sid}-has-no-uid`"
              class="font-size-16 m-0"
              :class="{'demo-mode-blur': $currentUser.inDemoMode}"
            >
              {{ student.firstName }} {{ student.lastName }}
            </span>
          </span>
        </div>
      </div>
      <div :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="d-flex student-sid">
        <div :id="`row-${rowIndex}-student-sid`">{{ student.sid }}</div>
        <div
          v-if="student.academicCareerStatus === 'Inactive'"
          :id="`row-${rowIndex}-inactive`"
          class="red-flag-status ml-1"
        >
          INACTIVE
        </div>
        <div
          v-if="student.academicCareerStatus === 'Completed'"
          class="ml-1"
          uib-tooltip="Graduated"
          tooltip-placement="bottom"
        >
          <font-awesome icon="graduation-cap" />
        </div>
      </div>
      <div
        v-if="displayAsAscInactive(student)"
        :id="`row-${rowIndex}-inactive-asc`"
        class="d-flex student-sid red-flag-status"
      >
        ASC INACTIVE
      </div>
      <div
        v-if="displayAsCoeInactive(student)"
        :id="`row-${rowIndex}-inactive-coe`"
        class="d-flex student-sid red-flag-status"
      >
        CoE INACTIVE
      </div>
      <div v-if="student.withdrawalCancel" :id="`row-${rowIndex}-withdrawal-cancel`">
        <span class="red-flag-small">
          {{ student.withdrawalCancel.description }} {{ student.withdrawalCancel.date | moment('MMM DD, YYYY') }}
        </span>
      </div>
      <StudentAcademicStanding v-if="student.academicStanding" :standing="student.academicStanding" :row-index="`row-${rowIndex}`" />
      <div v-if="student.academicCareerStatus !== 'Completed'">
        <div
          :id="`row-${rowIndex}-student-level`"
          class="student-text"
        >
          {{ student.level }}
        </div>
        <div
          v-if="student.matriculation"
          :id="`row-${rowIndex}-student-matriculation`"
          class="student-text"
          aria-label="Entering term"
        >
          Entered {{ student.matriculation }}
        </div>
        <div
          v-if="student.expectedGraduationTerm"
          :id="`row-${rowIndex}-student-grad-term`"
          class="student-text"
          aria-label="Expected graduation term"
        >
          Grad:&nbsp;{{ student.expectedGraduationTerm.name }}
        </div>
        <div
          v-if="student.termsInAttendance"
          :id="`row-${rowIndex}-student-terms-in-attendance`"
          class="student-text"
          aria-label="Terms in attendance"
        >
          Terms in Attendance:&nbsp;{{ student.termsInAttendance }}
        </div>
        <div
          v-for="(major, index) in student.majors"
          :key="index"
          class="student-text"
        >
          <span :id="`row-${rowIndex}-student-major-${index}`">{{ major }}</span>
        </div>
      </div>
      <div v-if="student.academicCareerStatus === 'Completed'">
        <div
          v-if="student.matriculation"
          :id="`row-${rowIndex}-student-matriculation`"
          class="student-text"
          aria-label="Entering term"
        >
          Entered {{ student.matriculation }}
        </div>
        <DegreesAwarded :student="student" />
        <div v-for="owner in degreePlanOwners" :key="owner" class="student-text">
          <span class="student-text">{{ owner }}</span>
        </div>
      </div>
      <div v-if="student.athleticsProfile" class="student-teams-container">
        <div
          v-for="(team, index) in student.athleticsProfile.athletics"
          :key="index"
          class="student-text"
        >
          <span :id="`row-${rowIndex}-student-team-${index}`">{{ team.groupName }}</span>
        </div>
      </div>
    </div>
    <div class="student-column student-column-gpa">
      <div>
        <span
          v-if="$_.isNil(student.cumulativeGPA)"
          :id="`row-${rowIndex}-student-cumulative-gpa`"
          class="student-gpa"
        >--<span class="sr-only">No data</span></span>
        <span
          v-if="!$_.isNil(student.cumulativeGPA)"
          :id="`row-${rowIndex}-student-cumulative-gpa`"
          class="student-gpa"
        >{{ round(student.cumulativeGPA, 3) }}</span>
        <span class="student-text"> GPA (Cumulative)</span>
      </div>
      <StudentGpaChart
        v-if="$_.size(student.termGpa) > 1"
        :chart-description="`Chart of GPA over time. ${student.name}'s cumulative GPA is ${round(student.cumulativeGPA, 3)}`"
        :student="student"
        :width="130"
      />
      <div
        v-if="$_.size(student.termGpa)"
        class="student-bio-status-legend profile-last-term-gpa-outer pl-0"
      >
        <font-awesome
          v-if="student.termGpa[0].gpa < 2"
          icon="exclamation-triangle"
          class="boac-exclamation mr-1"
        />
        <span :id="`row-${rowIndex}-student-gpa-term-name`">{{ student.termGpa[0].termName }}</span> GPA:
        <strong
          :id="`row-${rowIndex}-student-term-gpa`"
          :class="student.termGpa[0].gpa >= 2 ? 'profile-last-term-gpa' : 'profile-gpa-alert'"
        >{{ round(student.termGpa[0].gpa, 3) }}</strong>
      </div>
    </div>
    <div class="student-column">
      <div class="d-flex flex-wrap">
        <div :id="`row-${rowIndex}-student-enrolled-units`" class="mr-1 student-gpa">{{ $_.get(student.term, 'enrolledUnits', 0) }}</div>
        <div class="student-text">{{ isCurrentTerm ? 'Units in Progress' : 'Units Enrolled' }}</div>
      </div>
      <div
        v-if="!$_.isNil($_.get(student.term, 'minTermUnitsAllowed')) && student.term.minTermUnitsAllowed !== $config.defaultTermUnitsAllowed.min"
        class="d-flex flex-wrap"
      >
        <div :id="`row-${rowIndex}-student-min-units`" class="mr-1 student-gpa">{{ student.term.minTermUnitsAllowed }}</div>
        <div class="no-wrap student-text">Min&nbsp;Approved</div>
      </div>
      <div v-if="!$_.isNil($_.get(student.term, 'maxTermUnitsAllowed')) && student.term.maxTermUnitsAllowed !== $config.defaultTermUnitsAllowed.max">
        <span :id="`row-${rowIndex}-student-max-units`" class="mr-1 student-gpa">{{ student.term.maxTermUnitsAllowed }}</span>
        <span class="no-wrap student-text">Max&nbsp;Approved</span>
      </div>
      <div v-if="isCurrentTerm" class="d-flex flex-wrap">
        <div
          v-if="!$_.isUndefined(student.cumulativeUnits)"
          :id="`row-${rowIndex}-student-cumulative-units`"
          class="mr-1 student-gpa"
        >
          {{ student.cumulativeUnits }}
        </div>
        <div
          v-if="$_.isUndefined(student.cumulativeUnits)"
          :id="`row-${rowIndex}-student-cumulative-units`"
          class="student-gpa"
        >
          &mdash;<span class="sr-only"> No data</span>
        </div>
        <div class="no-wrap student-text">Units Completed</div>
      </div>
    </div>
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
            <font-awesome
              v-if="getSectionsWithIncompleteStatus(enrollment).length"
              :id="`term-${termId}-course-${index}-has-incomplete-status`"
              :aria-label="getIncompleteGradeDescription(enrollment.displayName, getSectionsWithIncompleteStatus(enrollment))"
              class="has-error ml-1"
              icon="info-circle"
              :title="getIncompleteGradeDescription(enrollment.displayName, getSectionsWithIncompleteStatus(enrollment))"
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
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import DegreesAwarded from '@/components/student/DegreesAwarded'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import StudentAcademicStanding from '@/components/student/profile/StudentAcademicStanding'
import StudentAnalytics from '@/mixins/StudentAnalytics'
import StudentAvatar from '@/components/student/StudentAvatar'
import StudentGpaChart from '@/components/student/StudentGpaChart'
import StudentMetadata from '@/mixins/StudentMetadata'
import Util from '@/mixins/Util'

export default {
  name: 'StudentRow',
  components: {
    CuratedStudentCheckbox,
    DegreesAwarded,
    ManageStudent,
    StudentAcademicStanding,
    StudentAvatar,
    StudentGpaChart
  },
  mixins: [
    Berkeley,
    Context,
    StudentAnalytics,
    StudentMetadata,
    Util
  ],
  props: {
    listType: {
      required: true,
      type: String
    },
    removeStudent: {
      required: false,
      default: () => {},
      type: Function
    },
    rowIndex: {
      required: true,
      type: Number
    },
    sortedBy: {
      required: true,
      type: String
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
    hover: false,
    termEnrollments: []
  }),
  computed: {
    degreePlanOwners() {
      const plans = this.$_.get(this.student, 'degree.plans')
      if (plans) {
        return this.$_.uniq(this.$_.map(plans, 'group'))
      } else {
        return []
      }
    },
    isCurrentTerm() {
      return this.termId === `${this.$config.currentEnrollmentTermId}`
    }
  },
  created() {
    const termEnrollments = this.$_.get(this.student.term, 'enrollments', [])
    this.$_.each(termEnrollments, this.setWaitlistedStatus)
    this.termEnrollments = termEnrollments
  },
  methods: {
    getSectionsWithIncompleteStatus(course) {
      return this.$_.filter(course.sections, 'incompleteStatusCode')
    },
    onClickRemoveStudent(student) {
      this.removeStudent(student.sid)
      this.$announcer.polite(`Removed ${student.firstName} ${student.lastName} from group`)
    }
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
.cohort-student-bio-container {
  flex: 0.8;
  margin-left: 20px;
  min-width: 200px;
}
.cohort-student-name-container {
  display: flex;
}
.cohort-student-name-container div:first-child {
  flex-basis: 70%;
}
.manage-curated-student {
  height: 24px;
  margin-right: 18px;
  width: 92px;
}
.profile-gpa-alert {
  color: #d0021b;
}
.profile-last-term-gpa {
  color: #000;
}
.profile-last-term-gpa-outer {
  font-size: 12px;
  padding-left: 5px;
  text-align: left;
}
.student-bio-status-legend {
  color: #999;
  font-size: 13px;
  font-weight: 300;
  text-transform: uppercase;
}
.student-column-gpa {
  flex: 0.5 0 130px;
  margin-left: 15px;
}
.student-gpa {
  font-size: 13px;
  font-weight: bold;
}
</style>

<style>
.cohort-boxplot-container .highcharts-tooltip {
  background-color: #000;
  border-color: #000;
  border-radius: 6px;
  padding: 8px;
  width: 250px;
}
.cohort-boxplot-container g.highcharts-tooltip {
  display: none !important;
}
.cohort-boxplot-container .highcharts-tooltip span {
  position: relative !important;
  top: 0 !important;
  left: 0 !important;
  width: auto !important;
}
</style>
