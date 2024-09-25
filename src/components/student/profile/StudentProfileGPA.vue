<template>
  <div class="py-2">
    <div class="d-flex flex-wrap h-100">
      <div class="align-self-center gpa ml-0 py-2 text-center">
        <div id="cumulative-gpa" class="data-number">
          <span v-if="!isNil(cumulativeGPA)">{{ round(cumulativeGPA, 3) }}</span>
          <span v-if="isNil(cumulativeGPA)">--</span>
          <span v-if="isNil(cumulativeGPA)" class="sr-only">No data</span>
        </div>
        <div class="font-size-12 text-medium-emphasis text-uppercase">Cumulative GPA</div>
      </div>
      <div id="gpa-trends" class="align-self-center border-s-sm gpa-trends py-2">
        <div id="gpa-chart">
          <h4 class="font-weight-bold font-size-12 text-medium-emphasis ml-6 mt-1 text-uppercase">
            GPA Trends
          </h4>
          <StudentGpaChart
            v-if="get(student, 'termGpa.length') > 1"
            :chart-description="`Chart of GPA over time. ${student.name}'s `"
            class="ml-4 gpa-trends-chart"
            :student="student"
          />
          <div class="ml-6">
            <div v-if="isEmpty(student.termGpa)" class="font-size-12 text-medium-emphasis">
              GPA Not Yet Available
            </div>
            <div
              v-if="!isEmpty(student.termGpa)"
              id="current-term-gpa"
              class="align-center d-flex"
            >
              <div class="mr-2">
                <span class="font-size-12 text-medium-emphasis text-uppercase mr-1">{{ student.termGpa[0].name }} GPA:</span>
                <span
                  :class="{'gpa-last-term': student.termGpa[0].gpa >= 2, 'gpa-alert': student.termGpa[0].gpa < 2}"
                  class="font-weight-bold"
                >
                  {{ round(student.termGpa[0].gpa, 3) }}
                </span>
              </div>
              <v-btn
                v-if="!isEmpty(student.termGpa)"
                id="show-hide-term-gpa-button"
                aria-controls="term-gpa-collapse"
                class="pa-0 show-more-term-gpa-btn"
                color="primary"
                variant="text"
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
    <v-expand-transition
      id="term-gpa-collapse"
      class="border-t-sm mr-3"
    >
      <v-card v-if="showTermGpa" class="px-4" elevation="0">
        <table
          id="table-with-gpa-per-term"
          class="term-gpa-table w-100"
        >
          <thead>
            <tr>
              <th class="border-b-md pl-2 py-2 text-medium-emphasis">Term</th>
              <th class="border-b-md pr-3 py-2 text-medium-emphasis d-flex justify-end">GPA</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(term, index) in student.termGpa"
              :key="index"
              :class="{'bg-sky-blue': index % 2 === 0}"
            >
              <td class="font-weight-500 pl-2 text-no-wrap">{{ term.name }}</td>
              <td class="pr-2 text-no-wrap d-flex align-center justify-end">
                <v-icon
                  v-if="term.gpa < 2"
                  class="pr-2"
                  color="error"
                  :icon="mdiAlert"
                />
                <span v-if="term.gpa < 2" class="sr-only">Low GPA in {{ term.name }}: </span>
                <span
                  :id="`student-gpa-term-${term.name}`"
                  :class="{'text-error font-weight-medium': term.gpa < 2}"
                >{{ round(term.gpa, 3) }}</span>
              </td>
            </tr>
            <tr
              v-if="isEmpty(student.termGpa)"
              id="student-gpa-no-terms"
            >
              <td>No previous terms</td>
              <td>&mdash;</td>
            </tr>
          </tbody>
        </table>
      </v-card>
    </v-expand-transition>
  </div>
</template>

<script setup>
import StudentGpaChart from '@/components/student/StudentGpaChart'
import {alertScreenReader, round} from '@/lib/utils'
import {get, isEmpty, isNil} from 'lodash'
import {mdiAlert, mdiMenuDown, mdiMenuRight} from '@mdi/js'
import {ref} from 'vue'

const props = defineProps({
  student: {
    required: true,
    type: Object
  }
})

const cumulativeGPA = get(props.student, 'sisProfile.cumulativeGPA')
const showTermGpa = ref(false)

const showHideTermGpa = () => {
  showTermGpa.value = !showTermGpa.value
  alertScreenReader(`The table with GPA per term is now ${showTermGpa.value ? 'visible' : 'hidden'}.`)
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
  color: rgb(var(--v-theme-error));
  font-size: 12px;
}
.gpa-last-term {
  font-size: 12px;
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
.show-more-term-gpa-btn {
  font-size: 12px;
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
