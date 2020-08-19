<template>
  <div class="pt-2 pb-1">
    <div class="d-flex flex-wrap">
      <div class="gpa text-center">
        <div id="cumulative-gpa" class="data-number">
          <span v-if="!isNil(cumulativeGPA)">{{ round(cumulativeGPA, 3) }}</span>
          <span v-if="isNil(cumulativeGPA)">--</span>
          <span v-if="isNil(cumulativeGPA)" class="sr-only">No data</span>
        </div>
        <div class="gpa-label text-uppercase">Cumulative GPA</div>
      </div>
      <div id="gpa-trends" class="border-left">
        <div id="gpa-chart" class="ml-3">
          <div class="align-items-end d-flex justify-content-between pb-2">
            <div class="gpa-trends-label text-uppercase font-weight-bold">
              GPA Trends
            </div>
            <b-btn
              v-if="!isEmpty(student.termGpa)"
              id="show-hide-term-gpa-button"
              class="gpa-trends-more-button col-auto"
              variant="link"
              @click="showHideTermGpa()">
              {{ showTermGpa ? 'Less' : 'More' }}
            </b-btn>
          </div>
          <StudentGpaChart
            v-if="get(student, 'termGpa.length') > 1"
            :student="student" />
          <div v-if="isEmpty(student.termGpa)" class="gpa-trends-label">
            GPA Not Yet Available
          </div>
          <div v-if="!isEmpty(student.termGpa)" id="current-term-gpa" class="current-term-gpa">
            <span class="gpa-label text-uppercase">{{ student.termGpa[0].name }} GPA:</span>
            <span
              :class="{'gpa-last-term': student.termGpa[0].gpa >= 2, 'gpa-alert': student.termGpa[0].gpa < 2}"
              class="font-weight-bold">
              {{ round(student.termGpa[0].gpa, 3) }}
            </span>
          </div>
        </div>
      </div>
    </div>
    <div>
      <b-collapse
        id="term-gpa-collapse"
        v-model="showTermGpa"
        class="border-top ml-3 mr-3">
        <div class="pl-3 pr-4">
          <table
            id="table-with-gpa-per-term"
            class="term-gpa-table w-100">
            <tr>
              <th class="pt-0 pb-3 text-muted">Term</th>
              <th class="pt-0 pb-3 text-muted text-right">GPA</th>
            </tr>
            <tr
              v-for="(term, index) in student.termGpa"
              :key="index"
              :class="{'bg-light': index % 2 === 0}">
              <td class="text-nowrap">{{ term.name }}</td>
              <td class="text-nowrap text-right">
                <font-awesome
                  v-if="term.gpa < 2"
                  icon="exclamation-triangle"
                  aria-label="Icon of danger sign"
                  class="text-danger pr-2"
                  tabindex="0" />
                <span v-if="term.gpa < 2" class="sr-only">Low GPA in {{ term.name }}: </span>
                <span
                  :id="`student-gpa-term-${term.name}`"
                  :class="{'text-danger': term.gpa < 2}">{{ round(term.gpa, 3) }}</span>
              </td>
            </tr>
            <tr
              v-if="isEmpty(student.termGpa)"
              id="student-gpa-no-terms">
              <td>No previous terms</td>
              <td>--</td>
            </tr>
          </table>
        </div>
      </b-collapse>
    </div>
  </div>
</template>

<script>
import StudentGpaChart from '@/components/student/StudentGpaChart';
import Util from '@/mixins/Util';

export default {
  name: 'StudentProfileGPA',
  components: {
    StudentGpaChart
  },
  mixins: [Util],
  props: {
    student: Object
  },
  data: () => ({
    cumulativeGPA: undefined,
    showTermGpa: false
  }),
  created() {
    this.cumulativeGPA = this.get(this.student, 'sisProfile.cumulativeGPA');
  },
  methods: {
    showHideTermGpa() {
      this.showTermGpa = !this.showTermGpa;
      this.alertScreenReader(`The table with GPA per term is now ${this.showTermGpa ? 'visible' : 'hidden'}.`);
    }
  }
};
</script>

<style scoped>
.current-term-gpa {
  line-height: 1;
}
.data-number {
  font-size: 28px;
  line-height: 1.4em;
}
.gpa {
  font-weight: 700;
  margin-left: 20px;
  white-space: nowrap;
  width: 40%;
}
.gpa-alert {
  color: #d0021b;
  font-size: 11px;
}
.gpa-label {
  color: #999;
  font-size: 11px;
}
.gpa-last-term {
  color: #000;
  font-size: 11px;
  font-weight: 700;
}
.gpa-trends-label {
  color: #555;
  font-size: 11px;
}
.gpa-trends-more-button {
  border: 0;
  font-size: 12px;
  padding: 0;
  text-align: right;
}
.show-hide-caret {
  width: 12px;
}
.term-gpa-table {
  line-height: 1.2em;
  margin: 10px 0;
}
.term-gpa-table td {
  padding: 3px 0;
}
.term-gpa-table th {
  padding: 15px 0 3px 0;
}
</style>
