<template>
  <div>
    <div class="flex-row">
      <div id="student-status-cumulative-gpa">
        <div class="student-status-legend">Cumulative GPA</div>
        <div class="student-status-number"
             v-if="student.sisProfile.cumulativeGPA">
          {{ student.sisProfile.cumulativeGPA | round(3) }}
        </div>
        <div class="student-status-number" v-if="!student.sisProfile.cumulativeGPA">
          -- <span class="sr-only">No data</span>
        </div>
      </div>
      <div id="student-status-gpa-trends" class="student-chart-outer">
        <div class="student-status-legend student-status-legend-heading">GPA Trends</div>
        <StudentGpaChart :student="student"
                         v-if="get(student, 'termGpa.length') > 1"/>
        <div class="student-status-legend student-status-legend-small"
             v-if="isEmpty(student.termGpa)">
          GPA Not Yet Available
        </div>
        <div class="student-status-legend student-status-legend-gpa"
             v-if="!isEmpty(student.termGpa)">
          {{ student.termGpa[0].name }} GPA:
          <strong :class="{
            'student-gpa-last-term': student.termGpa[0].gpa >= 2,
            'student-gpa-alert': student.termGpa[0].gpa < 2
          }">
            {{ student.termGpa[0].gpa | round(3) }}
          </strong>
        </div>
        <b-btn id="show-hide-term-gpa-button"
               class="toggle-btn-link"
               variant="link"
               @click="showTermGpa = !showTermGpa"
               v-if="!isEmpty(student.termGpa)">
          <i :class="{'fas fa-caret-right': !showTermGpa, 'fas fa-caret-down': showTermGpa}"></i>
          <span v-if="!showTermGpa">Show Term GPA</span>
          <span v-if="showTermGpa">Hide Term GPA</span>
        </b-btn>
      </div>
    </div>
    <table class="student-status-table" v-if="showTermGpa">
      <tr>
        <th>Term</th>
        <th>GPA</th>
      </tr>
      <tr v-for="(term, termIndex) in student.termGpa"
          :key="termIndex"
          :class="{'student-status-table-zebra': termIndex % 2 === 0}">
        <td>{{ term.name }}</td>
        <td v-if="term.gpa < 2">
          <i class="fa fa-exclamation-triangle student-gpa-term-alert student-gpa-term-alert-icon"></i>
          <div :id="`student-gpa-term-${term.name}`" class="student-gpa-term-alert">{{ term.gpa | round(3) }}</div>
        </td>
        <td :id="`student-gpa-term-${term.name}`"
            v-if="term.gpa >= 2">{{ term.gpa | round(3) }}</td>
      </tr>
      <tr id="student-gpa-no-terms"
          v-if="isEmpty(student.termGpa)">
        <td>No previous terms</td>
        <td>--</td>
      </tr>
    </table>
  </div>
</template>

<script>
import StudentGpaChart from '@/components/student/StudentGpaChart';
import Util from '@/mixins/Util';

export default {
  name: 'StudentProfileGPA',
  mixins: [Util],
  components: {
    StudentGpaChart
  },
  props: {
    student: Object
  },
  data: () => ({
    showTermGpa: false
  })
};
</script>

<style scoped>
.student-gpa-alert {
  color: #d0021b;
}
.student-gpa-last-term {
  color: #000;
  font-weight: 700;
}
.student-gpa-term-alert {
  color: #d0021b;
  position: relative;
  right: 20px;
}
.student-gpa-term-alert-icon {
  width: 20px;
}
.student-status-number {
  font-size: 42px;
  line-height: 1.2em;
}
</style>
