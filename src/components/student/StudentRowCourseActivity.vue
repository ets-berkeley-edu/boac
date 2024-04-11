<template>
  <table class="table-hover w-100">
    <thead class="text-none">
      <tr>
        <th class="col-course">Class</th>
        <th class="col-units">Units</th>
        <th v-if="useContextStore().currentUser.canAccessCanvasData" class="col-bcourses">
          <span aria-hidden="true">bCourses Activity</span>
          <span class="sr-only">Most recent B Courses activity</span>
        </th>
        <th class="col-midterm">
          <span aria-hidden="true">Mid</span>
          <span class="sr-only">Midpoint grade</span>
        </th>
        <th class="col-final">
          <span>Final<span class="sr-only"> grade</span></span>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(enrollment, index) in termEnrollments" :key="index">
        <td class="col-course">
          <span :id="`row-${rowIndex}-student-enrollment-name-${index}`" :class="{'demo-mode-blur': useContextStore().currentUser.inDemoMode}">
            {{ enrollment.displayName }}
          </span>
          <span
            v-if="enrollment.waitlisted"
            :id="`student-${student.uid}-waitlisted-for-${enrollment.sections.length ? enrollment.sections[0].ccn : enrollment.displayName}`"
            aria-hidden="true"
            class="pl-1 red-flag-status"
          >(W)</span>
          <span v-if="enrollment.waitlisted" class="sr-only">
            Waitlisted
          </span>
        </td>
        <td class="col-units pl-2">
          {{ enrollment.units || '&mdash;' }}
        </td>
        <td v-if="useContextStore().currentUser.canAccessCanvasData" class="col-bcourses pl-1">
          <div
            v-for="(canvasSite, cIndex) in enrollment.canvasSites"
            :key="cIndex"
          >
            <span
              v-if="enrollment.canvasSites.length > 1"
              class="sr-only"
            >
              {{ `Course site ${cIndex + 1} of ${enrollment.canvasSites.length}` }}
            </span>
            {{ lastActivityDays(canvasSite.analytics) }}
          </div>
          <div v-if="!get(enrollment, 'canvasSites').length">
            <span class="sr-only">No data </span>&mdash;
          </div>
        </td>
        <td class="col-midterm">
          <span v-if="enrollment.midtermGrade" v-accessible-grade="enrollment.midtermGrade" class="font-weight-bold"></span>
          <v-icon v-if="isAlertGrade(enrollment.midtermGrade)" :icon="mdiAlertRhombus" class="boac-exclamation" />
          <span v-if="!enrollment.midtermGrade"><span class="sr-only">No data</span>&mdash;</span>
        </td>
        <td class="col-final">
          <span
            v-if="enrollment.grade"
            v-accessible-grade="enrollment.grade"
            class="font-weight-bold"
          ></span>
          <v-icon
            v-if="isAlertGrade(enrollment.grade)"
            :icon="mdiAlertRhombus"
            class="boac-exclamation ml-1"
          />
          <IncompleteGradeAlertIcon
            v-if="getSectionsWithIncompleteStatus(enrollment.sections).length"
            :course="enrollment"
            :index="index"
            :term-id="termId"
          />
          <span
            v-if="!enrollment.grade"
            class="cohort-grading-basis"
          >{{ enrollment.gradingBasis }}</span>
          <span v-if="!enrollment.grade && !enrollment.gradingBasis"><span class="sr-only">No data</span>&mdash;</span>
        </td>
      </tr>
      <tr v-if="!termEnrollments.length">
        <td class="col-course text-grey">
          No {{ termNameForSisId(termId) }} enrollments
        </td>
        <td class="col-units">
          <span class="sr-only">No data</span>&mdash;
        </td>
        <td v-if="useContextStore().currentUser.canAccessCanvasData" class="col-bcourses">
          <span class="sr-only">No data</span>&mdash;
        </td>
        <td class="col-midterm">
          <span class="sr-only">No data</span>&mdash;
        </td>
        <td class="col-final">
          <span class="sr-only">No data</span>&mdash;
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
import {each, get} from 'lodash'
import {
  getSectionsWithIncompleteStatus,
  isAlertGrade,
  lastActivityDays,
  setWaitlistedStatus,
  termNameForSisId
} from '@/berkeley'
import {mdiAlertRhombus} from '@mdi/js'
import {useContextStore} from '@/stores/context'
</script>

<script>
import IncompleteGradeAlertIcon from '@/components/student/IncompleteGradeAlertIcon'

export default {
  name: 'StudentRowCourseActivity',
  components: {IncompleteGradeAlertIcon},
  props: {
    rowIndex: {
      required: true,
      type: Number
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
  computed: {
    termEnrollments() {
      const termEnrollments = get(this.student.term, 'enrollments', [])
      each(termEnrollments, setWaitlistedStatus)
      return termEnrollments
    }
  }
}
</script>

<style scoped>
td {
  font-size: 13px;
  line-height: 1.1em;
  padding: 0.2rem 0.3rem;
}
th {
  line-height: 1.1em;
  padding: 0.2rem 0.3rem;
}
.col-course {
  min-width: 80px;
  padding-right: 15px;
}
.col-bcourses {
  min-width: 120px;
}
.col-final {
  min-width: 40px;
}
.col-midterm {
  min-width: 40px;
}
.col-units {
  min-width: 40px;
}
</style>
