<template>
  <table id="cohort-admitted-students" class="border-top-0 table table-sm table-borderless">
    <thead class="sortable-table-header">
      <tr>
        <th v-if="includeCuratedCheckbox || removeStudent" class="pt-3"></th>
        <th class="align-top pt-3">Name</th>
        <th class="align-top pt-3 text-nowrap">CS ID</th>
        <th class="align-top pt-3">SIR</th>
        <th class="align-top pt-3">CEP</th>
        <th class="align-top pt-3 text-nowrap">Re-entry</th>
        <th class="align-top pt-3 text-nowrap">1st Gen</th>
        <th class="align-top pt-3">UREM</th>
        <th class="align-top pt-3">Waiver</th>
        <th class="align-top pt-3 text-nowrap">INT'L</th>
        <th class="align-top pt-3">Freshman or Transfer</th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="(student, index) in students"
        :id="`admit-${getSid(student)}`"
        :key="index"
      >
        <td v-if="includeCuratedCheckbox" class="pr-1 pt-1">
          <CuratedStudentCheckbox
            domain="admitted_students"
            :student="student"
          />
        </td>
        <td v-if="removeStudent" class="pr-1 pt-1">
          <button
            :id="`row-${index}-remove-student-from-curated-group`"
            class="btn btn-link p-0"
            @click="curatedGroupRemoveStudent(student)"
            @keyup.enter="curatedGroupRemoveStudent(student)"
          >
            <font-awesome icon="times-circle" class="font-size-18" />
            <span class="sr-only">Remove {{ fullName(student) }}</span>
          </button>
        </td>
        <td>
          <span class="sr-only">Admitted student name</span>
          <router-link
            :id="`link-to-admit-${student.csEmplId}`"
            :aria-label="`Go to admitted student profile page of ${fullName(student)}`"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            :to="admitRoutePath(student)"
          >
            <span v-html="fullName(student)" />
          </router-link>
        </td>
        <td>
          <span class="sr-only">C S I D </span>
          <span :id="`row-${index}-cs-empl-id`" :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ getSid(student) }}</span>
        </td>
        <td>
          <span class="sr-only">S I R</span>
          <span :id="`row-${index}-current-sir`">{{ student.currentSir }}</span>
        </td>
        <td>
          <span :id="`row-${index}-special-program-cep`">
            <span class="sr-only">C E P</span>
            <span v-if="!isNilOrBlank(student.specialProgramCep)">{{ student.specialProgramCep }}</span>
            <span v-if="isNilOrBlank(student.specialProgramCep)"><span class="sr-only">No data</span></span>
          </span>
        </td>
        <td>
          <span class="sr-only">Re-entry</span>
          <span :id="`row-${index}-reentry-status`">{{ student.reentryStatus }}</span>
        </td>
        <td>
          <span :id="`row-${index}-first-generation-college`">
            <span class="sr-only">First generation</span>
            <span v-if="isNilOrBlank(student.firstGenerationCollege)">&mdash;<span class="sr-only"> No data</span></span>
            <span v-if="!isNilOrBlank(student.firstGenerationCollege)">{{ student.firstGenerationCollege }}</span>
          </span>
        </td>
        <td>
          <span class="sr-only">U R E M</span>
          <span :id="`row-${index}-urem`">{{ student.urem }}</span>
        </td>
        <td>
          <span class="sr-only">Waiver</span>
          <span :id="`row-${index}-application-fee-waiver-flag`">
            <span v-if="isNilOrBlank(student.applicationFeeWaiverFlag)">&mdash;<span class="sr-only">No data</span></span>
            <span v-if="!_isNil(student.applicationFeeWaiverFlag)">{{ student.applicationFeeWaiverFlag }}</span>
          </span>
        </td>
        <td>
          <span class="sr-only">Residency</span>
          <span :id="`row-${index}-residency-category`">{{ student.residencyCategory }}</span>
        </td>
        <td>
          <span class="sr-only">Freshman or Transfer</span>
          <span :id="`row-${index}-freshman-or-transfer`">{{ student.freshmanOrTransfer }}</span>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import Context from '@/mixins/Context'
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import Util from '@/mixins/Util'

export default {
  name: 'AdmitStudentsTable',
  components: {CuratedStudentCheckbox},
  mixins: [Context, Util],
  props: {
    includeCuratedCheckbox: {
      required: false,
      type: Boolean
    },
    removeStudent: {
      default: undefined,
      required: false,
      type: Function
    },
    students: {
      required: true,
      type: Array
    }
  },
  methods: {
    admitRoutePath(student) {
      const sid = this.getSid(student)
      return this.currentUser.inDemoMode ? `/admit/student/${window.btoa(sid)}` : `/admit/student/${sid}`
    },
    curatedGroupRemoveStudent(student) {
      this.removeStudent(this.getSid(student))
      this.alertScreenReader(`Removed ${this.fullName(student)} from group`)
    },
    fullName(student) {
      const firstName = student.firstName
      const middleName = student.middleName
      const lastName = student.lastName
      let fullName
      if (this.currentUser.preferences.admitSortBy === 'first_name') {
        fullName = this._join(this._remove([firstName, middleName, lastName]), ' ')
      } else {
        fullName = this._join(this._remove([lastName ? `${lastName},` : null, firstName, middleName]), ' ')
      }
      return fullName
    },
    getSid: student => student.csEmplId || student.sid
  }
}
</script>

<style scoped>
td {
  font-size: 14px;
}
</style>
