<template>
  <b-card
    no-body
    border-variant="white"
    class="mb-3 p-2"
    :class="{'background-light student-term-current': $config.currentEnrollmentTermId === parseInt(term.termId)}">
    <h3 :id="`term-header-${term.termId}`" class="student-term-header">{{ term.termName }}</h3>
    <StudentAcademicStanding :standing="term.academicStanding" :term-id="term.termId" />
    <StudentWithdrawalCancel
      v-if="student.sisProfile.withdrawalCancel"
      :withdrawal="student.sisProfile.withdrawalCancel"
      :term-id="term.termId" />
    <div role="table">
      <div role="rowgroup">
        <div role="row" class="student-course student-course-label student-course-header">
          <div role="columnheader" class="student-course-column-name">Course</div>
          <div role="columnheader" class="student-course-column-mid-grade">Mid</div>
          <div role="columnheader" class="student-course-column-final-grade">Final</div>
          <div role="columnheader" class="student-course-column-units">Units</div>
        </div>
      </div>
      <div role="rowgroup">
        <div
          v-for="(course, courseIndex) in term.enrollments"
          :key="courseIndex"
          role="row"
          class="student-course">
          <div role="cell" class="student-course-column-name">
            <b-btn
              v-if="$currentUser.canAccessCanvasData && !student.fullProfilePending"
              :id="`term-${term.termId}-course-${courseIndex}-toggle`"
              v-b-toggle="`course-canvas-data-${term.termId}-${courseIndex}`"
              class="d-flex flex-row-reverse justify-content-between student-course-collapse-button"
              variant="link">
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
      </div>
    </div>
    <b-card-footer
      footer-bg-variant="transparent"
      footer-class="student-term-footer">
      <div :id="`term-${term.termId}-gpa`">
        <span class="student-course-label mr-1">Term GPA: </span>{{ $_.get(term, 'termGpa.gpa', '0.0') }}
      </div>
      <div :id="`term-${term.termId}-units`">
        <span class="student-course-label mr-1">Total Units: </span>{{ $_.get(term, 'enrolledUnits', 0) }}
      </div>
    </b-card-footer>
  </b-card>
</template>

<script>
import StudentAcademicStanding from '@/components/student/profile/StudentAcademicStanding'
import StudentWithdrawalCancel from '@/components/student/profile/StudentWithdrawalCancel'
import Util from '@/mixins/Util'

export default {
  name: 'StudentEnrollmentTerm',
  components: {
    StudentAcademicStanding,
    StudentWithdrawalCancel
  },
  mixins: [Util],
  props: {
    student: {
      required: true,
      type: Object
    },
    term: {
      required: true,
      type: Object
    }
  }
}
</script>

<style scoped>
.collapsed > .when-course-open,
:not(.collapsed) > .when-course-closed {
  display: none;
}
.student-course {
  display: flex;
  flex-direction: row;
  line-height: 1.1;
  margin: 15px 0;
  width: 100%;
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
.student-course-dropped-icon {
  color: #f0ad4e;
}
.student-course-footer {
  margin: 5px 0;
  padding: 10px 0;
}
.student-course-header {
  border-bottom: 1px #999 solid;
  margin: 5px 0;
  padding: 10px 0;
}
.student-course-column-name {
  width: 65%;
}
.student-course-column-mid-grade {
  width: 15%;
}
.student-course-column-final-grade {
  width: 15%;
}
.student-course-column-units {
  text-align: right;
  width: 10%;
}
.student-course-label {
  color: #999;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}
.student-term-current {
  border: 1px #999 solid!important;
  border-radius: 0;
}
.student-term-header {
  display: inline-block;
  font-size: 18px;
  font-weight: 700;
}
.student-term-footer {
  border-top: 1px #999 solid!important;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 5px 0 0;
}
</style>
