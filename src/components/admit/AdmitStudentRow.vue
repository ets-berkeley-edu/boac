<template>
  <tr>
    <td>
      <div>
        <span class="sr-only">Admitted student name</span>
        <router-link
          :id="`link-to-admit-${admitStudent.csEmplId}`"
          :aria-label="`Go to profile page of ${admitStudent.firstName} ${admitStudent.lastName}`"
          :class="{'demo-mode-blur': $currentUser.inDemoMode}"
          :to="$currentUser.inDemoMode ? `/admit/student/${window.btoa(admitStudent.csEmplId)}` : `/admit/student/${admitStudent.csEmplId}`"
          v-html="admitName"></router-link>
      </div>
    </td>
    <td>
      <div>
        <span class="sr-only">C S I D</span>
        <span :id="`row-${rowIndex}-cs-empl-id`" :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ admitStudent.csEmplId }}</span>
      </div>
    </td>
    <td>
      <div>
        <span class="sr-only">S I R</span>
        <span :id="`row-${rowIndex}-current-sir`">{{ admitStudent.currentSir }}</span>
      </div>
    </td>
    <td>
      <div>
        <span class="sr-only">C E P</span>
        <span :id="`row-${rowIndex}-special-program-cep`">{{ admitStudent.specialProgramCep }}</span>
      </div>
    </td>
    <td>
      <div>
        <span class="sr-only">Re-entry</span>
        <span :id="`row-${rowIndex}-reentry-status`">{{ admitStudent.reentryStatus }}</span>
      </div>
    </td>
    <td>
      <div>
        <span class="sr-only">First generation</span>
        <span :id="`row-${rowIndex}-first-generation-college`">{{ admitStudent.firstGenerationCollege }}</span>
      </div>
    </td>
    <td>
      <div>
        <span class="sr-only">U R E M</span>
        <span :id="`row-${rowIndex}-urem`">{{ admitStudent.urem }}</span>
      </div>
    </td>
    <td>
      <div>
        <span class="sr-only">Waiver</span>
        <span :id="`row-${rowIndex}-application-fee-waiver-flag`">{{ admitStudent.applicationFeeWaiverFlag }}</span>
      </div>
    </td>
    <td>
      <div>
        <span class="sr-only">International</span>
        <span :id="`row-${rowIndex}-residency-category`">{{ admitStudent.residencyCategory }}</span>
      </div>
    </td>
    <td>
      <div>
        <span class="sr-only">Freshman or Transfer</span>
        <span :id="`row-${rowIndex}-freshman-or-transfer`">{{ admitStudent.freshmanOrTransfer }}</span>
      </div>
    </td>
  </tr>
</template>

<script>
export default {
  name: 'AdmitStudentRow',
  props: {
    rowIndex: {
      required: true,
      type: Number
    },
    sortedBy: {
      required: true,
      type: String
    },
    admitStudent: {
      required: true,
      type: Object
    }
  },
  computed: {
    admitName() {
      if (this.sortedBy === 'first_name') {
        return `${this.admitStudent.firstName} ${this.admitStudent.lastName}`;
      }
      return `${this.admitStudent.lastName}, ${this.admitStudent.firstName}`;
    }
  }
}
</script>