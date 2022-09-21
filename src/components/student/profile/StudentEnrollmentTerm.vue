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
        class="font-size-14"
      />
      <StudentWithdrawalCancel
        v-if="student.sisProfile.withdrawalCancel"
        :withdrawal="student.sisProfile.withdrawalCancel"
        :term-id="term.termId"
        class="font-size-14"
      />
    </b-card-header>
    <b-card-body body-class="p-0" role="table">
      <div role="rowgroup">
        <div role="row" class="student-course-label student-course-header text-nowrap">
          <div role="columnheader" class="student-course-column-name">Course</div>
          <div role="columnheader" class="student-course-column-grade">Mid</div>
          <div role="columnheader" class="student-course-column-grade">Final</div>
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
              {{ droppedSection.displayName }} - {{ droppedSection.component }} {{ droppedSection.sectionNumber }}
              (Dropped<span v-if="droppedSection.dropDate"> as of {{ droppedSection.dropDate | moment('MMM D, YYYY') }}</span>)
            </div>
          </div>
        </div>
      </div>
    </b-card-body>
    <b-card-footer footer-bg-variant="transparent" footer-class="student-term-footer">
      <div class="d-flex justify-content-between">
        <div :id="`term-${term.termId}-gpa`">
          <span class="student-course-label mr-1">Term GPA: </span>
          <span v-if="round($_.get(term, 'termGpa.gpa', 0), 3) > 0" class="font-size-14">{{ round($_.get(term, 'termGpa.gpa', 0), 3) }}</span>
          <span v-else>&mdash;</span>
        </div>
        <div :id="`term-${term.termId}-units`" class="align-items-center d-flex justify-content-end">
          <div class="student-course-label align-right mr-1">Total Units: </div>
          <div class="font-size-14 text-right" :class="{'units-total': showMinUnits || showMaxUnits}">
            <span v-if="$_.get(term, 'enrolledUnits', 0) !== 0">{{ numFormat(term.enrolledUnits, '0.0') }}</span>
            <span v-else>&mdash;</span>
          </div>
        </div>
      </div>
      <div
        v-if="showMinUnits || showMaxUnits"
        :id="`term-${term.termId}-units-allowed`"
        class="text-right"
      >
        <div v-if="showMinUnits" class="align-items-center d-flex justify-content-end">
          <div class="student-course-label align-right mr-1">Exception Min Units: </div>
          <div :id="`term-${term.termId}-min-units`" class="font-size-14 units-total">{{ numFormat(term.minTermUnitsAllowed, '0.0') }}</div>
        </div>
        <div v-if="showMaxUnits" class="align-items-center d-flex justify-content-end">
          <div class="student-course-label align-right mr-1">Exception Max Units: </div>
          <div :id="`term-${term.termId}-max-units`" class="font-size-14 units-total">{{ numFormat(term.maxTermUnitsAllowed, '0.0') }}</div>
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
  },
  data: () => ({
    showMaxUnits: undefined,
    showMinUnits: undefined,
  }),
  created() {
    const maxUnits = this.term.maxTermUnitsAllowed
    const minUnits = this.term.minTermUnitsAllowed
    this.showMaxUnits = !this.$_.isNil(maxUnits) && maxUnits !== this.$config.defaultTermUnitsAllowed.max
    this.showMinUnits = !this.$_.isNil(minUnits) && minUnits !== this.$config.defaultTermUnitsAllowed.min
  }
}
</script>

<style scoped>
.student-course-column-grade {
  display: flex;
  justify-content: space-between;
  width: 15%;
}
.student-course-column-name {
  width: 60%;
}
.student-course-column-units {
  text-align: right;
  width: 15%;
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
  margin: 10px;
  padding: 10px 0 0;
}
.units-total {
  min-width: 30px;
}
</style>
