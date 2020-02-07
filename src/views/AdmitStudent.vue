<template>
  <div>
    <Spinner alert-prefix="Admit profile" />
    <div v-if="!loading" class="m-3">
      <h1
        id="admit-name-header"
        ref="pageHeader"
        :class="{'demo-mode-blur': $currentUser.inDemoMode}"
        class="student-section-header"
        tabindex="0">
        {{ admit.firstName }}&nbsp;{{ admit.lastName }}
      </h1>
      <table class="mb-4">
        <caption class="sr-only">Basic information for {{ admit.firstName }} {{ admit.lastName }}</caption>
        <tr>
          <th class="table-cell">ApplyUC CPID</th>
          <td id="admit-apply-uc-cpid" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.applyucCpid }}</td>
        </tr>
        <tr>
          <th class="table-cell">CS Empl ID</th>
          <td id="admit-sid" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.sid }}</td>
        </tr>
        <tr>
          <th class="table-cell">Birthdate</th>
          <td id="admit-birthdate" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.birthdate | moment('MMM D, YYYY') }}</td>
        </tr>
        <tr>
          <th class="table-cell">Freshman or Transfer</th>
          <td id="admit.freshman-or-transfer" class="table-cell">{{ admit.freshmanOrTransfer }}</td>
        </tr>
        <tr>
          <th class="table-cell">Admit Status</th>
          <td v-if="admit.admitStatus" id="admit-admit-status" class="table-cell">
            <font-awesome v-if="toBoolean(admit.admitStatus)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.admitStatus)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.admitStatus }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">Current SIR</th>
          <td v-if="admit.currentSir" id="admit-current-sir" class="table-cell">
            <font-awesome v-if="toBoolean(admit.currentSir)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.currentSir)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.currentSir }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">College</th>
          <td id="admit-college" class="table-cell">{{ admit.college }}</td>
        </tr>
      </table>
      <table class="mb-4">
        <caption class="sr-only">Contact information for {{ admit.firstName }} {{ admit.lastName }}</caption>
        <tr>
          <th class="table-cell">Email</th>
          <td id="admit-email" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.email }}</td>
        </tr>
        <tr>
          <th class="table-cell">Daytime</th>
          <td id="admit-daytime" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.daytime }}</td>
        </tr>
        <tr>
          <th class="table-cell">Mobile</th>
          <td id="admit-mobile" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.mobile }}</td>
        </tr>
        <tr>
          <th class="table-cell">Address</th>
          <td :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">
            <div id="admit-permanent-street-1">{{ admit.permanentStreet1 }}</div>
            <div id="admit-permanent-street-2">{{ admit.permanentStreet2 }}</div>
            <div id="admit-permanent-city-region-postal">{{ admit.permanentCity }}, {{ admit.permanentRegion }}  {{ admit.permanentPostal }}</div>
            <div id="admit-permanent-country">{{ admit.permanentCountry }}</div>
          </td>
        </tr>
      </table>
      <table class="mb-4">
        <caption class="sr-only">Demographic information for {{ admit.firstName }} {{ admit.lastName }}</caption>
        <tr>
          <th class="table-cell">Sex</th>
          <td id="admit-sex" class="table-cell">{{ admit.sex }}</td>
        </tr>
        <tr>
          <th class="table-cell">Gender Identity</th>
          <td id="admit-gender-identity" class="table-cell">{{ admit.genderIdentity }}</td>
        </tr>
        <tr>
          <th class="table-cell">XEthnic</th>
          <td id="admit-x-ethnic" class="table-cell">{{ admit.xEthnic }}</td>
        </tr>
        <tr>
          <th class="table-cell">Hispanic</th>
          <td id="admit-hispanic" class="table-cell">{{ admit.hispanic }}</td>
        </tr>
        <tr>
          <th class="table-cell">UREM</th>
          <td id="admit-urem" class="table-cell">{{ admit.Urem }}</td>
        </tr>
        <tr>
          <th class="table-cell">First Generation Student</th>
          <td id="admit-first-generation-student" class="table-cell">{{ admit.firstGenerationStudent }}</td>
        </tr>
        <tr>
          <th class="table-cell">First Generation College</th>
          <td id="admit-first-generation-college" class="table-cell">{{ admit.firstGenerationCollege }}</td>
        </tr>
        <tr>
          <th class="table-cell">Parent 1 Education Level</th>
          <td id="admit-parent-1-education-level" class="table-cell">{{ admit.parent1EducationLevel }}</td>
        </tr>
        <tr>
          <th class="table-cell">Parent 2 Education Level</th>
          <td id="admit-parent-2-education-level" class="table-cell">{{ admit.parent2EducationLevel }}</td>
        </tr>
      </table>
      <table class="mb-4">
        <caption class="sr-only">GPA and test scores for {{ admit.firstName }} {{ admit.lastName }}</caption>
        <tr>
          <th
            id="admit-gpa"
            class="table-cell"
            colspan="2"
            scope="colgroup">
            GPA
          </th>
        </tr>
        <tr>
          <th id="admit-gpa-hs-unweighted-th" class="table-cell pl-4">HS Unweighted GPA</th>
          <td id="admit-gpa-hs-unweighted" class="table-cell" headers="admit-gpa admit-gpa-hs-unweighted-th">{{ admit.hsUnweightedGpa }}</td>
        </tr>
        <tr>
          <th id="admit-gpa-hs-weighted-th" class="table-cell pl-4">HS Weighted GPA</th>
          <td id="admit-gpa-hs-weighted" class="table-cell" headers="admit-gpa admit-gpa-hs-weighted-th">{{ admit.hsWeightedGpa }}</td>
        </tr>
        <tr>
          <th id="admit-gpa-transfer-th" class="table-cell pl-4">Transfer GPA</th>
          <td id="admit-gpa-transfer" class="table-cell" headers="admit-gpa admit-gpa-transfer-th">{{ admit.transferGpa }}</td>
        </tr>
        <tr>
          <th
            id="admit-act"
            class="table-cell"
            colspan="2"
            scope="colgroup">
            ACT
          </th>
        </tr>
        <tr>
          <th id="admit-act-composite-th" class="table-cell pl-4">Composite</th>
          <td id="admit-act-composite" class="table-cell" headers="admit-act admit-act-composite-th">{{ admit.actComposite }}</td>
        </tr>
        <tr>
          <th id="admit-act-math-th" class="table-cell pl-4">Math</th>
          <td id="admit-act-math" class="table-cell" headers="admit-act admit-act-math-th">{{ admit.actMath }}</td>
        </tr>
        <tr>
          <th id="admit-act-english-th" class="table-cell pl-4">English</th>
          <td id="admit-act-english" class="table-cell" headers="admit-act admit-act-english-th">{{ admit.actEnglish }}</td>
        </tr>
        <tr>
          <th id="admit-act-reading-th" class="table-cell pl-4">Reading</th>
          <td id="admit-act-reading" class="table-cell" headers="admit-act admit-act-reading-th">{{ admit.actReading }}</td>
        </tr>
        <tr>
          <th id="admit-act-writing-th" class="table-cell pl-4">Writing</th>
          <td id="admit-act-writing" class="table-cell" headers="admit-act admit-act-writing-th">{{ admit.actWriting }}</td>
        </tr>
        <tr>
          <th
            id="admit-sat"
            class="table-cell"
            colspan="2"
            scope="colgroup">
            SAT
          </th>
        </tr>
        <tr>
          <th id="admit-sat-total-th" class="table-cell pl-4">Total</th>
          <td id="admit-sat-total" class="table-cell" headers="admit-sat admit-sat-total-th">{{ admit.satTotal }}</td>
        </tr>
        <tr>
          <th id="admit-sat-evidence-th" class="table-cell pl-4">Evidence-Based Reading and Writing Section</th>
          <td id="admit-sat-evidence" class="table-cell" headers="admit-sat admit-sat-evidence-th">{{ admit.satREvidenceBasedRwSection }}</td>
        </tr>
        <tr>
          <th id="admit-sat-math-th" class="table-cell pl-4">Math</th>
          <td id="admit-sat-math" class="table-cell" headers="admit-sat admit-sat-math-th">{{ admit.satRMathSection }}</td>
        </tr>
        <tr>
          <th id="admit-sat-reading-th" class="table-cell pl-4">Essay - Reading</th>
          <td id="admit-sat-reading" class="table-cell" headers="admit-sat admit-sat-reading-th">{{ admit.satREssayReading }}</td>
        </tr>
        <tr>
          <th id="admit-sat-analysis-th" class="table-cell pl-4">Essay - Analysis</th>
          <td id="admit-sat-analysis" class="table-cell" headers="admit-sat admit-sat-analysis-th">{{ admit.satREssayAnalysis }}</td>
        </tr>
        <tr>
          <th id="admit-sat-writing-th" class="table-cell pl-4">Writing</th>
          <td id="admit-sat-writing" class="table-cell" headers="admit-sat admit-sat-writing-th">{{ admit.satREssayWriting }}</td>
        </tr>
      </table>
      <table class="mb-4">
        <caption class="sr-only">Family and status information for {{ admit.firstName }} {{ admit.lastName }}</caption>
        <tr>
          <th class="table-cell">Application Fee Waiver Flag</th>
          <td v-if="admit.applicationFeeWaiverFlag" id="admit-application-fee-waiver-flag" class="table-cell">
            <font-awesome v-if="toBoolean(admit.applicationFeeWaiverFlag)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.applicationFeeWaiverFlag)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.applicationFeeWaiverFlag }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">Foster Care Flag</th>
          <td v-if="admit.fosterCareFlag" id="admit-foster-care-flag" class="table-cell">
            <font-awesome v-if="toBoolean(admit.fosterCareFlag)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.fosterCareFlag)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.fosterCareFlag }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">Family Is Single Parent</th>
          <td v-if="admit.familyIsSingleParent" id="admit-family-is-single-parent" class="table-cell">
            <font-awesome v-if="toBoolean(admit.familyIsSingleParent)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.familyIsSingleParent)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.familyIsSingleParent }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">Student Is Single Parent</th>
          <td v-if="admit.studentIsSingleParent" id="admit-student-is-single-parent" class="table-cell">
            <font-awesome v-if="toBoolean(admit.studentIsSingleParent)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.studentIsSingleParent)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.studentIsSingleParent }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">Family Dependents No.</th>
          <td id="admit-family-dependents-num" class="table-cell">{{ admit.familyDependentsNum }}</td>
        </tr>
        <tr>
          <th class="table-cell">Student Dependents No.</th>
          <td id="admit-student-dependents-num" class="table-cell">{{ admit.studentDependentsNum }}</td>
        </tr>
        <tr>
          <th class="table-cell">Family Income</th>
          <td v-if="admit.familyIncome" id="admit-family-income" class="table-cell">{{ `$${toInt(admit.familyIncome).toLocaleString()}` }}</td>
        </tr>
        <tr>
          <th class="table-cell">Student Income</th>
          <td v-if="admit.studentIncome" id="admit-student-income" class="table-cell">{{ `$${toInt(admit.studentIncome).toLocaleString()}` }}</td>
        </tr>
        <tr>
          <th class="table-cell">Is Military Dependent</th>
          <td v-if="admit.isMilitaryDependent" class="table-cell">
            <font-awesome v-if="toBoolean(admit.isMilitaryDependent)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.isMilitaryDependent)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.isMilitaryDependent }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">Military Status</th>
          <td v-if="admit.militaryStatus" id="admit-military-status" class="table-cell">
            <font-awesome v-if="toBoolean(admit.militaryStatus)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.militaryStatus)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.militaryStatus }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">Re-entry Status</th>
          <td v-if="admit.reentryStatus" id="admit-reentry-status" class="table-cell">
            <font-awesome v-if="toBoolean(admit.reentryStatus)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.reentryStatus)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.reentryStatus }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">Athlete Status</th>
          <td v-if="admit.athleteStatus" id="admit-athlete-status" class="table-cell">
            <font-awesome v-if="toBoolean(admit.athleteStatus)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.athleteStatus)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.athleteStatus }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">Summer Bridge Status</th>
          <td v-if="admit.summerBridgeStatus" id="admit-summer-bridge-status" class="table-cell">
            <font-awesome v-if="toBoolean(admit.summerBridgeStatus)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.summerBridgeStatus)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.summerBridgeStatus }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">Last School LCFF+ Flag</th>
          <td v-if="admit.lastSchoolLcffPlusFlag" id="admit-last-school-lcff-plus-flag" class="table-cell">
            <font-awesome v-if="toBoolean(admit.lastSchoolLcffPlusFlag)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.lastSchoolLcffPlusFlag)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.lastSchoolLcffPlusFlag }}
          </td>
        </tr>
        <tr>
          <th class="table-cell">Special Program - CEP</th>
          <td v-if="admit.specialProgramCep" id="admit-special-program-cep" class="table-cell">
            <font-awesome v-if="toBoolean(admit.specialProgramCep)" icon="check-circle" class="boolean-true-icon" />
            <font-awesome v-if="!toBoolean(admit.specialProgramCep)" :icon="['far', 'circle']" class="boolean-false-icon" />
            {{ admit.specialProgramCep }}
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
import Loading from '@/mixins/Loading.vue';
import Util from '@/mixins/Util';
import Spinner from '@/components/util/Spinner';
import { getAdmitBySid } from '@/api/admit';

export default {
  name: 'AdmitStudent',
  components: { Spinner },
  mixins: [Loading, Util],
  data: () => ({
    admit: {}
  }),
  created() {
    let sid = this.get(this.$route, 'params.sid');
    if (this.$currentUser.inDemoMode) {
      // In demo-mode we do not want to expose SID in browser location bar.
      sid = window.atob(sid);
    }
    getAdmitBySid(sid).then(admit => {
      if (admit) {
        this.setPageTitle(this.$currentUser.inDemoMode ? 'Admitted Student' : admit.name);
        this.assign(this.admit, admit);
        this.loaded(this.admit);
      } else {
        this.$router.push({ path: '/404' });
      }
    })
    
  },
  methods: {
    toBoolean(word) {
      return word === 'Yes' || word === 'T';
    }
  }
}
</script>

<style scoped>
.boolean-false-icon {
  color: grey;
}
.boolean-true-icon {
  color: #00c13a;
}
.table-cell {
  font-weight: normal;
  padding: 5px 50px 5px 0;
  vertical-align: top;
  width: 450px;
}
</style>
