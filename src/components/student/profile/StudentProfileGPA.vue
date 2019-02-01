<template>
  <div class="h-100 p-2">
    <div id="screen-reader-alert" class="sr-only" aria-live="polite">{{ screenReaderAlert }}</div>
    <div class="d-flex flex-wrap align-items-center">
      <div class="gpa text-center mb-3">
        <div id="cumulative-gpa"
             class="data-number">{{cumulativeGPA || '--'}}<span class="sr-only" v-if="!cumulativeGPA">No data</span></div>
        <div class="gpa-label text-uppercase">Cumulative GPA</div>
      </div>
      <div id="gpa-trends" class="h-100 border-left">
        <div id="gpa-chart" class="ml-3">
          <div class="gpa-trends-label text-uppercase font-weight-bold">GPA Trends</div>
          <StudentGpaChart :student="student"
                           v-if="get(student, 'termGpa.length') > 1"/>
          <div class="gpa-trends-label" v-if="isEmpty(student.termGpa)">
            GPA Not Yet Available
          </div>
          <div id="current-term-gpa" v-if="!isEmpty(student.termGpa)">
            <span class="gpa-label text-uppercase">{{ student.termGpa[0].name }} GPA:</span>
            <span class="font-weight-bold"
                  :class="{'gpa-last-term': student.termGpa[0].gpa >= 2, 'gpa-alert': student.termGpa[0].gpa < 2}">
              {{ student.termGpa[0].gpa | round(3) }}
            </span>
          </div>
          <div>
            <b-btn id="show-hide-term-gpa-button"
                   class="p-0 mt-1"
                   variant="link"
                   @click="showHideTermGpa()"
                   v-if="!isEmpty(student.termGpa)">
              <i class="show-hide-caret"
                 :class="{
                   'fas fa-caret-right': !showTermGpa,
                   'fas fa-caret-down mb-2': showTermGpa
                 }"></i>
              {{ showTermGpa ? 'Hide' : 'Show' }} Term GPA
            </b-btn>
          </div>
        </div>
      </div>
    </div>
    <div>
      <b-collapse id="term-gpa-collapse"
                  class="border-top ml-3 mr-3"
                  v-model="showTermGpa">
        <div class="pl-3 pr-4">
          <table id="table-with-gpa-per-term"
                 class="term-gpa-table w-100">
            <tr>
              <th class="pt-0 pb-3 text-muted">Term</th>
              <th class="pt-0 pb-3 text-muted text-right">GPA</th>
            </tr>
            <tr v-for="(term, index) in student.termGpa"
                :key="index"
                :class="{'bg-light': index % 2 === 0}">
              <td class="text-nowrap">{{ term.name }}</td>
              <td class="text-nowrap text-right">
                <i class="fa fa-exclamation-triangle text-danger pr-2"
                   aria-label="Icon of danger sign"
                   tabindex="0"
                   v-if="term.gpa < 2"></i>
                <span class="sr-only" v-if="term.gpa < 2">Low GPA in {{ term.name }}: </span>
                <span :id="`student-gpa-term-${term.name}`"
                      :class="{ 'text-danger': term.gpa < 2 }">{{ term.gpa | round(3) }}</span>
              </td>
            </tr>
            <tr id="student-gpa-no-terms"
                v-if="isEmpty(student.termGpa)">
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
  mixins: [Util],
  components: {
    StudentGpaChart
  },
  props: {
    student: Object
  },
  data: () => ({
    cumulativeGPA: undefined,
    screenReaderAlert: undefined,
    showTermGpa: false
  }),
  created() {
    this.cumulativeGPA = this.get(this.student, 'sisProfile.cumulativeGPA');
  },
  methods: {
    showHideTermGpa() {
      this.showTermGpa = !this.showTermGpa;
      this.screenReaderAlert = `The table with GPA per term is now ${
        this.showTermGpa ? 'visible' : 'hidden'
      }.`;
    }
  }
};
</script>

<style scoped>
.data-number {
  font-size: 42px;
  line-height: 1.2em;
}
.gpa {
  font-weight: 700;
  margin-left: 20px;
  white-space: nowrap;
  width: 40%;
}
.gpa-alert {
  color: #d0021b;
}
.gpa-label {
  color: #999;
  font-size: 12px;
}
.gpa-last-term {
  color: #000;
  font-weight: 700;
}
.gpa-trends-label {
  color: #555;
  font-size: 14px;
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
