<template>
  <tr>
    <td v-if="removeStudent" class="pr-1 pt-1">
      <button
        :id="`row-${rowIndex}-remove-student-from-curated-group`"
        class="btn btn-link p-0"
        @click="onClickRemoveStudent"
        @keyup.enter="onClickRemoveStudent"
      >
        <font-awesome icon="times-circle" class="font-size-18" />
        <span class="sr-only">Remove {{ student.firstName }} {{ student.lastName }}</span>
      </button>
    </td>
    <td>
      <span class="sr-only">Admitted student name</span>
      <router-link
        :id="`link-to-admit-${sid}`"
        :aria-label="`Go to admitted student profile page of ${fullName}`"
        :class="{'demo-mode-blur': $currentUser.inDemoMode}"
        :to="admitRoutePath()"
        v-html="fullName"
      />
    </td>
    <td>
      <span class="sr-only">C S I D </span>
      <span :id="`row-${rowIndex}-cs-empl-id`" :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ sid }}</span>
    </td>
    <td>
      <span class="sr-only">S I R</span>
      <span :id="`row-${rowIndex}-current-sir`">{{ student.currentSir }}</span>
    </td>
    <td>
      <span :id="`row-${rowIndex}-special-program-cep`">
        <span class="sr-only">C E P</span>
        <span v-if="!isNilOrBlank(student.specialProgramCep)">{{ student.specialProgramCep }}</span>
        <span v-if="isNilOrBlank(student.specialProgramCep)"><span class="sr-only">No data</span></span>
      </span>
    </td>
    <td>
      <span class="sr-only">Re-entry</span>
      <span :id="`row-${rowIndex}-reentry-status`">{{ student.reentryStatus }}</span>
    </td>
    <td>
      <span :id="`row-${rowIndex}-first-generation-college`">
        <span class="sr-only">First generation</span>
        <span v-if="isNilOrBlank(student.firstGenerationCollege)">&mdash;<span class="sr-only"> No data</span></span>
        <span v-if="!isNilOrBlank(student.firstGenerationCollege)">{{ student.firstGenerationCollege }}</span>
      </span>
    </td>
    <td>
      <span class="sr-only">U R E M</span>
      <span :id="`row-${rowIndex}-urem`">{{ student.urem }}</span>
    </td>
    <td>
      <span class="sr-only">Waiver</span>
      <span :id="`row-${rowIndex}-application-fee-waiver-flag`">
        <span v-if="isNilOrBlank(student.applicationFeeWaiverFlag)">&mdash;<span class="sr-only">No data</span></span>
        <span v-if="!$_.isNil(student.applicationFeeWaiverFlag)">{{ student.applicationFeeWaiverFlag }}</span>
      </span>
    </td>
    <td>
      <span class="sr-only">Residency</span>
      <span :id="`row-${rowIndex}-residency-category`">{{ student.residencyCategory }}</span>
    </td>
    <td>
      <span class="sr-only">Freshman or Transfer</span>
      <span :id="`row-${rowIndex}-freshman-or-transfer`">{{ student.freshmanOrTransfer }}</span>
    </td>
  </tr>
</template>

<script>
import Util from '@/mixins/Util'

export default {
  name: 'AdmitStudentRow',
  mixins: [Util],
  props: {
    removeStudent: {
      default: undefined,
      required: false,
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
    }
  },
  data: () => ({
    sid: undefined
  }),
  computed: {
    fullName() {
      if (this.sortedBy === 'first_name') {
        return this.$_.join(this.$_.remove([this.student.firstName, this.student.middleName, this.student.lastName]), ' ')
      }
      const lastName = this.student.lastName ? `${this.student.lastName},` : null
      return this.$_.join(this.$_.remove([lastName, this.student.firstName, this.student.middleName]), ' ')
    }
  },
  created() {
    this.sid = this.student.csEmplId || this.student.sid
  },
  methods: {
    admitRoutePath() {
      return this.$currentUser.inDemoMode ? `/admit/student/${window.btoa(this.sid)}` : `/admit/student/${this.sid}`
    },
    onClickRemoveStudent() {
      this.removeStudent(this.sid)
      this.$announcer.set(`Removed ${this.student.firstName} ${this.student.lastName} from group`, 'polite')
    }
  }
}
</script>

<style scoped>
td {
  font-size: 14px;
}
</style>
