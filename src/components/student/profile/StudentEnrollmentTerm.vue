<template>
  <v-card
    :class="{'bg-sky-blue student-term-current': config.currentEnrollmentTermId === parseInt(term.termId)}"
    density="compact"
    elevation="0"
    min-width="300"
  >
    <v-card-title class="pt-3 student-term-header">
      <StudentEnrollmentTermAcademicStanding :student="student" :term="term" />
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
              (Dropped<span v-if="droppedSection.dropDate"> as of {{ DateTime.fromSQL(droppedSection.dropDate) }}</span>)
            </div>
          </div>
        </div>
      </div>
    </v-card-text>
    <v-card-subtitle class="pb-3">
      <StudentEnrollmentTermUnits :term="term" />
    </v-card-subtitle>
  </v-card>
</template>

<script setup>
import StudentCourse from '@/components/student/profile/StudentCourse'
import StudentEnrollmentTermAcademicStanding from '@/components/student/profile/StudentEnrollmentTermAcademicStanding.vue'
import StudentEnrollmentTermUnits from '@/components/student/profile/StudentEnrollmentTermUnits.vue'
import {DateTime} from 'luxon'
import {isEmpty} from 'lodash'
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
const student = props.student
const term = props.term
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
</style>
