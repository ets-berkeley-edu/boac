<template>
  <b-container
    class="px-0"
    fluid
    @focusin="hover = true"
    @focusout="hover = false"
    @mouseover="hover = true"
    @mouseleave="hover = false"
  >
    <b-row>
      <b-col sm="2">
        <div class="align-items-center d-flex">
          <div v-if="listType === 'curatedGroupForOwner'">
            <button
              :id="`row-${rowIndex}-remove-student-from-curated-group`"
              class="btn btn-link pl-0"
              @click="onClickRemoveStudent(student)"
              @keyup.enter="onClickRemoveStudent(student)"
            >
              <font-awesome icon="times-circle" class="font-size-24" />
              <span class="sr-only">Remove {{ student.firstName }} {{ student.lastName }}</span>
            </button>
          </div>
          <div>
            <div class="align-items-center d-flex">
              <div v-if="listType === 'cohort'" class="mr-2">
                <CuratedStudentCheckbox domain="default" :student="student" />
              </div>
              <div>
                <StudentAvatar
                  :alert-count="student.alertCount"
                  size="medium"
                  :student="student"
                />
              </div>
            </div>
            <div v-if="listType === 'cohort'" class="float-right manage-curated-student mb-1">
              <ManageStudent
                domain="default"
                :is-button-variant-link="true"
                :sr-only="!hover"
                :student="student"
              />
            </div>
          </div>
        </div>
      </b-col>
      <b-col class="pl-0" sm="2">
        <StudentRowBioColumn
          :row-index="rowIndex"
          :student="student"
          :sorted-by="sortedBy"
        />
      </b-col>
      <b-col class="pl-0" sm="2">
        <div>
          <span
            v-if="$_.isNil(student.cumulativeGPA)"
            :id="`row-${rowIndex}-student-cumulative-gpa`"
            class="student-gpa"
          >--<span class="sr-only">No data</span></span>
          <span
            v-if="!$_.isNil(student.cumulativeGPA)"
            :id="`row-${rowIndex}-student-cumulative-gpa`"
            class="student-gpa"
          >{{ round(student.cumulativeGPA, 3) }}</span>
          <span class="student-text"> GPA (Cumulative)</span>
        </div>
        <StudentGpaChart
          v-if="$_.size(student.termGpa) > 1"
          :chart-description="`Chart of GPA over time. ${student.name}'s cumulative GPA is ${round(student.cumulativeGPA, 3)}`"
          :student="student"
          :width="130"
        />
        <div
          v-if="$_.size(student.termGpa)"
          class="student-bio-status-legend profile-last-term-gpa-outer pl-0"
        >
          <font-awesome
            v-if="student.termGpa[0].gpa < 2"
            icon="exclamation-triangle"
            class="boac-exclamation mr-1"
          />
          <span :id="`row-${rowIndex}-student-gpa-term-name`">{{ student.termGpa[0].termName }}</span> GPA:
          <strong
            :id="`row-${rowIndex}-student-term-gpa`"
            :class="student.termGpa[0].gpa >= 2 ? 'profile-last-term-gpa' : 'profile-gpa-alert'"
          >{{ round(student.termGpa[0].gpa, 3) }}</strong>
        </div>
      </b-col>
      <b-col class="pl-0" sm="2">
        <div class="d-flex flex-wrap">
          <div :id="`row-${rowIndex}-student-enrolled-units`" class="mr-1 student-gpa">{{ $_.get(student.term, 'enrolledUnits', 0) }}</div>
          <div class="student-text">{{ isCurrentTerm ? 'Units in Progress' : 'Units Enrolled' }}</div>
        </div>
        <div
          v-if="!$_.isNil($_.get(student.term, 'minTermUnitsAllowed')) && student.term.minTermUnitsAllowed !== $config.defaultTermUnitsAllowed.min"
          class="d-flex flex-wrap"
        >
          <div :id="`row-${rowIndex}-student-min-units`" class="mr-1 student-gpa">{{ student.term.minTermUnitsAllowed }}</div>
          <div class="no-wrap student-text">Min&nbsp;Approved</div>
        </div>
        <div v-if="!$_.isNil($_.get(student.term, 'maxTermUnitsAllowed')) && student.term.maxTermUnitsAllowed !== $config.defaultTermUnitsAllowed.max">
          <span :id="`row-${rowIndex}-student-max-units`" class="mr-1 student-gpa">{{ student.term.maxTermUnitsAllowed }}</span>
          <span class="no-wrap student-text">Max&nbsp;Approved</span>
        </div>
        <div v-if="isCurrentTerm" class="d-flex flex-wrap">
          <div
            v-if="!$_.isUndefined(student.cumulativeUnits)"
            :id="`row-${rowIndex}-student-cumulative-units`"
            class="mr-1 student-gpa"
          >
            {{ student.cumulativeUnits }}
          </div>
          <div
            v-if="$_.isUndefined(student.cumulativeUnits)"
            :id="`row-${rowIndex}-student-cumulative-units`"
            class="student-gpa"
          >
            &mdash;<span class="sr-only"> No data</span>
          </div>
          <div class="no-wrap student-text">Units Completed</div>
        </div>
      </b-col>
      <b-col class="float-right pl-0" sm="4">
        <StudentRowCourseActivity
          :row-index="rowIndex"
          :student="student"
          :term-id="termId"
        />
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import Berkeley from '@/mixins/Berkeley'
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
  mixins: [Berkeley, Context, Util],
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
      return this.termId === `${this.$config.currentEnrollmentTermId}`
    }
  },
  methods: {
    onClickRemoveStudent(student) {
      this.removeStudent(student.sid)
      this.$announcer.polite(`Removed ${student.firstName} ${student.lastName} from group`)
    }
  }
}
</script>

<style scoped>
.cohort-student-name-container div:first-child {
  flex-basis: 70%;
}
.manage-curated-student {
  height: 24px;
  margin-right: 18px;
  width: 92px;
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
.student-gpa {
  font-size: 13px;
  font-weight: bold;
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
