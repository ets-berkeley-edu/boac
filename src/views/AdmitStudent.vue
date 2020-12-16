<template>
  <div>
    <Spinner />
    <div v-if="!loading" class="m-3">
      <h1
        id="admit-name-header"
        :class="{'demo-mode-blur': $currentUser.inDemoMode}"
        class="student-section-header">
        {{ fullName }}
      </h1>
      <div v-if="admit.studentUid" class="pt-2 pb-3">
        <router-link
          :id="`link-to-student-${admit.studentUid}`"
          :to="studentRoutePath(admit.studentUid, $currentUser.inDemoMode)">
          View <span :class="{'demo-mode-blur': $currentUser.inDemoMode}" v-html="fullName"></span>'s profile page
        </router-link>
      </div>
      <AdmitDataWarning :updated-at="$_.get(admit, 'updatedAt')" />
      <table class="mb-4 table-striped">
        <caption class="sr-only">Basic information for {{ fullName }}</caption>
        <tbody>
          <tr>
            <th class="table-cell">ApplyUC CPID</th>
            <td id="admit-apply-uc-cpid" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.applyucCpid }}</td>
          </tr>
          <tr>
            <th class="table-cell">CS Empl ID</th>
            <td id="admit-sid" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.sid }}</td>
          </tr>
          <tr>
            <th class="table-cell">UID</th>
            <td id="admit-uid" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.uid }}</td>
          </tr>
          <tr>
            <th class="table-cell">Birthdate</th>
            <td id="admit-birthdate" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ birthDate }}</td>
          </tr>
          <tr>
            <th class="table-cell">Freshman or Transfer</th>
            <td id="admit.freshman-or-transfer" class="table-cell">{{ admit.freshmanOrTransfer }}</td>
          </tr>
          <tr>
            <th class="table-cell">Admit Status</th>
            <td id="admit-admit-status" class="table-cell">{{ admit.admitStatus }}</td>
          </tr>
          <tr>
            <th class="table-cell">Current SIR</th>
            <td id="admit-current-sir" class="table-cell">{{ admit.currentSir }}</td>
          </tr>
          <tr>
            <th class="table-cell">College</th>
            <td id="admit-college" class="table-cell">{{ admit.college }}</td>
          </tr>
          <tr>
            <th class="table-cell">Admit Term</th>
            <td id="admit-admit-term" class="table-cell">{{ admit.admitTerm }}</td>
          </tr>
        </tbody>
      </table>
      <table class="mb-4 table-striped">
        <caption class="sr-only">Contact information for {{ fullName }}</caption>
        <tbody>
          <tr>
            <th class="table-cell">Email</th>
            <td id="admit-email" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.email }}</td>
          </tr>
          <tr>
            <th class="table-cell">Campus Email</th>
            <td id="admit-campus-email" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.campusEmail1 }}</td>
          </tr>
          <tr>
            <th class="table-cell">Daytime Phone</th>
            <td id="admit-daytime-phone" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell">{{ admit.daytimePhone }}</td>
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
        </tbody>
      </table>
      <table class="mb-4 table-striped">
        <caption class="sr-only">Demographic information for {{ fullName }}</caption>
        <tbody>
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
            <td id="admit-x-ethnic" class="table-cell">{{ admit.xethnic }}</td>
          </tr>
          <tr>
            <th class="table-cell">Hispanic</th>
            <td id="admit-hispanic" class="table-cell">{{ admit.hispanic }}</td>
          </tr>
          <tr>
            <th class="table-cell">UREM</th>
            <td id="admit-urem" class="table-cell">{{ admit.urem }}</td>
          </tr>
          <tr>
            <th class="table-cell">Residency Category</th>
            <td id="admit-residency-category" class="table-cell">{{ admit.residencyCategory }}</td>
          </tr>
          <tr>
            <th class="table-cell">US Citizenship Status</th>
            <td id="admit-us-citizenship-status" class="table-cell">{{ admit.usCitizenshipStatus }}</td>
          </tr>
          <tr>
            <th class="table-cell">US Non Citizen Status</th>
            <td id="admit-us-non-citizen-status" class="table-cell">{{ admit.usNonCitizenStatus }}</td>
          </tr>
          <tr>
            <th class="table-cell">Citizenship Country</th>
            <td id="admit-citizenship-country" class="table-cell">{{ admit.citizenshipCountry }}</td>
          </tr>
          <tr>
            <th class="table-cell">Permanent Residence Country</th>
            <td id="admit-permanent-residence-country" class="table-cell">{{ admit.permanentResidenceCountry }}</td>
          </tr>
          <tr>
            <th class="table-cell">Non Immigrant Visa Current</th>
            <td id="admit-non-immigrant-visa-current" class="table-cell">{{ admit.nonImmigrantVisaCurrent }}</td>
          </tr>
          <tr>
            <th class="table-cell">Non Immigrant Visa Planned</th>
            <td id="admit-non-immigrant-visa-planned" class="table-cell">{{ admit.nonImmigrantVisaPlanned }}</td>
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
          <tr>
            <th class="table-cell">Highest Parent Education Level</th>
            <td id="admit-highest-parent-education-level" class="table-cell">{{ admit.highestParentEducationLevel }}</td>
          </tr>
        </tbody>
      </table>
      <table class="mb-4 table-striped">
        <caption class="sr-only">GPA and test scores for {{ fullName }}</caption>
        <tbody>
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
        </tbody>
      </table>
      <table class="mb-4 table-striped">
        <caption class="sr-only">Family and status information for {{ fullName }}</caption>
        <tbody>
          <tr>
            <th class="table-cell">Application Fee Waiver Flag</th>
            <td id="admit-application-fee-waiver-flag" class="table-cell">{{ admit.applicationFeeWaiverFlag }}</td>
          </tr>
          <tr>
            <th class="table-cell">Foster Care Flag</th>
            <td id="admit-foster-care-flag" class="table-cell">{{ admit.fosterCareFlag }}</td>
          </tr>
          <tr>
            <th class="table-cell">Family Is Single Parent</th>
            <td id="admit-family-is-single-parent" class="table-cell">{{ admit.familyIsSingleParent }}</td>
          </tr>
          <tr>
            <th class="table-cell">Student Is Single Parent</th>
            <td id="admit-student-is-single-parent" class="table-cell">{{ admit.studentIsSingleParent }}</td>
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
            <td id="admit-family-income" class="table-cell">{{ admit.familyIncome ? `$${toInt(admit.familyIncome).toLocaleString()}` : '' }}</td>
          </tr>
          <tr>
            <th class="table-cell">Student Income</th>
            <td id="admit-student-income" class="table-cell">{{ admit.studentIncome ? `$${toInt(admit.studentIncome).toLocaleString()}` : '' }}</td>
          </tr>
          <tr>
            <th class="table-cell">Is Military Dependent</th>
            <td class="table-cell">{{ admit.isMilitaryDependent }}</td>
          </tr>
          <tr>
            <th class="table-cell">Military Status</th>
            <td id="admit-military-status" class="table-cell">{{ admit.militaryStatus }}</td>
          </tr>
          <tr>
            <th class="table-cell">Re-entry Status</th>
            <td id="admit-reentry-status" class="table-cell">{{ admit.reentryStatus }}</td>
          </tr>
          <tr>
            <th class="table-cell">Athlete Status</th>
            <td id="admit-athlete-status" class="table-cell">{{ admit.athleteStatus }}</td>
          </tr>
          <tr>
            <th class="table-cell">Summer Bridge Status</th>
            <td id="admit-summer-bridge-status" class="table-cell">{{ admit.summerBridgeStatus }}</td>
          </tr>
          <tr>
            <th class="table-cell">Last School LCFF+ Flag</th>
            <td id="admit-last-school-lcff-plus-flag" class="table-cell">{{ admit.lastSchoolLcffPlusFlag }}</td>
          </tr>
          <tr>
            <th class="table-cell">Special Program - CEP</th>
            <td id="admit-special-program-cep" class="table-cell">{{ admit.specialProgramCep }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import Loading from '@/mixins/Loading'
import Scrollable from '@/mixins/Scrollable'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import { getAdmitBySid } from '@/api/admit'

export default {
  name: 'AdmitStudent',
  components: { AdmitDataWarning, Spinner },
  mixins: [Loading, Scrollable, Util],
  data: () => ({
    admit: {}
  }),
  computed: {
    birthDate() {
      let birthDate = this.$moment(this.admit.birthdate, ['YYYY-MM-DD', 'M/D/YY'])
      if (birthDate.isAfter(this.now)) {
        birthDate.subtract(100, 'years')
      }
      return birthDate.format('MMM D, YYYY')
    },
    fullName() {
      return this.$_.join(this.$_.remove([this.admit.firstName, this.admit.middleName, this.admit.lastName]), ' ')
    }
  },
  created() {
    this.now = this.$moment()
    let sid = this.$_.get(this.$route, 'params.sid')
    if (this.$currentUser.inDemoMode) {
      // In demo-mode we do not want to expose SID in browser location bar.
      sid = window.atob(sid)
    }
    getAdmitBySid(sid).then(admit => {
      if (admit) {
        this.$_.assign(this.admit, admit)
        let pageTitle = this.$currentUser.inDemoMode ? 'Admitted Student' : this.fullName
        this.setPageTitle(pageTitle)
        this.loaded(`${pageTitle} has loaded`)
      } else {
        this.$router.push({ path: '/404' })
      }
    })
  },
  mounted() {
    this.scrollToTop()
  },
}
</script>

<style scoped>
.table-cell {
  font-weight: normal;
  padding: 5px 50px 5px 3px;
  vertical-align: top;
  width: 450px;
}
</style>
