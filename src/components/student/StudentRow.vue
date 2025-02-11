<template>
  <v-row
    class="student-row pb-3"
    @focusin="hover = true"
    @focusout="hover = false"
    @mouseover="hover = true"
    @mouseleave="hover = false"
  >
    <v-col
      class="pb-0 pl-0 student-profile-col"
      cols="12"
      lg="5"
    >
      <v-container class="pa-0" fluid>
        <v-row no-gutters>
          <v-col class="student-avatar-col">
            <div class="align-center d-flex">
              <v-btn
                v-if="listType === 'curatedGroupForOwner'"
                :id="`row-${rowIndex}-remove-student-from-curated-group`"
                variant="flat"
                :icon="mdiCloseCircle"
                @click="removeStudent"
              >
                <v-icon
                  color="primary"
                  :icon="mdiCloseCircle"
                  size="22"
                />
                <span class="sr-only">Remove {{ student.firstName }} {{ student.lastName }} from curated group</span>
              </v-btn>
              <CuratedStudentCheckbox
                v-if="listType === 'cohort'"
                class="mr-3"
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
              :button-width="162"
              domain="default"
              :sr-only="!hover"
              :student="student"
            />
          </v-col>
          <v-col class="pl-sm-2">
            <StudentRowBioColumn
              :row-index="rowIndex"
              :student="student"
              :sorted-by="sortedBy"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-col>
    <v-col
      class="font-size-13 pl-10 pl-md-0 pb-lg-0 pb-2 student-gpa-col"
      cols="4"
      lg="1"
    >
      <div>
        <template v-if="isNil(student.cumulativeGPA)">
          <span :id="`row-${rowIndex}-student-cumulative-gpa`" class="font-weight-bold">
            --
            <span class="sr-only">No data</span>
          </span>
        </template>
        <template v-else>
          <span :id="`row-${rowIndex}-student-cumulative-gpa`" class="font-weight-bold">
            {{ round(student.cumulativeGPA, 3) }}
          </span>
        </template>
        <span class="text-medium-emphasis"> GPA (Cumulative)</span>
      </div>
      <StudentGpaChart
        v-if="size(student.termGpa) > 1"
        :chart-description="`Chart of GPA over time. ${student.name}'s cumulative GPA is ${round(student.cumulativeGPA, 3)}`"
        :student="student"
        :width="130"
      />
      <div
        v-if="size(student.termGpa)"
        class="align-center d-flex flex-wrap font-weight-light pl-0 profile-last-term-gpa text-uppercase text-medium-emphasis"
      >
        <v-icon
          v-if="student.termGpa[0].gpa < 2"
          :icon="mdiAlert"
          class="mr-1"
          color="warning"
          size="small"
        />
        <span :id="`row-${rowIndex}-student-gpa-term-name`" class="text-no-wrap mr-1">{{ student.termGpa[0].termName }}</span><span class="mr-1"> GPA:</span>
        <strong
          :id="`row-${rowIndex}-student-term-gpa`"
          class="text-high-emphasis font-weight-regular"
          :class="{'text-error': student.termGpa[0].gpa < 2}"
        >{{ round(student.termGpa[0].gpa, 3) }}</strong>
      </div>
    </v-col>
    <v-col
      class="font-size-13 pl-10 pl-lg-0 pr-0 pb-lg-0 pb-2 student-units-col"
      cols="4"
      lg="1"
    >
      <div class="d-flex flex-wrap align-baseline">
        <div :id="`row-${rowIndex}-student-enrolled-units`" class="mr-1 font-weight-bold ">{{ get(student.term, 'enrolledUnits', 0) }}</div>
        <div class="text-medium-emphasis">{{ isCurrentTerm ? 'Units in Progress' : 'Units Enrolled' }}</div>
      </div>
      <div
        v-if="!isNil(get(student.term, 'minTermUnitsAllowed')) && student.term.minTermUnitsAllowed !== config.defaultTermUnitsAllowed.min"
        class="d-flex flex-wrap align-baseline"
      >
        <div :id="`row-${rowIndex}-student-min-units`" class="mr-1 font-weight-bold ">{{ student.term.minTermUnitsAllowed }}</div>
        <div class="text-no-wrap text-medium-emphasis">Min&nbsp;Approved</div>
      </div>
      <div v-if="!isNil(get(student.term, 'maxTermUnitsAllowed')) && student.term.maxTermUnitsAllowed !== config.defaultTermUnitsAllowed.max">
        <span :id="`row-${rowIndex}-student-max-units`" class="mr-1 font-weight-bold ">{{ student.term.maxTermUnitsAllowed }}</span>
        <span class="text-no-wrap text-medium-emphasis">Max&nbsp;Approved</span>
      </div>
      <div v-if="isCurrentTerm" class="d-flex flex-wrap align-baseline">
        <div
          v-if="!isUndefined(student.cumulativeUnits)"
          :id="`row-${rowIndex}-student-cumulative-units`"
          class="mr-1 font-weight-bold "
        >
          {{ student.cumulativeUnits }}
        </div>
        <div
          v-if="isUndefined(student.cumulativeUnits)"
          :id="`row-${rowIndex}-student-cumulative-units`"
          class="font-weight-bold"
        >
          &mdash;<span class="sr-only"> No data</span>
        </div>
        <div class="text-no-wrap text-medium-emphasis">Units Completed</div>
      </div>
    </v-col>
    <v-col
      class="pl-9 pl-xl-0 pb-0 pr-0"
      cols="11"
      lg="5"
    >
      <StudentRowCourseActivity
        :row-index="rowIndex"
        :student="student"
        :term-id="termId"
      />
    </v-col>
  </v-row>
</template>

<script setup>
import {computed, ref} from 'vue'
import {get, isNil, isUndefined, size} from 'lodash'
import {mdiAlert, mdiCloseCircle} from '@mdi/js'
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import StudentAvatar from '@/components/student/StudentAvatar'
import StudentGpaChart from '@/components/student/StudentGpaChart'
import StudentRowBioColumn from '@/components/student/StudentRowBioColumn'
import StudentRowCourseActivity from '@/components/student/StudentRowCourseActivity'
import {round} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
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
})

const config = useContextStore().config
const hover = ref(false)

const isCurrentTerm = computed(() => {
  return props.termId === `${config.currentEnrollmentTermId}`
})
</script>

<style scoped>
.profile-last-term-gpa {
  padding-left: 5px;
  text-align: left;
}
.student-avatar-col {
  width: 150px;
  max-width: 150px;
}
.student-gpa-col {
  min-width: 150px;
}
.student-profile-col {
  max-width: 400px;
}
.student-row {
  border-bottom: 1px solid rgb(var(--v-theme-surface-light));
}
.student-units-col {
  min-width: 125px;
}
</style>
