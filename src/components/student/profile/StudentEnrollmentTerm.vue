<template>
  <b-card
    no-body
    border-variant="white"
    class="student-term"
    :class="{'background-light student-term-current': $config.currentEnrollmentTermId === parseInt(term.termId)}"
  >
    <b-card-header header-bg-variant="transparent" header-class="student-term-header">
      <h3 :id="`term-header-${term.termId}`" class="font-size-18 mr-3">{{ term.termName }}</h3>
      <StudentAcademicStanding :standing="term.academicStanding" :term-id="term.termId" />
      <StudentWithdrawalCancel
        v-if="student.sisProfile.withdrawalCancel"
        :withdrawal="student.sisProfile.withdrawalCancel"
        :term-id="term.termId"
      />
    </b-card-header>
    <b-card-body body-class="student-courses" role="table">
      <div role="rowgroup">
        <div role="row" class="student-course-label student-course-header">
          <div role="columnheader" class="student-course-column-name">Course</div>
          <div role="columnheader" class="student-course-column-mid-grade">Mid</div>
          <div role="columnheader" class="student-course-column-final-grade">Final</div>
          <div role="columnheader" class="student-course-column-units">Units</div>
        </div>
      </div>
      <div role="rowgroup">
        <div v-if="$_.isEmpty(term.enrollments)" role="row">
          <div class="font-italic text-muted" role="cell">{{ `No ${term.termName} enrollments` }}</div>
        </div>
        <div
          v-for="(course, courseIndex) in term.enrollments"
          :key="courseIndex"
        >
          <StudentCourse
            :course="course"
            :index="courseIndex"
            :student="student"
            :term="term"
          />
        </div>
        <div>
          <div
            v-for="(droppedSection, dsIndex) in term.droppedSections"
            :key="dsIndex"
            class="student-course-dropped"
            role="row"
          >
            <div role="cell">
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
        <span class="student-course-label mr-1">Term GPA: </span>{{ round($_.get(term, 'termGpa.gpa', 0), 3) }}
      </div>
      <div :id="`term-${term.termId}-units`">
        <span class="student-course-label align-right mr-1">Total Units: </span>{{ $_.get(term, 'enrolledUnits', 0) }}
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
  color: #999;
  font-weight: 500;
  line-height: 1.1;
  padding: 8px 15px;
}
.student-course-header {
  border-bottom: 1px #999 solid;
  display: flex;
  flex-direction: row;
  line-height: 1.1;
  padding: 8px 0;
}
.student-course-label {
  color: #999;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}
.student-courses {
  padding: 0 10px;
}
.student-term {
  margin: 0 10px 10px;
}
.student-term-current {
  border: 1px #999 solid!important;
  border-radius: 0;
}
.student-term-header {
  align-items: baseline;
  border: none;
  display: flex;
  font-weight: 700;
  padding: 10px 10px 0;
}
.student-term-footer {
  border-top: 1px #999 solid!important;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin: 10px;
  padding: 10px 0 0;
}
</style>

<style>
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
</style>
