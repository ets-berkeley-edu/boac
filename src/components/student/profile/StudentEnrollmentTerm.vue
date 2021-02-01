<template>
  <b-card
    no-body
    border-variant="white"
    class="student-term"
    :class="{'background-light student-term-current': $config.currentEnrollmentTermId === parseInt(term.termId)}"
  >
    <b-card-header header-bg-variant="transparent" header-class="student-term-header">
      <h3 :id="`term-${term.termId}-header`" class="font-size-18 mb-0 mr-2">{{ term.termName }}</h3>
      <StudentAcademicStanding
        v-if="term.academicStanding"
        :standing="term.academicStanding"
        :term-id="term.termId"
        class="font-size-14"
      />
      <StudentWithdrawalCancel
        v-if="student.sisProfile.withdrawalCancel"
        :withdrawal="student.sisProfile.withdrawalCancel"
        :term-id="term.termId"
        class="font-size-14"
      />
    </b-card-header>
    <b-card-body body-class="student-courses" role="table">
      <div role="rowgroup">
        <div role="row" class="student-course-label student-course-header text-nowrap">
          <div role="columnheader" class="student-course-column-name">Course</div>
          <div role="columnheader" class="student-course-column-mid-grade">Mid</div>
          <div role="columnheader" class="student-course-column-final-grade">Final</div>
          <div role="columnheader" class="student-course-column-units">Units</div>
        </div>
      </div>
      <div role="rowgroup" class="pt-2">
        <div v-if="$_.isEmpty(term.enrollments)" role="row">
          <div :id="`term-${term.termId}-no-enrollments`" role="cell" class="student-term-empty">{{ `No ${term.termName} enrollments` }}</div>
        </div>
        <StudentCourse
          v-for="(course, courseIndex) in term.enrollments"
          :key="courseIndex"
          :course="course"
          :index="courseIndex"
          :student="student"
          :term-id="term.termId"
          :year="term.academicYear"
        />
        <div>
          <div
            v-for="(droppedSection, droppedIndex) in term.droppedSections"
            :key="droppedIndex"
            class="student-course-dropped"
            role="row"
          >
            <div :id="`term-${term.termId}-dropped-course-${droppedIndex}`" role="cell">
              {{ droppedSection.displayName }} - {{ droppedSection.component }} {{ droppedSection.sectionNumber }} (Dropped)
            </div>
          </div>
        </div>
      </div>
    </b-card-body>
    <b-card-footer
      footer-bg-variant="transparent"
      footer-class="student-term-footer"
    >
      <div :id="`term-${term.termId}-gpa`">
        <span class="student-course-label mr-1">Term GPA: </span>
        <span v-if="round($_.get(term, 'termGpa.gpa', 0), 3) > 0">{{ round($_.get(term, 'termGpa.gpa', 0), 3) }}</span>
        <span v-else>&mdash;</span>
      </div>
      <div :id="`term-${term.termId}-units`">
        <span class="student-course-label align-right mr-1">Total Units: </span>
        <span v-if="$_.get(term, 'enrolledUnits', 0) !== 0">{{ $_.get(term, 'enrolledUnits', 0) }}</span>
        <span v-else>&mdash;</span>
      </div>
    </b-card-footer>
  </b-card>
</template>

<script>
import StudentAcademicStanding from '@/components/student/profile/StudentAcademicStanding'
import StudentCourse from '@/components/student/profile/StudentCourse'
import StudentWithdrawalCancel from '@/components/student/profile/StudentWithdrawalCancel'
import Util from '@/mixins/Util'

export default {
  name: 'StudentEnrollmentTerm',
  components: {
    StudentAcademicStanding,
    StudentCourse,
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
.student-academic-standing {
  line-height: 1.1;
  margin: 0;
}
.student-course-dropped {
  color: #666;
  font-weight: 500;
  line-height: 1.1;
  padding: 8px 15px;
}
.student-course-header {
  border-bottom: 1px #999 solid;
  display: flex;
  flex-direction: row;
  line-height: 1.1;
  margin: 0 10px;
  padding: 8px 0;
}
.student-course-label {
  color: #666;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}
.student-courses {
  padding: 0;
}
.student-term {
  margin: 0;
  min-width: 300px;
}
.student-term-current {
  border: 1px #999 solid !important;
  border-radius: 0;
}
.student-term-empty {
  color: #666;
  font-style: italic;
  height: 2.2em;
  padding: 3px 10px 0;
}
.student-term-header {
  align-items: baseline;
  border: none;
  display: flex;
  flex-wrap: wrap;
  font-weight: 700;
  height: 2.8em;
  line-height: 1.1;
  padding: 10px 10px 0;
}
.student-term-footer {
  border-top: 1px #999 solid !important;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin: 10px;
  padding: 10px 0 0;
}
</style>

<style>
.student-course-column-name {
  width: 60%;
}
.student-course-column-mid-grade {
  width: 15%;
}
.student-course-column-final-grade {
  width: 15%;
}
.student-course-column-units {
  text-align: right;
  width: 15%;
}
</style>
