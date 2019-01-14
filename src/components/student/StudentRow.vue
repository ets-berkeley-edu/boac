<template>
  <div>
    <div class="cohort-list-view-column-01">
      <button :id="`student-${student.uid}-curated-cohort-remove`"
              class="btn btn-link"
              @click="removeFromCuratedGroup"
              v-if="listType === 'curatedGroup'">
        <i class="fas fa-times-circle"></i>
      </button>
      <div class="add-to-cohort-checkbox"
           v-if="listType !== 'curatedGroup'">
        <CuratedStudentCheckbox :sid="student.sid"/>
      </div>
    </div>
    <div class="cohort-list-view-column-01">
      <StudentAvatar :size="'large'"
                     :student="student"
                     :alertCount="student.alertCount"/>
    </div>
    <div class="cohort-student-bio-container">
      <div class="cohort-student-name-container">
        <div>
          <router-link :id="student.uid" :to="`/student/${student.uid}`">
            <h3 class="student-name"
                :class="{'demo-mode-blur' : user.inDemoMode}"
                v-if="sortedBy !== 'firstName'">
              {{ student.lastName }}, {{ student.firstName }}
            </h3>
            <h3 class="student-name"
                :class="{'demo-mode-blur' : user.inDemoMode}"
                v-if="sortedBy === 'firstName'">
              {{ student.firstName }} {{ student.lastName }}
            </h3>
          </router-link>
        </div>
      </div>
      <div class="student-sid" :class="{'demo-mode-blur' : user.inDemoMode}">
        {{ student.sid }}
        <span class="red-flag-status" v-if="displayAsInactive(student)">INACTIVE</span>
      </div>
      <div v-if="student.withdrawalCancel">
        <span class="red-flag-small">
          {{ student.withdrawalCancel.description }} {{ student.withdrawalCancel.date | date }}
        </span>
      </div>
      <div class="student-text">{{ student.level }}</div>
      <div class="student-text"
           v-for="(major, index) in student.majors"
           :key="index">
        {{ major }}
      </div>
      <div class="student-teams-container" v-if="student.athleticsProfile">
        <div class="student-teams"
             v-for="(team, index) in student.athleticsProfile.athletics"
             :key="index">
          {{ team.groupName }}
        </div>
      </div>
    </div>
    <div class="student-column student-column-gpa">
      <div>
        <span class="student-gpa" v-if="!student.cumulativeGPA">--<span class="sr-only">No data</span></span>
        <span class="student-gpa" v-if="student.cumulativeGPA">{{ student.cumulativeGPA | round(3) }}</span>
        <span class="student-text"> GPA (Cumulative)</span>
      </div>
      <StudentGpaChart v-if="size(student.termGpa) > 1" :student="student" :width="'130'"/>
      <div class="student-bio-status-legend profile-last-term-gpa-outer"
           v-if="size(student.termGpa)">
        <i class="fa fa-exclamation-triangle boac-exclamation"
            v-if="student.termGpa[0].gpa < 2"></i>
        <span>{{ student.termGpa[0].termName }}</span> GPA:
        <strong :class="student.termGpa[0].gpa >= 2 ? 'profile-last-term-gpa' : 'profile-gpa-alert'">{{ student.termGpa[0].gpa | round(3) }}</strong>
      </div>
    </div>
    <div class="student-column">
      <div class="student-gpa">{{ get(student.term, 'enrolledUnits', 0) }}</div>
      <div class="student-text">Units in Progress</div>
      <div class="student-gpa" v-if="student.cumulativeUnits">{{ student.cumulativeUnits }}</div>
      <div class="student-gpa" v-if="!student.cumulativeUnits">--<span class="sr-only">No data</span></div>
      <div class="student-text">Units Completed</div>
    </div>
    <div class="cohort-course-activity-wrapper">
      <table class="cohort-course-activity-table">
        <tr>
          <th class="cohort-course-activity-header cohort-course-activity-course-name">CLASS</th>
          <th class="cohort-course-activity-header">BCOURSES ACTIVITY</th>
          <th class="cohort-course-activity-header">MID</th>
          <th class="cohort-course-activity-header">FINAL</th>
        </tr>
        <tr v-for="(enrollment, index) in get(student.term, 'enrollments', [])" :key="index">
          <td class="cohort-course-activity-data cohort-course-activity-course-name">
            <div>{{ enrollment.displayName }}</div>
          </td>
          <td class="cohort-course-activity-data">
            <div class="cohort-boxplot-container"
                  v-for="(canvasSite, index) in enrollment.canvasSites"
                  :key="index">
              <span class="sr-only"
                    v-if="enrollment.canvasSites.length > 1">
                {{ `Course site ${index + 1} of ${enrollment.canvasSites.length}` }}
              </span>
              <span>{{ lastActivityDays(canvasSite.analytics) }}</span>
            </div>
            <div v-if="!get(enrollment, 'canvasSites').length"><span class="sr-only">No data</span>&mdash;</div>
          </td>
          <td class="cohort-course-activity-data">
            <span class="cohort-grade" v-if="enrollment.midtermGrade">{{ enrollment.midtermGrade }}</span>
            <i class="fas fa-exclamation-triangle boac-exclamation" v-if="isAlertGrade(enrollment.midtermGrade)"></i>
            <span v-if="!enrollment.midtermGrade"><span class="sr-only">No data</span>&mdash;</span>
          </td>
          <td class="cohort-course-activity-data">
            <span class="cohort-grade"
                  v-if="enrollment.grade">{{ enrollment.grade }}</span>
            <i class="fas fa-exclamation-triangle boac-exclamation" v-if="isAlertGrade(enrollment.grade)"></i>
            <span class="cohort-grading-basis"
                  v-if="!enrollment.grade">{{ enrollment.gradingBasis }}</span>
            <span v-if="!enrollment.grade && !enrollment.gradingBasis"><span class="sr-only">No data</span>&mdash;</span>
          </td>
        </tr>
        <tr v-if="!get(student.term, 'enrollments', []).length">
          <td class="cohort-course-activity-data cohort-course-activity-course-name faint-text">
            No {{ termNameForSisId(currentEnrollmentTermId) }} enrollments
          </td>
          <td class="cohort-course-activity-data">
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
import Berkeley from '@/mixins/Berkeley';
import Context from '@/mixins/Context';
import CuratedStudentCheckbox from '@/components/curated/CuratedStudentCheckbox';
import StudentAnalytics from '@/mixins/StudentAnalytics';
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentGpaChart from '@/components/student/StudentGpaChart';
import StudentMetadata from '@/mixins/StudentMetadata';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'StudentRow',
  mixins: [
    Berkeley,
    Context,
    StudentAnalytics,
    StudentMetadata,
    UserMetadata,
    Util
  ],
  components: {
    CuratedStudentCheckbox,
    StudentAvatar,
    StudentGpaChart
  },
  props: {
    listType: String,
    student: Object,
    sortedBy: String
  },
  methods: {
    removeFromCuratedGroup: function() {
      this.$eventHub.$emit('curated-group-remove-student', this.student.sid);
    }
  }
};
</script>
