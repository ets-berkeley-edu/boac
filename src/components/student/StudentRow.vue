<template>
  <v-container
    class="px-0"
    @focusin="hover = true"
    @focusout="hover = false"
    @mouseover="hover = true"
    @mouseleave="hover = false"
  >
    <v-row class="pb-3">
      <v-col
        class="pb-0"
        lg="4"
        md="6"
        sm="8"
      >
        <div class="align-center d-flex">
          <div v-if="listType === 'curatedGroupForOwner'">
            <button
              :id="`row-${rowIndex}-remove-student-from-curated-group`"
              class="btn btn-link pl-0"
              @click="onClickRemoveStudent(student)"
              @keyup.enter="onClickRemoveStudent(student)"
            >
              <v-icon :icon="mdiCloseCircleOutline" class="font-size-24" />
              <span class="sr-only">Remove {{ student.firstName }} {{ student.lastName }}</span>
            </button>
          </div>
          <div class="d-flex flex-column flex-sm-row">
            <div>
              <div class="align-center d-flex">
                <CuratedStudentCheckbox
                  v-if="listType === 'cohort'"
                  domain="default"
                  :student="student"
                />
                <StudentAvatar
                  :alert-count="student.alertCount"
                  class="mr-2"
                  size="medium"
                  :student="student"
                />
              </div>
              <ManageStudent
                v-if="listType === 'cohort'"
                class="d-flex justify-center ml-6"
                domain="default"
                :sr-only="!hover"
                :student="student"
              />
            </div>
            <div class="pl-2">
              <StudentRowBioColumn
                :row-index="rowIndex"
                :student="student"
                :sorted-by="sortedBy"
              />
            </div>
          </div>
        </div>
      </v-col>
      <v-col
        class="font-size-13 student-gpa-col ml-10 ml-md-0 pb-0"
        md="2"
        sm="4"
      >
        <div>
          <span
            v-if="_isNil(student.cumulativeGPA)"
            :id="`row-${rowIndex}-student-cumulative-gpa`"
            class="font-weight-bold "
          >--<span class="sr-only">No data</span></span>
          <span
            v-if="!_isNil(student.cumulativeGPA)"
            :id="`row-${rowIndex}-student-cumulative-gpa`"
            class="student-gpa"
          >{{ round(student.cumulativeGPA, 3) }}</span>
          <span class="text-medium-emphasis"> GPA (Cumulative)</span>
        </div>
        <StudentGpaChart
          v-if="_size(student.termGpa) > 1"
          :chart-description="`Chart of GPA over time. ${student.name}'s cumulative GPA is ${round(student.cumulativeGPA, 3)}`"
          :student="student"
          :width="130"
        />
        <div
          v-if="_size(student.termGpa)"
          class="student-bio-status-legend profile-last-term-gpa-outer pl-0"
        >
          <v-icon
            v-if="student.termGpa[0].gpa < 2"
            :icon="mdiAlertRhombus"
            class="boac-exclamation mr-1"
          />
          <span :id="`row-${rowIndex}-student-gpa-term-name`">{{ student.termGpa[0].termName }}</span> GPA:
          <strong
            :id="`row-${rowIndex}-student-term-gpa`"
            :class="student.termGpa[0].gpa >= 2 ? 'profile-last-term-gpa' : 'profile-gpa-alert'"
          >{{ round(student.termGpa[0].gpa, 3) }}</strong>
        </div>
      </v-col>
      <v-col
        class="font-size-13 ml-10 ml-sm-0 pb-0"
        lg="2"
        md="3"
        sm="4"
      >
        <div class="d-flex flex-wrap align-baseline">
          <div :id="`row-${rowIndex}-student-enrolled-units`" class="mr-1 font-weight-bold ">{{ _get(student.term, 'enrolledUnits', 0) }}</div>
          <div class="text-medium-emphasis">{{ isCurrentTerm ? 'Units in Progress' : 'Units Enrolled' }}</div>
        </div>
        <div
          v-if="!_isNil(_get(student.term, 'minTermUnitsAllowed')) && student.term.minTermUnitsAllowed !== config.defaultTermUnitsAllowed.min"
          class="d-flex flex-wrap align-baseline"
        >
          <div :id="`row-${rowIndex}-student-min-units`" class="mr-1 font-weight-bold ">{{ student.term.minTermUnitsAllowed }}</div>
          <div class="text-no-wrap text-medium-emphasis">Min&nbsp;Approved</div>
        </div>
        <div v-if="!_isNil(_get(student.term, 'maxTermUnitsAllowed')) && student.term.maxTermUnitsAllowed !== config.defaultTermUnitsAllowed.max">
          <span :id="`row-${rowIndex}-student-max-units`" class="mr-1 font-weight-bold ">{{ student.term.maxTermUnitsAllowed }}</span>
          <span class="text-no-wrap text-medium-emphasis">Max&nbsp;Approved</span>
        </div>
        <div v-if="isCurrentTerm" class="d-flex flex-wrap align-baseline">
          <div
            v-if="!_isUndefined(student.cumulativeUnits)"
            :id="`row-${rowIndex}-student-cumulative-units`"
            class="mr-1 font-weight-bold "
          >
            {{ student.cumulativeUnits }}
          </div>
          <div
            v-if="_isUndefined(student.cumulativeUnits)"
            :id="`row-${rowIndex}-student-cumulative-units`"
            class="font-weight-bold"
          >
            &mdash;<span class="sr-only"> No data</span>
          </div>
          <div class="text-no-wrap text-medium-emphasis">Units Completed</div>
        </div>
      </v-col>
      <v-col class="ml-10 pl-2 ml-md-auto pl-md-4 pl-lg-0 ml-lg-0 pb-0" lg="4" md="10">
        <StudentRowCourseActivity
          :row-index="rowIndex"
          :student="student"
          :term-id="termId"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import {mdiAlertRhombus, mdiCloseCircleOutline} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import StudentAvatar from '@/components/student/StudentAvatar'
import StudentGpaChart from '@/components/student/StudentGpaChart'
import StudentRowBioColumn from '@/components/student/StudentRowBioColumn.vue'
import StudentRowCourseActivity from '@/components/student/StudentRowCourseActivity.vue'
import Util from '@/mixins/Util'

export default {
  name: 'StudentRow',
  components: {
    CuratedStudentCheckbox,
    ManageStudent,
    StudentAvatar,
    StudentGpaChart,
    StudentRowBioColumn,
    StudentRowCourseActivity
  },
  mixins: [Context, Util],
  props: {
    listType: {
      required: true,
      type: String
    },
    removeStudent: {
      required: false,
      default: () => {},
      type: Function
    },
    rowIndex: {
      required: true,
      type: Number
    },
    sortedBy: {
      required: true,
      type: String
    },
    student: {
      required: true,
      type: Object
    },
    termId: {
      required: true,
      type: String
    }
  },
  data: () => ({
    hover: false
  }),
  computed: {
    isCurrentTerm() {
      return this.termId === `${this.config.currentEnrollmentTermId}`
    }
  },
  methods: {
    onClickRemoveStudent(student) {
      this.removeStudent(student.sid)
      this.alertScreenReader(`Removed ${student.firstName} ${student.lastName} from group`)
    }
  }
}
</script>

<style scoped>
.cohort-student-name-container div:first-child {
  flex-basis: 70%;
}
.profile-gpa-alert {
  color: #d0021b;
}
.profile-last-term-gpa {
  color: #000;
}
.profile-last-term-gpa-outer {
  font-size: 12px;
  padding-left: 5px;
  text-align: left;
}
.student-bio-status-legend {
  color: #999;
  font-size: 13px;
  font-weight: 300;
  text-transform: uppercase;
}
.student-gpa-col {
  min-width: 155px;
}
</style>

<style>
.cohort-boxplot-container .highcharts-tooltip {
  background-color: #000;
  border-color: #000;
  border-radius: 6px;
  padding: 8px;
  width: 250px;
}
.cohort-boxplot-container g.highcharts-tooltip {
  display: none !important;
}
.cohort-boxplot-container .highcharts-tooltip span {
  position: relative !important;
  top: 0 !important;
  left: 0 !important;
  width: auto !important;
}
</style>
