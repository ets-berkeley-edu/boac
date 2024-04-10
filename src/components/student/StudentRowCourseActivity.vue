<template>
  <table>
    <thead>
      <tr>
        <th class="col-course">Class</th>
        <th class="col-units">Units</th>
        <th v-if="currentUser.canAccessCanvasData" class="col-bcourses">
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
          <span :id="`row-${rowIndex}-student-enrollment-name-${index}`" :class="{'demo-mode-blur': currentUser.inDemoMode}">
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
        <td v-if="currentUser.canAccessCanvasData" class="col-bcourses pl-1">
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
          <div v-if="!_get(enrollment, 'canvasSites').length">
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
        <td v-if="currentUser.canAccessCanvasData" class="col-bcourses">
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
import {mdiAlertRhombus} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import IncompleteGradeAlertIcon from '@/components/student/IncompleteGradeAlertIcon'
import Util from '@/mixins/Util'
import {
  getSectionsWithIncompleteStatus,
  isAlertGrade,
  lastActivityDays,
  setWaitlistedStatus,
  termNameForSisId
} from '@/berkeley'

export default {
  name: 'StudentRowCourseActivity',
  components: {IncompleteGradeAlertIcon},
  mixins: [Context, Util],
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
      const termEnrollments = this._get(this.student.term, 'enrollments', [])
      this._each(termEnrollments, setWaitlistedStatus)
      return termEnrollments
    }
  },
  methods: {
    getSectionsWithIncompleteStatus,
    isAlertGrade,
    lastActivityDays,
    termNameForSisId
  }
}
</script>

<style scoped>
td {
  font-size: 12px;
  line-height: 1.4em;
  vertical-align: top;
}
th {
  color: #aaa;
  font-size: 12px;
  vertical-align: bottom;
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
