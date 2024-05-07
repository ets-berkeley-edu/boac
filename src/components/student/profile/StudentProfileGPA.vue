<template>
  <div class="py-2">
    <div class="align-center d-flex flex-wrap h-100">
      <div class="border-e-sm gpa ml-0 py-2 text-center">
        <div id="cumulative-gpa" class="data-number">
          <span v-if="!_isNil(cumulativeGPA)">{{ round(cumulativeGPA, 3) }}</span>
          <span v-if="_isNil(cumulativeGPA)">--</span>
          <span v-if="_isNil(cumulativeGPA)" class="sr-only">No data</span>
        </div>
        <div class="gpa-label text-uppercase">Cumulative GPA</div>
      </div>
      <div id="gpa-trends" class="border-left gpa-trends py-2">
        <div id="gpa-chart">
          <h4 class="font-weight-bold gpa-trends-label ml-6 mt-1 text-uppercase">
            GPA Trends
          </h4>
          <StudentGpaChart
            v-if="_get(student, 'termGpa.length') > 1"
            :chart-description="`Chart of GPA over time. ${student.name}'s `"
            class="ml-4 gpa-trends-chart"
            :student="student"
          />
          <div class="ml-6">
            <div v-if="_isEmpty(student.termGpa)" class="gpa-trends-label">
              GPA Not Yet Available
            </div>
            <div
              v-if="!_isEmpty(student.termGpa)"
              id="current-term-gpa"
              class="align-end d-flex"
            >
              <div class="mr-2">
                <span class="gpa-label text-uppercase mr-1">{{ student.termGpa[0].name }} GPA:</span>
                <span
                  :class="{'gpa-last-term': student.termGpa[0].gpa >= 2, 'gpa-alert': student.termGpa[0].gpa < 2}"
                  class="font-weight-bold"
                >
                  {{ round(student.termGpa[0].gpa, 3) }}
                </span>
              </div>
              <div>
                <v-btn
                  v-if="!_isEmpty(student.termGpa)"
                  id="show-hide-term-gpa-button"
                  aria-controls="term-gpa-collapse"
                  class="pa-0 show-more-term-gpa-btn"
                  color="primary"
                  variant="plain"
                  @click="showHideTermGpa"
                >
                  <v-icon :icon="showTermGpa ? mdiMenuDown : mdiMenuRight" size="14" />
                  Show {{ showTermGpa ? 'less' : 'more' }}
                </v-btn>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <v-expand-transition
      id="term-gpa-collapse"
      class="border-t-sm mr-3"
    >
      <v-card v-if="showTermGpa" class="px-4" elevation="0">
        <table
          id="table-with-gpa-per-term"
          class="term-gpa-table w-100"
        >
          <tr>
            <th class="border-b-md pl-2 py-2 text-grey-darken-2 text-left">Term</th>
            <th class="border-b-md pr-3 py-2 text-grey-darken-2 text-right">GPA</th>
          </tr>
          <tr
            v-for="(term, index) in student.termGpa"
            :key="index"
            :class="{'bg-sky-blue': index % 2 === 0}"
          >
            <td class="font-weight-500 pl-2 py-1 text-no-wrap">{{ term.name }}</td>
            <td class="pr-2 text-no-wrap text-right">
              <v-icon v-if="term.gpa < 2" :icon="mdiAlertRhombus" class="text-danger pr-2" />
              <span v-if="term.gpa < 2" class="sr-only">Low GPA in {{ term.name }}: </span>
              <span
                :id="`student-gpa-term-${term.name}`"
                :class="{'text-danger': term.gpa < 2}"
              >{{ round(term.gpa, 3) }}</span>
            </td>
          </tr>
          <tr
            v-if="_isEmpty(student.termGpa)"
            id="student-gpa-no-terms"
          >
            <td>No previous terms</td>
            <td>&mdash;</td>
          </tr>
        </table>
      </v-card>
    </v-expand-transition>
  </div>
</template>

<script setup>
import {mdiAlertRhombus, mdiMenuDown, mdiMenuRight} from '@mdi/js'
</script>

<script>
import StudentGpaChart from '@/components/student/StudentGpaChart'
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'

export default {
  name: 'StudentProfileGPA',
  components: {
    StudentGpaChart
  },
  mixins: [Context, Util],
  props: {
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    cumulativeGPA: undefined,
    showTermGpa: false
  }),
  created() {
    this.cumulativeGPA = this._get(this.student, 'sisProfile.cumulativeGPA')
  },
  methods: {
    showHideTermGpa() {
      this.showTermGpa = !this.showTermGpa
      alertScreenReader(`The table with GPA per term is now ${this.showTermGpa ? 'visible' : 'hidden'}.`)
    }
  }
}
</script>

<style scoped>
.data-number {
  font-size: 28px;
  line-height: 1.4em;
}
.gpa {
  font-weight: 700;
  margin-left: 20px;
  min-width: 120px;
  white-space: nowrap;
  width: 40%;
}
.gpa-alert {
  color: #d0021b;
  font-size: 11px;
}
.gpa-label {
  color: #666;
  font-size: 11px;
}
.gpa-last-term {
  color: #000;
  font-size: 11px;
  font-weight: 700;
}
.gpa-trends {
  min-width: 205px;
  width: 50%;
}
.gpa-trends-chart {
  min-width: 180px;
  width: 100%;
}
.gpa-trends-label {
  color: #555;
  font-size: 11px;
}
.show-more-term-gpa-btn {
  font-size: 11px;
  height: 14px;
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
