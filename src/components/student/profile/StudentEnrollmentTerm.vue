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
        <div role="row" class="student-course-label student-course-header">
          <div role="columnheader" class="student-course-column-name">Course</div>
          <div role="columnheader" class="student-course-column-mid-grade">Mid</div>
          <div role="columnheader" class="student-course-column-final-grade">Final</div>
          <div role="columnheader" class="student-course-column-units">Units</div>
        </div>
      </div>
      <div role="rowgroup">
        <div
          v-for="(course, courseIndex) in term.enrollments"
          :key="courseIndex">
          <StudentCourse
            :course="course"
            :index="courseIndex"
            :student="student"
            :term="term" />
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
      <div
        v-if="!$_.isEmpty(term.droppedSections)"
        class="student-course mt-3 pt-1"
        is-open="true">
        <div v-for="(droppedSection, dsIndex) in term.droppedSections" :key="dsIndex" class="ml-4">
          <div class="font-weight-bold">
            {{ droppedSection.displayName }} - {{ droppedSection.component }} {{ droppedSection.sectionNumber }}
            <div class="student-course-notation">
              <font-awesome icon="exclamation-triangle" class="student-course-dropped-icon" /> Dropped
            </div>
          </div>
        </div>
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
.student-course-dropped-icon {
  color: #f0ad4e;
}
.student-course-header {
  border-bottom: 1px #999 solid;
  display: flex;
  flex-direction: row;
  line-height: 1.1;
  margin: 5px 0;
  padding: 10px;
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
