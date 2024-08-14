<template>
  <table id="cohort-admitted-students" class="w-100">
    <thead>
      <tr>
        <th v-if="includeCuratedCheckbox || removeStudent"></th>
        <th class="vertical-bottom">Name</th>
        <th class="text-no-wrap vertical-bottom">CS ID</th>
        <th class="vertical-bottom">SIR</th>
        <th class="vertical-bottom">CEP</th>
        <th class="pr-2 text-no-wrap vertical-bottom">Re-entry</th>
        <th class="pr-2 text-no-wrap vertical-bottom">1st Gen</th>
        <th class="pr-2 vertical-bottom">UREM</th>
        <th class="vertical-bottom">Waiver</th>
        <th class="pr-2 text-no-wrap vertical-bottom">INT'L</th>
        <th class="vertical-bottom">Freshman or Transfer</th>
      </tr>
    </thead>
    <tbody class="font-size-14">
      <tr
        v-for="(student, index) in students"
        :id="`admit-${getSid(student)}`"
        :key="index"
      >
        <td v-if="includeCuratedCheckbox" class="pa-1">
          <CuratedStudentCheckbox
            domain="admitted_students"
            :student="student"
          />
        </td>
        <td v-if="removeStudent" class="pr-3 py-1">
          <v-btn
            :id="`row-${index}-remove-student-from-curated-group`"
            density="compact"
            :icon="true"
            variant="text"
            @click="curatedGroupRemoveStudent(student)"
            @keyup.enter="curatedGroupRemoveStudent(student)"
          >
            <v-icon :icon="mdiCloseCircle" size="22" color="primary" />
            <span class="sr-only">Remove {{ fullName(student) }}</span>
          </v-btn>
        </td>
        <td class="pa-1">
          <span class="sr-only">Admitted student name</span>
          <router-link
            :id="`link-to-admit-${student.csEmplId}`"
            :aria-label="`Go to admitted student profile page of ${fullName(student)}`"
            :class="{'demo-mode-blur': get(useContextStore().currentUser, 'inDemoMode')}"
            :to="admitRoutePath(student)"
          >
            <span v-html="fullName(student)" />
          </router-link>
        </td>
        <td class="pr-3">
          <span class="sr-only">C S I D <span aria-hidden="true">&nbsp;</span></span>
          <span :id="`row-${index}-cs-empl-id`" :class="{'demo-mode-blur': get(useContextStore().currentUser, 'inDemoMode')}">{{ getSid(student) }}</span>
        </td>
        <td class="pr-2">
          <span class="sr-only">S I R</span>
          <span :id="`row-${index}-current-sir`">{{ student.currentSir }}</span>
        </td>
        <td class="pr-2">
          <span :id="`row-${index}-special-program-cep`">
            <span class="sr-only">C E P</span>
            <span v-if="!isNilOrBlank(student.specialProgramCep)">{{ student.specialProgramCep }}</span>
            <span v-if="isNilOrBlank(student.specialProgramCep)"><span class="sr-only">No data</span></span>
          </span>
        </td>
        <td class="pa-1">
          <span class="sr-only">Re-entry</span>
          <span :id="`row-${index}-reentry-status`">{{ student.reentryStatus }}</span>
        </td>
        <td class="pa-1">
          <span :id="`row-${index}-first-generation-college`">
            <span class="sr-only">First generation</span>
            <span v-if="isNilOrBlank(student.firstGenerationCollege)">&mdash;<span class="sr-only"> No data</span></span>
            <span v-if="!isNilOrBlank(student.firstGenerationCollege)">{{ student.firstGenerationCollege }}</span>
          </span>
        </td>
        <td class="pa-1">
          <span class="sr-only">U R E M</span>
          <span :id="`row-${index}-urem`">{{ student.urem }}</span>
        </td>
        <td class="pa-1">
          <span class="sr-only">Waiver</span>
          <span :id="`row-${index}-application-fee-waiver-flag`">
            <span v-if="isNilOrBlank(student.applicationFeeWaiverFlag)">&mdash;<span class="sr-only">No data</span></span>
            <span v-if="!isNil(student.applicationFeeWaiverFlag)">{{ student.applicationFeeWaiverFlag }}</span>
          </span>
        </td>
        <td class="pa-1">
          <span class="sr-only">Residency</span>
          <span :id="`row-${index}-residency-category`">{{ student.residencyCategory }}</span>
        </td>
        <td class="pa-1">
          <span class="sr-only">Freshman or Transfer</span>
          <span :id="`row-${index}-freshman-or-transfer`">{{ student.freshmanOrTransfer }}</span>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
import {mdiCloseCircle} from '@mdi/js'
import {get, isNil, join, remove} from 'lodash'
import {isNilOrBlank} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
</script>

<script>
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import {alertScreenReader} from '@/lib/utils'

export default {
  name: 'AdmitStudentsTable',
  components: {CuratedStudentCheckbox},
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
      return get(useContextStore().currentUser, 'inDemoMode') ? `/admit/student/${window.btoa(sid)}` : `/admit/student/${sid}`
    },
    curatedGroupRemoveStudent(student) {
      this.removeStudent(this.getSid(student))
      alertScreenReader(`Removed ${this.fullName(student)} from group`)
    },
    fullName(student) {
      const firstName = student.firstName
      const middleName = student.middleName
      const lastName = student.lastName
      let fullName
      if (get(useContextStore().currentUser, 'preferences.admitSortBy') === 'first_name') {
        fullName = join(remove([firstName, middleName, lastName]), ' ')
      } else {
        fullName = join(remove([lastName ? `${lastName},` : null, firstName, middleName]), ' ')
      }
      return fullName
    },
    getSid: student => student.csEmplId || student.sid
  }
}
</script>
