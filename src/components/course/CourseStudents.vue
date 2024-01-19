<template>
  <b-table
    :borderless="true"
    :fields="fields"
    :items="section.students"
    :small="true"
    :tbody-tr-class="rowClass"
    stacked="md"
    thead-class="sortable-table-header border-bottom"
    @row-hovered="rowHovered"
    @row-unhovered="rowUnhovered"
  >
    <template v-slot:cell(avatar)="row">
      <div class="align-items-center d-flex">
        <div class="px-2">
          <CuratedStudentCheckbox domain="default" :student="row.item" />
        </div>
        <div class="mb-1 text-center">
          <StudentAvatar :key="row.item.sid" size="medium" :student="row.item" />
          <ManageStudent
            domain="default"
            :is-button-variant-link="true"
            :sr-only="hoverSid !== row.item.sid"
            :student="row.item"
          />
        </div>
      </div>
    </template>
    <template v-slot:cell(profile)="row">
      <div>
        <router-link
          v-if="row.item.uid"
          :id="`link-to-student-${row.item.uid}`"
          :to="studentRoutePath(row.item.uid, $currentUser.inDemoMode)"
        >
          <h3
            :class="{'demo-mode-blur': $currentUser.inDemoMode}"
            class="m-0 p-0 student-name"
          >
            <span v-if="row.item.firstName" v-html="lastNameFirst(row.item)"></span>
            <span v-if="!row.item.firstName" v-html="row.item.lastName"></span>
          </h3>
        </router-link>
        <span
          v-if="!row.item.uid"
          :id="`student-${row.item.sid}-has-no-uid`"
          class="font-size-16 m-0 p-0 "
          :class="{'demo-mode-blur': $currentUser.inDemoMode}"
        >
          <span v-if="row.item.firstName" v-html="lastNameFirst(row.item)"></span>
          <span v-if="!row.item.firstName" v-html="row.item.lastName"></span>
        </span>
      </div>
      <div :id="`row-${row.index}-student-sid`" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="student-sid">
        {{ row.item.sid }}
        <span
          v-if="row.item.enrollment.enrollmentStatus === 'W'"
          :id="`student-${row.item.uid}-waitlisted-for-${section.termId}-${section.sectionId}`"
          class="red-flag-status"
        >WAITLISTED</span>
        <span
          v-if="row.item.academicCareerStatus === 'Inactive'"
          :id="`student-${row.item.uid}-inactive-for-${section.termId}-${section.sectionId}`"
          class="red-flag-status"
        >INACTIVE</span>
        <span
          v-if="row.item.academicCareerStatus === 'Completed'"
          class="ml-1"
          uib-tooltip="Graduated"
          tooltip-placement="bottom"
        >
          <font-awesome icon="graduation-cap" />
        </span>
      </div>
      <div
        v-if="displayAsAscInactive(row.item)"
        :id="`student-${row.item.uid}-asc-inactive-for-${section.termId}-${section.sectionId}`"
        class="student-sid red-flag-status"
      >
        ASC INACTIVE
      </div>
      <div
        v-if="displayAsCoeInactive(row.item)"
        :id="`student-${row.item.uid}-coe-inactive-for-${section.termId}-${section.sectionId}`"
        class="student-sid red-flag-status"
      >
        CoE INACTIVE
      </div>
      <div v-if="row.item.academicCareerStatus !== 'Completed'">
        <div :id="`student-${row.item.uid}-level`">
          <span class="student-text">{{ row.item.level }}</span>
        </div>
        <div :id="`student-${row.item.uid}-majors`">
          <div v-for="major in row.item.majors" :key="major" class="student-text">{{ major }}</div>
        </div>
      </div>
      <div v-if="row.item.academicCareerStatus === 'Completed'">
        <DegreesAwarded :student="row.item" />
        <div :id="`student-${row.item.uid}-graduated-colleges`">
          <div v-for="owner in degreePlanOwners(row.item)" :key="owner" class="student-text">
            {{ owner }}
          </div>
        </div>
      </div>
      <div>
        <div v-if="row.item.athleticsProfile" :id="`student-${row.item.uid}-teams`" class="student-teams-container">
          <div v-for="membership in row.item.athleticsProfile.athletics" :key="membership.groupName" class="student-text">
            {{ membership.groupName }}
            <span v-if="row.item.athleticsProfile.isActiveAsc === false"> (Inactive)</span>
          </div>
        </div>
      </div>
    </template>

    <template v-slot:cell(courseSites)="row">
      <div class="course-sites flex-col font-size-14 pl-2">
        <div
          v-for="(canvasSite, index) in row.item.enrollment.canvasSites"
          :key="index"
        >
          <strong>{{ canvasSite.courseCode }}</strong>
        </div>
        <div v-if="!row.item.enrollment.canvasSites.length">
          No course site
        </div>
      </div>
    </template>

    <template v-slot:cell(assignmentsSubmitted)="row">
      <div v-if="row.item.enrollment.canvasSites.length" class="flex-col">
        <div
          v-for="canvasSite in row.item.enrollment.canvasSites"
          :key="canvasSite.canvasCourseId"
        >
          <span v-if="row.item.enrollment.canvasSites.length > 1" class="sr-only">
            {{ canvasSite.courseCode }}
          </span>
          <StudentBoxplot
            v-if="canvasSite.analytics.assignmentsSubmitted.boxPlottable"
            :chart-description="`Chart of ${row.item.firstName} ${row.item.lastName}'s assignments submitted in ${canvasSite.courseCode}`"
            :dataset="canvasSite.analytics.assignmentsSubmitted"
            :numeric-id="`${row.item.uid}-${canvasSite.canvasCourseId}-assignments`"
          />
          <div v-if="canvasSite.analytics.assignmentsSubmitted.boxPlottable" class="sr-only">
            <div>User score: {{ canvasSite.analytics.assignmentsSubmitted.student.raw }}</div>
            <div>Maximum:  {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[10] }}</div>
            <div>70th Percentile: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[7] }}</div>
            <div>50th Percentile: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[5] }}</div>
            <div>30th Percentile: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[3] }}</div>
            <div>Minimum: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[0] }}</div>
          </div>
          <div v-if="!canvasSite.analytics.assignmentsSubmitted.boxPlottable" class="font-size-14 text-nowrap">
            <div v-if="canvasSite.analytics.assignmentsSubmitted.courseDeciles">
              <strong>{{ canvasSite.analytics.assignmentsSubmitted.student.raw }}</strong>
              <span class="faint-text">
                (Max: {{ canvasSite.analytics.assignmentsSubmitted.courseDeciles[10] }})
              </span>
            </div>
            <div v-if="!canvasSite.analytics.assignmentsSubmitted.courseDeciles">
              No Data
            </div>
          </div>
        </div>
      </div>
      <span
        v-if="!row.item.enrollment.canvasSites.length"
      ><span class="sr-only">No data</span>&mdash;</span>
    </template>

    <template v-slot:cell(assignmentGrades)="row">
      <div class="flex-col">
        <div
          v-for="canvasSite in row.item.enrollment.canvasSites"
          :key="canvasSite.canvasCourseId"
          class="profile-boxplot-container"
        >
          <span v-if="row.item.enrollment.canvasSites.length > 1" class="sr-only">
            {{ canvasSite.courseCode }}
          </span>
          <StudentBoxplot
            v-if="canvasSite.analytics.currentScore.boxPlottable"
            :chart-description="`Chart of ${row.item.firstName} ${row.item.lastName}'s assignment grades in ${canvasSite.courseCode}`"
            :dataset="canvasSite.analytics.currentScore"
            :numeric-id="`${row.item.uid}-${canvasSite.canvasCourseId}`"
          />
          <div v-if="canvasSite.analytics.currentScore.boxPlottable" class="sr-only">
            <div>User score: {{ canvasSite.analytics.currentScore.student.raw }}</div>
            <div>Maximum:  {{ canvasSite.analytics.currentScore.courseDeciles[10] }}</div>
            <div>70th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[7] }}</div>
            <div>50th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[5] }}</div>
            <div>30th Percentile: {{ canvasSite.analytics.currentScore.courseDeciles[3] }}</div>
            <div>Minimum: {{ canvasSite.analytics.currentScore.courseDeciles[0] }}</div>
          </div>
          <div v-if="!canvasSite.analytics.currentScore.boxPlottable" class="font-size-14">
            <div v-if="canvasSite.analytics.currentScore.courseDeciles">
              Score: <strong>{{ canvasSite.analytics.currentScore.student.raw }}</strong>
              <div class="faint-text">
                (Max: {{ canvasSite.analytics.currentScore.courseDeciles[10] }})
              </div>
            </div>
            <div v-if="!canvasSite.analytics.currentScore.courseDeciles">
              No Data
            </div>
          </div>
        </div>
        <span v-if="!row.item.enrollment.canvasSites.length"><span class="sr-only">No data</span>&mdash;</span>
      </div>
    </template>

    <template v-slot:cell(bCourses)="row">
      <div class="flex-col font-size-14">
        <div
          v-for="canvasSite in row.item.enrollment.canvasSites"
          :key="canvasSite.canvasCourseId"
          class="profile-boxplot-container"
        >
          <span v-if="row.item.enrollment.canvasSites.length > 1" class="sr-only">
            {{ canvasSite.courseCode }}
          </span>
          {{ lastActivityDays(canvasSite.analytics) }}
        </div>
        <span v-if="!row.item.enrollment.canvasSites.length"><span class="sr-only">No data</span>&mdash;</span>
      </div>
    </template>

    <template v-slot:cell(midtermGrade)="row">
      <span v-if="row.item.enrollment.midtermGrade" v-accessible-grade="row.item.enrollment.midtermGrade" class="font-weight-bold font-size-14"></span>
      <font-awesome v-if="isAlertGrade(row.item.enrollment.midtermGrade)" icon="exclamation-triangle" class="boac-exclamation" />
      <span v-if="!row.item.enrollment.midtermGrade"><span class="sr-only">No data</span>&mdash;</span>
    </template>

    <template v-slot:cell(finalGrade)="row">
      <span v-if="row.item.enrollment.grade" v-accessible-grade="row.item.enrollment.grade" class="font-weight-bold font-size-14"></span>
      <font-awesome v-if="isAlertGrade(row.item.enrollment.grade)" icon="exclamation-triangle" class="boac-exclamation" />
      <span v-if="!row.item.enrollment.grade" class="cohort-grading-basis">
        {{ row.item.enrollment.gradingBasis }}
      </span>
    </template>
  </b-table>
</template>

<script>
import Context from '@/mixins/Context'
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import DegreesAwarded from '@/components/student/DegreesAwarded'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import StudentAnalytics from '@/mixins/StudentAnalytics'
import StudentAvatar from '@/components/student/StudentAvatar'
import StudentBoxplot from '@/components/student/StudentBoxplot'
import StudentMetadata from '@/mixins/StudentMetadata'
import Util from '@/mixins/Util'

export default {
  name: 'CourseStudents',
  components: {
    CuratedStudentCheckbox,
    DegreesAwarded,
    ManageStudent,
    StudentAvatar,
    StudentBoxplot
  },
  mixins: [
    Context,
    StudentAnalytics,
    StudentMetadata,
    Util
  ],
  props: {
    featured: String,
    section: Object
  },
  data: () => ({
    fields: undefined,
    hoverSid: undefined
  }),
  created() {
    let cols = [
      {key: 'avatar', label: ''},
      {key: 'profile', label: ''},
      {key: 'courseSites', label: 'Course Site(s)'},
      {key: 'assignmentsSubmitted', label: 'Assignments Submitted'},
      {key: 'assignmentGrades', label: 'Assignment Grades'}
    ]
    if (this.$config.currentEnrollmentTermId === parseInt(this.section.termId)) {
      cols.push(
        {key: 'bCourses', label: 'bCourses Activity'}
      )
    }
    cols = cols.concat([
      {key: 'midtermGrade', label: 'Mid'},
      {key: 'finalGrade', label: 'Final', class: 'pr-3'}
    ])
    this.fields = cols
  },
  methods: {
    degreePlanOwners(student) {
      const plans = this.$_.get(student, 'degree.plans')
      if (plans) {
        return this.$_.uniq(this.$_.map(plans, 'group'))
      } else {
        return []
      }
    },
    rowClass(item) {
      return this.featured === item.uid ? 'list-group-item-info pb-3 pt-3' : 'border-bottom pb-3 pt-3'
    },
    rowHovered(item) {
      this.hoverSid = item.sid
    },
    rowUnhovered() {
      this.hoverSid = null
    }
  }
}
</script>

<style scoped>
.course-sites {
  border-left: 1px solid #ddd;
}
.course-list-view-column-profile button {
  padding: 2px 0 0 5px;
}
.flex-col > div {
  align-items: flex-start;
  flex: 0 0 50px;
}
.student-name {
  color: #49b;
  font-size: 16px;
  max-width: 150px;
}
</style>
