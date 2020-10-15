<template>
  <div class="d-flex flex-wrap">
    <span :id="`row-index-of-${student.sid}`" hidden aria-hidden="true">{{ rowIndex }}</span>
    <span :id="`student-sid-of-row-${rowIndex}`" hidden aria-hidden="true">{{ student.sid }}</span>
    <div class="cohort-list-view-column-01">
      <button
        v-if="listType === 'curatedGroupForOwner'"
        :id="`row-${rowIndex}-remove-student-from-curated-group`"
        class="btn btn-link"
        :aria-label="`Remove ${student.firstName} ${student.lastName} from group`"
        @click="onClickRemoveStudent(student)"
        @keyup.enter="onClickRemoveStudent(student)">
        <font-awesome icon="times-circle" class="font-size-24" />
      </button>
      <div v-if="listType === 'cohort'">
        <CuratedStudentCheckbox :student="student" />
      </div>
    </div>
    <div class="cohort-list-view-column-01">
      <StudentAvatar
        :student="student"
        :alert-count="student.alertCount"
        size="medium" />
    </div>
    <div class="cohort-student-bio-container mb-1">
      <div class="cohort-student-name-container">
        <div>
          <router-link :id="`link-to-student-${student.uid}`" :to="studentRoutePath(student.uid, $currentUser.inDemoMode)">
            <h3
              v-if="sortedBy !== 'first_name'"
              :id="`row-${rowIndex}-student-name`"
              :class="{'demo-mode-blur': $currentUser.inDemoMode}"
              class="student-name"
              v-html="`${student.lastName}, ${student.firstName}`"></h3>
            <h3
              v-if="sortedBy === 'first_name'"
              :id="`row-${rowIndex}-student-name`"
              :class="{'demo-mode-blur': $currentUser.inDemoMode}"
              class="student-name">
              {{ student.firstName }} {{ student.lastName }}
            </h3>
          </router-link>
        </div>
      </div>
      <div :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="d-flex student-sid">
        <div :id="`row-${rowIndex}-student-sid`">{{ student.sid }}</div>
        <div
          v-if="student.academicCareerStatus === 'Inactive'"
          :id="`row-${rowIndex}-inactive`"
          class="red-flag-status ml-1">
          INACTIVE
        </div>
        <div
          v-if="student.academicCareerStatus === 'Completed'"
          class="ml-1"
          uib-tooltip="Graduated"
          tooltip-placement="bottom">
          <font-awesome icon="graduation-cap" />
        </div>
      </div>
      <div
        v-if="displayAsAscInactive(student)"
        :id="`row-${rowIndex}-inactive-asc`"
        class="d-flex student-sid red-flag-status">
        ASC INACTIVE
      </div>
      <div
        v-if="displayAsCoeInactive(student)"
        :id="`row-${rowIndex}-inactive-coe`"
        class="d-flex student-sid red-flag-status">
        CoE INACTIVE
      </div>
      <div v-if="student.withdrawalCancel" :id="`row-${rowIndex}-withdrawal-cancel`">
        <span class="red-flag-small">
          {{ student.withdrawalCancel.description }} {{ student.withdrawalCancel.date | moment('MMM DD, YYYY') }}
        </span>
      </div>
      <StudentAcademicStanding v-if="student.academicStanding" :standing="student.academicStanding[0]" :row-index="`row-${rowIndex}`" />
      <div v-if="student.academicCareerStatus !== 'Completed'">
        <div
          :id="`row-${rowIndex}-student-level`"
          class="student-text">
          {{ student.level }}
        </div>
        <div
          v-if="student.matriculation"
          :id="`row-${rowIndex}-student-matriculation`"
          class="student-text"
          aria-label="Entering term">
          Entered {{ student.matriculation }}
        </div>
        <div
          v-if="student.expectedGraduationTerm"
          :id="`row-${rowIndex}-student-grad-term`"
          class="student-text"
          aria-label="Expected graduation term">
          Grad:&nbsp;{{ student.expectedGraduationTerm.name }}
        </div>
        <div
          v-if="student.termsInAttendance"
          :id="`row-${rowIndex}-student-terms-in-attendance`"
          class="student-text"
          aria-label="Terms in attendance">
          Terms in Attendance:&nbsp;{{ student.termsInAttendance }}
        </div>
        <div
          v-for="(major, index) in student.majors"
          :key="index"
          class="student-text">
          <span :id="`row-${rowIndex}-student-major-${index}`">{{ major }}</span>
        </div>
      </div>
      <div v-if="student.academicCareerStatus === 'Completed'">
        <div
          v-if="student.matriculation"
          :id="`row-${rowIndex}-student-matriculation`"
          class="student-text"
          aria-label="Entering term">
          Entered {{ student.matriculation }}
        </div>
        <div v-if="get(student, 'degree.dateAwarded')">
          <span class="student-text">Graduated {{ student.degree.dateAwarded | moment('MMM DD, YYYY') }}</span>
        </div>
        <div v-for="owner in degreePlanOwners" :key="owner" class="student-text">
          <span class="student-text">{{ owner }}</span>
        </div>
      </div>
      <div v-if="student.athleticsProfile" class="student-teams-container">
        <div
          v-for="(team, index) in student.athleticsProfile.athletics"
          :key="index"
          class="student-text">
          <span :id="`row-${rowIndex}-student-team-${index}`">{{ team.groupName }}</span>
        </div>
      </div>
    </div>
    <div class="student-column student-column-gpa">
      <div>
        <span
          v-if="isNil(student.cumulativeGPA)"
          :id="`row-${rowIndex}-student-cumulative-gpa`"
          class="student-gpa">--<span class="sr-only">No data</span></span>
        <span
          v-if="!isNil(student.cumulativeGPA)"
          :id="`row-${rowIndex}-student-cumulative-gpa`"
          class="student-gpa">{{ round(student.cumulativeGPA, 3) }}</span>
        <span class="student-text"> GPA (Cumulative)</span>
      </div>
      <StudentGpaChart
        v-if="size(student.termGpa) > 1"
        :student="student"
        :width="'130'" />
      <div
        v-if="size(student.termGpa)"
        class="student-bio-status-legend profile-last-term-gpa-outer pl-0">
        <font-awesome
          v-if="student.termGpa[0].gpa < 2"
          icon="exclamation-triangle"
          class="boac-exclamation mr-1" />
        <span :id="`row-${rowIndex}-student-gpa-term-name`">{{ student.termGpa[0].termName }}</span> GPA:
        <strong
          :id="`row-${rowIndex}-student-term-gpa`"
          :class="student.termGpa[0].gpa >= 2 ? 'profile-last-term-gpa' : 'profile-gpa-alert'">{{ round(student.termGpa[0].gpa, 3) }}</strong>
      </div>
    </div>
    <div class="student-column">
      <div :id="`row-${rowIndex}-student-enrolled-units`" class="student-gpa">{{ get(student.term, 'enrolledUnits', 0) }}</div>
      <div class="student-text">Units in Progress</div>
      <!--
      TODO: Until SISRP-48560 is resolved we will suppress unitsMin and unitsMax data in BOA.
      <div v-if="get(student, 'currentTerm.unitsMin')">
        <div :id="`row-${rowIndex}-student-min-units`" class="student-gpa">{{ student.currentTerm.unitsMin }}</div>
        <div class="student-text">Min&nbsp;Approved</div>
      </div>
      <div v-if="get(student, 'currentTerm.unitsMax')">
        <div :id="`row-${rowIndex}-student-max-units`" class="student-gpa">{{ student.currentTerm.unitsMax }}</div>
        <div class="student-text">Max&nbsp;Approved</div>
      </div>
      -->
      <div
        v-if="student.cumulativeUnits"
        :id="`row-${rowIndex}-student-cumulative-units`"
        class="student-gpa">
        {{ student.cumulativeUnits }}
      </div>
      <div
        v-if="!student.cumulativeUnits"
        :id="`row-${rowIndex}-student-cumulative-units`"
        class="student-gpa">
        --<span class="sr-only">No data</span>
      </div>
      <div class="student-text">Units Completed</div>
    </div>
    <div class="cohort-course-activity-wrapper">
      <table class="cohort-course-activity-table">
        <tr>
          <th class="cohort-course-activity-header cohort-course-activity-course-name">CLASS</th>
          <th v-if="$currentUser.canAccessCanvasData" class="cohort-course-activity-header">
            <span aria-hidden="true">BCOURSES ACTIVITY</span>
            <span class="sr-only">Most recent B Courses activity</span>
          </th>
          <th class="cohort-course-activity-header">
            <span aria-hidden="true">MID</span>
            <span class="sr-only">Midpoint grade</span>
          </th>
          <th class="cohort-course-activity-header">
            <span aria-hidden="true">FINAL</span>
            <span class="sr-only">Final grade</span>
          </th>
        </tr>
        <tr v-for="(enrollment, index) in termEnrollments" :key="index">
          <td class="cohort-course-activity-data cohort-course-activity-course-name">
            <span :id="`row-${rowIndex}-student-enrollment-name-${index}`">{{ enrollment.displayName }}</span>
            <span
              v-if="enrollment.waitlisted"
              :id="`student-${student.uid}-waitlisted-for-${enrollment.sections.length ? enrollment.sections[0].ccn : enrollment.displayName}`"
              aria-hidden="true"
              class="pl-1 red-flag-status">(W)</span>
            <span v-if="enrollment.waitlisted" class="sr-only">
              Waitlisted
            </span>
          </td>
          <td v-if="$currentUser.canAccessCanvasData" class="cohort-course-activity-data">
            <div
              v-for="(canvasSite, cIndex) in enrollment.canvasSites"
              :key="cIndex"
              class="cohort-boxplot-container">
              <span
                v-if="enrollment.canvasSites.length > 1"
                class="sr-only">
                {{ `Course site ${cIndex + 1} of ${enrollment.canvasSites.length}` }}
              </span>
              <span>{{ lastActivityDays(canvasSite.analytics) }}</span>
            </div>
            <div v-if="!get(enrollment, 'canvasSites').length">
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
              class="font-weight-bold"></span>
            <font-awesome v-if="isAlertGrade(enrollment.grade)" icon="exclamation-triangle" class="boac-exclamation" />
            <span
              v-if="!enrollment.grade"
              class="cohort-grading-basis">{{ enrollment.gradingBasis }}</span>
            <span v-if="!enrollment.grade && !enrollment.gradingBasis"><span class="sr-only">No data</span>&mdash;</span>
          </td>
        </tr>
        <tr v-if="!termEnrollments.length">
          <td class="cohort-course-activity-data cohort-course-activity-course-name faint-text">
            No {{ termNameForSisId($config.currentEnrollmentTermId) }} enrollments
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
import CuratedStudentCheckbox from '@/components/curated/CuratedStudentCheckbox'
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
    }
  },
  data: () => ({
    termEnrollments: []
  }),
  methods: {
    onClickRemoveStudent(student) {
      this.removeStudent(student.sid)
      this.alertScreenReader(`Removed ${student.firstName} ${student.lastName} from group`)
    }
  },
  computed: {
    degreePlanOwners() {
      const plans = this.get(this.student, 'degree.plans')
      if (plans) {
        return this.uniq(this.map(plans, 'group'))
      } else {
        return []
      }
    }
  },
  created() {
    const termEnrollments = this.get(this.student.term, 'enrollments', [])
    this.each(termEnrollments, this.setWaitlistedStatus)
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
.cohort-list-view-column-00 {
  align-self: center;
  flex: 0 0 30px;
  margin-right: 5px;
}
.cohort-list-view-column-01 {
  align-items: center;
  display: flex;
  flex: 0 0 30px;
  position: relative;
}
.cohort-student-name-container {
  display: flex;
}
.cohort-student-name-container div:first-child {
  flex-basis: 70%;
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
