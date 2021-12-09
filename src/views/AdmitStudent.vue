<template>
  <div>
    <Spinner />
    <div v-if="!loading" class="m-3">
      <h1
        id="admit-name-header"
        :class="{'demo-mode-blur': $currentUser.inDemoMode}"
        class="student-section-header"
      >
        {{ fullName }}
      </h1>
      <div class="d-flex justify-content-between">
        <div>
          <div v-if="admit.studentUid" class="pt-2 pb-3">
            <router-link
              :id="`link-to-student-${admit.studentUid}`"
              :to="studentRoutePath(admit.studentUid, $currentUser.inDemoMode)"
            >
              View <span :class="{'demo-mode-blur': $currentUser.inDemoMode}" v-html="fullName"></span>'s profile page
            </router-link>
          </div>
        </div>
        <div>
          <ManageStudent domain="admitted_students" :student="admit" />
        </div>
      </div>
      <AdmitDataWarning :updated-at="$_.get(admit, 'updatedAt')" />

      <b-container fluid>
        <b-row>
          <b-col>
            <b-row>
              <b-col>
                <caption class="sr-only">Academic Details</caption>
                <b-row>
                  <b-col class="table-cell">
                    <h2>Academic Details</h2>
                  </b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">ApplyUC CPID</b-col>
                  <b-col id="admit-apply-uc-cpid" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.applyucCpid }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">CS Empl ID</b-col>
                  <b-col id="admit-sid" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.sid }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Birthdate</b-col>
                  <b-col id="admit-birthdate" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell font-italic">{{ birthDate }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Freshman or Transfer</b-col>
                  <b-col id="admit.freshman-or-transfer" class="table-cell font-italic">{{ admit.freshmanOrTransfer }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Admit Status</b-col>
                  <b-col id="admit-admit-status" class="table-cell font-italic">{{ admit.admitStatus }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Current SIR</b-col>
                  <b-col id="admit-current-sir" class="table-cell font-italic">{{ admit.currentSir }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">College</b-col>
                  <b-col id="admit-college" class="table-cell font-italic">{{ admit.college }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Admit Term</b-col>
                  <b-col id="admit-admit-term" class="table-cell font-italic">{{ admit.admitTerm }}</b-col>
                </b-row>
              </b-col>
              <b-col>
                <caption class="sr-only">Eligibility Details</caption>
                <b-row>
                  <b-col class="table-cell">
                    <h2>Eligibility Details</h2>
                  </b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Application Fee Waiver Flag</b-col>
                  <b-col id="admit-application-fee-waiver-flag" class="table-cell font-italic">{{ admit.applicationFeeWaiverFlag }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Family Income</b-col>
                  <b-col id="admit-family-income" class="table-cell font-italic">{{ admit.familyIncome ? `$${toInt(admit.familyIncome).toLocaleString()}` : '' }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Student Income</b-col>
                  <b-col id="admit-student-income" class="table-cell font-italic">{{ admit.studentIncome ? `$${toInt(admit.studentIncome).toLocaleString()}` : '' }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">First Generation College</b-col>
                  <b-col id="admit-first-generation-college" class="table-cell font-italic">{{ admit.firstGenerationCollege }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Parent 1 Education Level</b-col>
                  <b-col id="admit-parent-1-education-level" class="table-cell font-italic">{{ admit.parent1EducationLevel }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Parent 2 Education Level</b-col>
                  <b-col id="admit-parent-2-education-level" class="table-cell font-italic">{{ admit.parent2EducationLevel }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Highest Parent Education Level</b-col>
                  <b-col id="admit-highest-parent-education-level" class="table-cell font-italic">{{ admit.highestParentEducationLevel }}</b-col>
                </b-row>
              </b-col>
            </b-row>
          </b-col>
        </b-row>

        <hr class="table-separator" />

        <b-row>
          <b-col>
            <b-row>
              <b-col>
                <caption class="sr-only">Demographic Information</caption>
                <b-row>
                  <b-col class="table-cell">
                    <h2>Demographic Information</h2>
                  </b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Gender Identity</b-col>
                  <b-col id="admit-gender-identity" class="table-cell font-italic">{{ admit.genderIdentity }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">XEthnic</b-col>
                  <b-col id="admit-x-ethnic" class="table-cell font-italic">{{ admit.xethnic }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Hispanic</b-col>
                  <b-col id="admit-hispanic" class="table-cell font-italic">{{ admit.hispanic }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">UREM</b-col>
                  <b-col id="admit-urem" class="table-cell font-italic">{{ admit.urem }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Residency Category</b-col>
                  <b-col id="admit-residency-category" class="table-cell font-italic">{{ admit.residencyCategory }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">US Citizenship Status</b-col>
                  <b-col id="admit-us-citizenship-status" class="table-cell font-italic">{{ admit.usCitizenshipStatus }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">US Non Citizen Status</b-col>
                  <b-col id="admit-us-non-citizen-status" class="table-cell font-italic">{{ admit.usNonCitizenStatus }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Citizenship Country</b-col>
                  <b-col id="admit-citizenship-country" class="table-cell font-italic">{{ admit.citizenshipCountry }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Permanent Residence Country</b-col>
                  <b-col id="admit-permanent-residence-country" class="table-cell font-italic">{{ admit.permanentResidenceCountry }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Non Immigrant Visa Current</b-col>
                  <b-col id="admit-non-immigrant-visa-current" class="table-cell font-italic">{{ admit.nonImmigrantVisaCurrent }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Non Immigrant Visa Planned</b-col>
                  <b-col id="admit-non-immigrant-visa-planned" class="table-cell font-italic">{{ admit.nonImmigrantVisaPlanned }}</b-col>
                </b-row>
              </b-col>
              <b-col>
                <caption class="sr-only">Family and Status Information</caption>
                <b-row>
                  <b-col class="table-cell">
                    <h2>Family and Status Information</h2>
                  </b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Foster Care Flag</b-col>
                  <b-col id="admit-foster-care-flag" class="table-cell font-italic">{{ admit.fosterCareFlag }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Family Is Single Parent</b-col>
                  <b-col id="admit-family-is-single-parent" class="table-cell font-italic">{{ admit.familyIsSingleParent }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Student Is Single Parent</b-col>
                  <b-col id="admit-student-is-single-parent" class="table-cell font-italic">{{ admit.studentIsSingleParent }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Family Dependents No.</b-col>
                  <b-col id="admit-family-dependents-num" class="table-cell font-italic">{{ admit.familyDependentsNum }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Student Dependents No.</b-col>
                  <b-col id="admit-student-dependents-num" class="table-cell font-italic">{{ admit.studentDependentsNum }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Is Military Dependent</b-col>
                  <b-col class="table-cell font-italic">{{ admit.isMilitaryDependent }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Military Status</b-col>
                  <b-col id="admit-military-status" class="table-cell font-italic">{{ admit.militaryStatus }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Re-entry Status</b-col>
                  <b-col id="admit-reentry-status" class="table-cell font-italic">{{ admit.reentryStatus }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Athlete Status</b-col>
                  <b-col id="admit-athlete-status" class="table-cell font-italic">{{ admit.athleteStatus }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Summer Bridge Status</b-col>
                  <b-col id="admit-summer-bridge-status" class="table-cell font-italic">{{ admit.summerBridgeStatus }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Last School LCFF+ Flag</b-col>
                  <b-col id="admit-last-school-lcff-plus-flag" class="table-cell font-italic">{{ admit.lastSchoolLcffPlusFlag }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Special Program - CEP</b-col>
                  <b-col id="admit-special-program-cep" class="table-cell font-italic">{{ admit.specialProgramCep }}</b-col>
                </b-row>
              </b-col>
            </b-row>
          </b-col>
        </b-row>

        <hr class="table-separator" />

        <b-row>
          <b-col>
            <b-row>
              <b-col>
                <caption class="sr-only">Contact Information</caption>
                <b-row>
                  <b-col class="table-cell font-weight-bold">
                    <h2>Contact Information</h2>
                  </b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Email</b-col>
                  <b-col id="admit-email" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.email }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Campus Email</b-col>
                  <b-col id="admit-campus-email" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.campusEmail1 }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Daytime Phone</b-col>
                  <b-col id="admit-daytime-phone" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.daytimePhone }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Mobile</b-col>
                  <b-col id="admit-mobile" :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.mobile }}</b-col>
                </b-row>
                <b-row>
                  <b-col class="table-cell">Address</b-col>
                  <b-col :class="{'demo-mode-blur': $currentUser.inDemoMode}" class="table-cell font-italic">
                    <div id="admit-permanent-street-1">{{ admit.permanentStreet1 }}</div>
                    <div id="admit-permanent-street-2">{{ admit.permanentStreet2 }}</div>
                    <div id="admit-permanent-city-region-postal">{{ admit.permanentCity }}, {{ admit.permanentRegion }}  {{ admit.permanentPostal }}</div>
                    <div id="admit-permanent-country">{{ admit.permanentCountry }}</div>
                  </b-col>
                </b-row>
              </b-col>
              <b-col>
                <caption class="sr-only">GPA</caption>
                <b-row>
                  <b-col class="table-cell font-weight-bold">
                    <h2>GPA</h2>
                  </b-col>
                </b-row>
                <b-row>
                  <b-col id="admit-gpa-hs-unweighted-th" class="table-cell">HS Unweighted GPA</b-col>
                  <b-col id="admit-gpa-hs-unweighted" class="table-cell font-italic" headers="admit-gpa admit-gpa-hs-unweighted-th">{{ admit.hsUnweightedGpa }}</b-col>
                </b-row>
                <b-row>
                  <b-col id="admit-gpa-hs-weighted-th" class="table-cell">HS Weighted GPA</b-col>
                  <b-col id="admit-gpa-hs-weighted" class="table-cell font-italic" headers="admit-gpa admit-gpa-hs-weighted-th">{{ admit.hsWeightedGpa }}</b-col>
                </b-row>
                <b-row>
                  <b-col id="admit-gpa-transfer-th" class="table-cell">Transfer GPA</b-col>
                  <b-col id="admit-gpa-transfer" class="table-cell font-italic" headers="admit-gpa admit-gpa-transfer-th">{{ admit.transferGpa }}</b-col>
                </b-row>
              </b-col>
            </b-row>
          </b-col>
        </b-row>
      </b-container>
    </div>
  </div>
</template>

<script>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import Loading from '@/mixins/Loading'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import Scrollable from '@/mixins/Scrollable'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {getAdmitBySid} from '@/api/admit'

export default {
  name: 'AdmitStudent',
  components: {AdmitDataWarning, ManageStudent, Spinner},
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
        this.$router.push({path: '/404'})
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
  padding: 4px 3px 4px 3px;
  vertical-align: top;
  width: 450px;
}
.table-separator {
  border-top: 1px solid rgb(108, 103, 103);
  margin: 20px 0 20px 0;
}
h2 {
  font-size: 16px;
  font-weight: bold;
}
</style>
