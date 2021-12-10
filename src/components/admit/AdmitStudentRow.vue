<template>
  <tr>
    <td>
      <div>
        <span class="sr-only">Admitted student name</span>
        <router-link
          :id="`link-to-admit-${sid}`"
          :aria-label="`Go to admitted student profile page of ${fullName}`"
          :class="{'demo-mode-blur': $currentUser.inDemoMode}"
          :to="admitRoutePath()"
          v-html="fullName"
        ></router-link>
      </div>
    </td>
    <td>
      <div>
        <span class="sr-only">C S I D</span>
        <span :id="`row-${rowIndex}-cs-empl-id`" :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ sid }}</span>
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
        <span
          v-if="admitStudent.specialProgramCep === '' || $_.isNil(admitStudent.specialProgramCep)"
          :id="`row-${rowIndex}-special-program-cep`"
        ><span class="sr-only">No data</span></span>

        <span
          v-if="!$_.isNil(admitStudent.specialProgramCep)"
          :id="`row-${rowIndex}-special-program-cep`"
        >{{ admitStudent.specialProgramCep }}</span>
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
        <span
          v-if="admitStudent.firstGenerationCollege === '' || $_.isNil(admitStudent.firstGenerationCollege)"
          :id="`row-${rowIndex}-first-generation-college`"
        >&mdash;<span class="sr-only">No data</span></span>

        <span
          v-if="!$_.isNil(admitStudent.firstGenerationCollege)"
          :id="`row-${rowIndex}-first-generation-college`"
        >{{ admitStudent.firstGenerationCollege }}</span>
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
        <span
          v-if="admitStudent.applicationFeeWaiverFlag === '' || $_.isNil(admitStudent.applicationFeeWaiverFlag)"
          :id="`row-${rowIndex}-application-fee-waiver-flag`"
        >&mdash;<span class="sr-only">No data</span></span>

        <span
          v-if="!$_.isNil(admitStudent.applicationFeeWaiverFlag)"
          :id="`row-${rowIndex}-application-fee-waiver-flag`"
        >{{ admitStudent.applicationFeeWaiverFlag }}</span>
      </div>
    </td>
    <td>
      <div>
        <span class="sr-only">Residency</span>
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
import Util from '@/mixins/Util'

export default {
  name: 'AdmitStudentRow',
  mixins: [Util],
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
  data: () => ({
    sid: undefined
  }),
  computed: {
    fullName() {
      if (this.sortedBy === 'first_name') {
        return this.$_.join(this.$_.remove([this.admitStudent.firstName, this.admitStudent.middleName, this.admitStudent.lastName]), ' ')
      }
      const lastName = this.admitStudent.lastName ? `${this.admitStudent.lastName},` : null
      return this.$_.join(this.$_.remove([lastName, this.admitStudent.firstName, this.admitStudent.middleName]), ' ')
    }
  },
  created() {
    this.sid = this.admitStudent.csEmplId || this.admitStudent.sid
  },
  methods: {
    admitRoutePath() {
      return this.$currentUser.inDemoMode ? `/admit/student/${window.btoa(this.sid)}` : `/admit/student/${this.sid}`
    }
  }
}
</script>