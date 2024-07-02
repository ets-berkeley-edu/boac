<template>
  <v-card
    class="student-term"
    :class="{'background-light student-term-current': config.currentEnrollmentTermId === parseInt(term.termId)}"
    density="compact"
    elevation="0"
  >
    <v-card-title>
      <div class="font-weight-500 text-grey-darken-3">
        <h3
          :id="`term-${term.termId}-header`"
          class="font-size-18 font-weight-500 text-grey-darken-3 mb-0 mr-2"
        >
          {{ term.termName }}
        </h3>
        <span v-if="isConcurrent" class="font-size-14 text-muted ml-1 mr-3">UCBX</span>
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
      </div>
    </v-card-title>
    <v-card-text class="px-2">
      <div role="table">
        <div role="rowgroup">
          <div role="row" class="student-course-label student-course-header text-nowrap">
            <div role="columnheader" class="student-course-column-name">Course</div>
            <div role="columnheader" class="student-course-column-grade">Mid</div>
            <div role="columnheader" class="student-course-column-grade">Final</div>
            <div role="columnheader" class="student-course-column-units">Units</div>
          </div>
        </div>
        <div role="rowgroup" class="pt-2">
          <div v-if="isEmpty(term.enrollments)" role="row">
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
              :class="{'demo-mode-blur': currentUser.inDemoMode}"
              role="row"
            >
              <div :id="`term-${term.termId}-dropped-course-${droppedIndex}`" role="cell">
                {{ droppedSection.displayName }} - {{ droppedSection.component }} {{ droppedSection.sectionNumber }}
                (Dropped<span v-if="droppedSection.dropDate"> as of {{ DateTime.fromISO(droppedSection.dropDate).toFormat('MMM dd, yyyy') }}</span>)
              </div>
            </div>
          </div>
        </div>
      </div>
    </v-card-text>
    <v-card-subtitle>
      <div class="student-term-footer">
        <div class="d-flex justify-content-between">
          <div :id="`term-${term.termId}-gpa`">
            <span class="student-course-label mr-1">Term GPA: </span>
            <span v-if="round(get(term, 'termGpa.gpa', 0), 3) > 0" class="font-size-14">{{ round(get(term, 'termGpa.gpa', 0), 3) }}</span>
            <span v-else>&mdash;</span>
          </div>
          <div :id="`term-${term.termId}-units`" class="align-center d-flex justify-content-end">
            <div class="student-course-label align-right mr-1">Total Units: </div>
            <div class="font-size-14 text-right" :class="{'units-total': showMinUnits || showMaxUnits}">
              <span v-if="get(term, 'enrolledUnits', 0) !== 0">{{ numFormat(term.enrolledUnits, '0.0') }}</span>
              <span v-else>&mdash;</span>
            </div>
          </div>
        </div>
        <div
          v-if="showMinUnits || showMaxUnits"
          :id="`term-${term.termId}-units-allowed`"
          class="text-right"
        >
          <div v-if="showMinUnits" class="align-center d-flex justify-content-end">
            <div class="student-course-label align-right mr-1">Exception Min Units: </div>
            <div :id="`term-${term.termId}-min-units`" class="font-size-14 units-total">{{ numFormat(term.minTermUnitsAllowed, '0.0') }}</div>
          </div>
          <div v-if="showMaxUnits" class="align-center d-flex justify-content-end">
            <div class="student-course-label align-right mr-1">Exception Max Units: </div>
            <div :id="`term-${term.termId}-max-units`" class="font-size-14 units-total">{{ numFormat(term.maxTermUnitsAllowed, '0.0') }}</div>
          </div>
        </div>
      </div>
    </v-card-subtitle>
  </v-card>
</template>

<script setup>
import StudentAcademicStanding from '@/components/student/profile/StudentAcademicStanding'
import StudentCourse from '@/components/student/profile/StudentCourse'
import StudentWithdrawalCancel from '@/components/student/profile/StudentWithdrawalCancel'
import {get, isEmpty, isNil, some} from 'lodash'
import {numFormat, round} from '@/lib/utils'
import {ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {DateTime} from 'luxon'

const props = defineProps({
  student: {
    required: true,
    type: Object
  },
  term: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()
const config = contextStore.config
const currentUser = contextStore.currentUser
const maxUnits = props.term.maxTermUnitsAllowed
const minUnits = props.term.minTermUnitsAllowed
const isConcurrent = ref(some(props.term.enrollments, {academicCareer: 'UCBX'}))
const showMaxUnits = ref(!isNil(maxUnits) && maxUnits !== config.defaultTermUnitsAllowed.max)
const showMinUnits = ref(!isNil(minUnits) && minUnits !== config.defaultTermUnitsAllowed.min)
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
  padding: 0 0 8px 0;
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
.student-term-footer {
  border-top: 1px #999 solid !important;
  margin: 10px;
  padding: 10px 0 0;
}
.units-total {
  min-width: 30px;
}
</style>
