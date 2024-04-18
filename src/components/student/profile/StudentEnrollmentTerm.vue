<template>
  <v-card
    :class="{'bg-light-blue student-term-current': config.currentEnrollmentTermId === parseInt(term.termId)}"
    density="compact"
    elevation="0"
    min-width="300"
  >
    <v-card-title class="pt-3 student-term-header">
      <div class="align-baseline d-flex flex-wrap">
        <h3 :id="`term-${term.termId}-header`" class="font-size-18">{{ term.termName }}</h3>
        <div v-if="isConcurrent" class="font-size-14 text-grey-darken-2">&nbsp;UCBX</div>
        <StudentAcademicStanding
          v-if="term.academicStanding"
          class="font-size-14 ml-1"
          :standing="term.academicStanding"
        />
        <StudentWithdrawalCancel
          v-if="student.sisProfile.withdrawalCancel"
          class="font-size-14 ml-1"
          :term-id="term.termId"
          :withdrawal="student.sisProfile.withdrawalCancel"
        />
      </div>
    </v-card-title>
    <v-card-text class="pb-3">
      <div role="table">
        <div role="rowgroup">
          <div role="row" class="student-course-label student-course-header text-no-wrap">
            <div role="columnheader" class="width-60-percent">Course</div>
            <div role="columnheader" class="width-15-percent">Mid</div>
            <div role="columnheader" class="width-15-percent">Final</div>
            <div role="columnheader" class="text-right width-15-percent">Units</div>
          </div>
        </div>
        <div class="pt-3" role="rowgroup">
          <div v-if="isEmpty(term.enrollments)" role="row">
            <div :id="`term-${term.termId}-no-enrollments`" role="cell" class="ml-3 student-term-empty">{{ `No ${term.termName} enrollments` }}</div>
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
          <div
            v-for="(droppedSection, droppedIndex) in term.droppedSections"
            :key="droppedIndex"
            class="student-course-dropped"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            role="row"
          >
            <div :id="`term-${term.termId}-dropped-course-${droppedIndex}`" role="cell">
              {{ droppedSection.displayName }} - {{ droppedSection.component }} {{ droppedSection.sectionNumber }}
              (Dropped<span v-if="droppedSection.dropDate"> as of {{ DateTime.fromJSDate(droppedSection.dropDate).toFormat('MMM D, YYYY') }}</span>)
            </div>
          </div>
        </div>
      </div>
    </v-card-text>
    <v-card-subtitle class="pb-3">
      <div class="pt-3 student-term-footer">
        <div class="d-flex justify-space-between">
          <div :id="`term-${term.termId}-gpa`">
            <span class="student-course-label">Term GPA: </span>
            <span
              v-if="round(get(term, 'termGpa.gpa', 0), 3) > 0"
              class="font-size-14"
            >
              {{ round(get(term, 'termGpa.gpa', 0), 3) }}
            </span>
            <span v-else>&mdash;</span>
          </div>
          <div :id="`term-${term.termId}-units`" class="align-center d-flex justify-content-end">
            <div class="student-course-label align-right">Total Units: </div>
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
            <div class="student-course-label align-right">Exception Min Units: </div>
            <div :id="`term-${term.termId}-min-units`" class="font-size-14 units-total">
              {{ numFormat(term.minTermUnitsAllowed, '0.0') || '&mdash;' }}
            </div>
          </div>
          <div v-if="showMaxUnits" class="align-center d-flex justify-content-end">
            <div class="student-course-label align-right">Exception Max Units: </div>
            <div :id="`term-${term.termId}-max-units`" class="font-size-14 units-total">
              {{ numFormat(term.maxTermUnitsAllowed, '0.0') || '&mdash;' }}
            </div>
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
import {useContextStore} from '@/stores/context'

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
const config = useContextStore().config
const currentUser = useContextStore().currentUser
const maxUnits = props.term.maxTermUnitsAllowed
const minUnits = props.term.minTermUnitsAllowed
const isConcurrent = some(props.term.enrollments, {'academicCareer': 'UCBX'})
const showMaxUnits = isNil(maxUnits) && maxUnits !== config.defaultTermUnitsAllowed.max
const showMinUnits = !isNil(minUnits) && minUnits !== config.defaultTermUnitsAllowed.min
</script>

<style scoped>
.width-15-percent {
  width: 15%;
}
.width-60-percent {
  width: 60%;
}
.student-course-dropped {
  color: #666;
  font-weight: 500;
}
.student-course-header {
  border-bottom: 1px #999 solid;
  display: flex;
  flex-direction: row;
  line-height: 1.1;
}
.student-course-label {
  color: #666;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}
.student-term-current {
  border: 1px #999 solid !important;
}
.student-term-empty {
  color: #666;
  font-style: italic;
}
.student-term-header {
  align-items: baseline;
  border: none;
  display: flex;
  flex-wrap: wrap;
  font-weight: 700;
}
.student-term-footer {
  border-top: 1px #999 solid !important;
}
.units-total {
  min-width: 30px;
}
</style>
