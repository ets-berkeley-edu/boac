<template>
  <div class="default-margins">
    <div v-if="!loading">
      <div class="align-center d-flex justify-space-between">
        <h1
          id="admit-name-header"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
          class="student-section-header"
        >
          {{ fullName }}
        </h1>
        <div class="mr-5">
          <ManageStudent
            :align-dropdown-right="true"
            button-variant="flat"
            domain="admitted_students"
            label="Add to Admission Group"
            label-class="px-2"
            :student="admit"
          />
        </div>
      </div>
      <div v-if="admit.studentUid">
        <router-link
          :id="`link-to-student-${admit.studentUid}`"
          :to="studentRoutePath(admit.studentUid, currentUser.inDemoMode)"
        >
          View <span :class="{'demo-mode-blur': currentUser.inDemoMode}" v-html="fullName" />'s profile page
        </router-link>
      </div>
      <div class="mt-3">
        <AdmitDataWarning :updated-at="get(admit, 'updatedAt')" />
      </div>
      <v-container class="px-2" fluid>
        <v-row>
          <v-col>
            <v-row>
              <v-col class="pl-0 py-0">
                <hr />
              </v-col>
            </v-row>
            <caption class="sr-only">Academic Details</caption>
            <v-row>
              <v-col class="table-cell">
                <h2>Academic Details</h2>
              </v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">ApplyUC CPID</v-col>
              <v-col id="admit-apply-uc-cpid" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.applyucCpid }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">CS Empl ID</v-col>
              <v-col id="admit-sid" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.sid }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">Birthdate</v-col>
              <v-col id="admit-birthdate" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ birthDate }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">Freshman or Transfer</v-col>
              <v-col id="admit.freshman-or-transfer" class="table-cell font-italic">{{ admit.freshmanOrTransfer }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">Admit Status</v-col>
              <v-col id="admit-admit-status" class="table-cell font-italic">{{ admit.admitStatus }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">Current SIR</v-col>
              <v-col id="admit-current-sir" class="table-cell font-italic">{{ admit.currentSir }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">College</v-col>
              <v-col id="admit-college" class="table-cell font-italic">{{ admit.college }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">Admit Term</v-col>
              <v-col id="admit-admit-term" class="table-cell font-italic">{{ admit.admitTerm }}</v-col>
            </v-row>
          </v-col>
          <v-col>
            <caption class="sr-only">Eligibility Details</caption>
            <v-row>
              <v-col class="pl-0 py-0">
                <hr />
              </v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">
                <h2>Eligibility Details</h2>
              </v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">Application Fee Waiver Flag</v-col>
              <v-col id="admit-application-fee-waiver-flag" class="table-cell font-italic">{{ admit.applicationFeeWaiverFlag }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">Family Income</v-col>
              <v-col id="admit-family-income" class="table-cell font-italic">{{ admit.familyIncome ? `$${toInt(admit.familyIncome).toLocaleString()}` : '' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">Student Income</v-col>
              <v-col id="admit-student-income" class="table-cell font-italic">{{ admit.studentIncome ? `$${toInt(admit.studentIncome).toLocaleString()}` : '' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">First Generation College</v-col>
              <v-col id="admit-first-generation-college" class="table-cell font-italic">{{ admit.firstGenerationCollege }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">Parent 1 Education Level</v-col>
              <v-col id="admit-parent-1-education-level" class="table-cell font-italic">{{ admit.parent1EducationLevel }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">Parent 2 Education Level</v-col>
              <v-col id="admit-parent-2-education-level" class="table-cell font-italic">{{ admit.parent2EducationLevel }}</v-col>
            </v-row>
            <v-row>
              <v-col class="table-cell">Highest Parent Education Level</v-col>
              <v-col id="admit-highest-parent-education-level" class="table-cell font-italic">{{ admit.highestParentEducationLevel }}</v-col>
            </v-row>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-row>
              <v-col>
                <v-row>
                  <v-col class="pl-0 py-0">
                    <hr />
                  </v-col>
                </v-row>
                <caption class="sr-only">Demographic Information</caption>
                <v-row>
                  <v-col class="table-cell">
                    <h2>Demographic Information</h2>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">XEthnic</v-col>
                  <v-col id="admit-x-ethnic" class="table-cell font-italic">{{ admit.xethnic }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Hispanic</v-col>
                  <v-col id="admit-hispanic" class="table-cell font-italic">{{ admit.hispanic }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">UREM</v-col>
                  <v-col id="admit-urem" class="table-cell font-italic">{{ admit.urem }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Residency Category</v-col>
                  <v-col id="admit-residency-category" class="table-cell font-italic">{{ admit.residencyCategory }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">US Citizenship Status</v-col>
                  <v-col id="admit-us-citizenship-status" class="table-cell font-italic">{{ admit.usCitizenshipStatus }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">US Non Citizen Status</v-col>
                  <v-col id="admit-us-non-citizen-status" class="table-cell font-italic">{{ admit.usNonCitizenStatus }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Citizenship Country</v-col>
                  <v-col id="admit-citizenship-country" class="table-cell font-italic">{{ admit.citizenshipCountry }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Permanent Residence Country</v-col>
                  <v-col id="admit-permanent-residence-country" class="table-cell font-italic">{{ admit.permanentResidenceCountry }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Non Immigrant Visa Current</v-col>
                  <v-col id="admit-non-immigrant-visa-current" class="table-cell font-italic">{{ admit.nonImmigrantVisaCurrent }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Non Immigrant Visa Planned</v-col>
                  <v-col id="admit-non-immigrant-visa-planned" class="table-cell font-italic">{{ admit.nonImmigrantVisaPlanned }}</v-col>
                </v-row>
              </v-col>
              <v-col>
                <v-row>
                  <v-col class="pl-0 py-0">
                    <hr />
                  </v-col>
                </v-row>
                <caption class="sr-only">Family and Status Information</caption>
                <v-row>
                  <v-col class="table-cell">
                    <h2>Family and Status Information</h2>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Foster Care Flag</v-col>
                  <v-col id="admit-foster-care-flag" class="table-cell font-italic">{{ admit.fosterCareFlag }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Family Is Single Parent</v-col>
                  <v-col id="admit-family-is-single-parent" class="table-cell font-italic">{{ admit.familyIsSingleParent }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Student Is Single Parent</v-col>
                  <v-col id="admit-student-is-single-parent" class="table-cell font-italic">{{ admit.studentIsSingleParent }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Family Dependents No.</v-col>
                  <v-col id="admit-family-dependents-num" class="table-cell font-italic">{{ admit.familyDependentsNum }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Student Dependents No.</v-col>
                  <v-col id="admit-student-dependents-num" class="table-cell font-italic">{{ admit.studentDependentsNum }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Is Military Dependent</v-col>
                  <v-col class="table-cell font-italic">{{ admit.isMilitaryDependent }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Military Status</v-col>
                  <v-col id="admit-military-status" class="table-cell font-italic">{{ admit.militaryStatus }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Re-entry Status</v-col>
                  <v-col id="admit-reentry-status" class="table-cell font-italic">{{ admit.reentryStatus }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Athlete Status</v-col>
                  <v-col id="admit-athlete-status" class="table-cell font-italic">{{ admit.athleteStatus }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Summer Bridge Status</v-col>
                  <v-col id="admit-summer-bridge-status" class="table-cell font-italic">{{ admit.summerBridgeStatus }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Last School LCFF+ Flag</v-col>
                  <v-col id="admit-last-school-lcff-plus-flag" class="table-cell font-italic">{{ admit.lastSchoolLcffPlusFlag }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Special Program - CEP</v-col>
                  <v-col id="admit-special-program-cep" class="table-cell font-italic">{{ admit.specialProgramCep }}</v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-row>
              <v-col>
                <v-row>
                  <v-col class="pl-0 py-0">
                    <hr />
                  </v-col>
                </v-row>
                <caption class="sr-only">Contact Information</caption>
                <v-row>
                  <v-col class="table-cell font-weight-bold">
                    <h2>Contact Information</h2>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Email</v-col>
                  <v-col id="admit-email" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.email }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Campus Email</v-col>
                  <v-col id="admit-campus-email" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.campusEmail1 }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Daytime Phone</v-col>
                  <v-col id="admit-daytime-phone" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.daytimePhone }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Mobile</v-col>
                  <v-col id="admit-mobile" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.mobile }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="table-cell">Address</v-col>
                  <v-col :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">
                    <div id="admit-permanent-street-1">{{ admit.permanentStreet1 }}</div>
                    <div id="admit-permanent-street-2">{{ admit.permanentStreet2 }}</div>
                    <div id="admit-permanent-city-region-postal">{{ admit.permanentCity }}, {{ admit.permanentRegion }}  {{ admit.permanentPostal }}</div>
                    <div id="admit-permanent-country">{{ admit.permanentCountry }}</div>
                  </v-col>
                </v-row>
              </v-col>
              <v-col>
                <v-row>
                  <v-col class="pl-0 py-0">
                    <hr />
                  </v-col>
                </v-row>
                <caption class="sr-only">GPA</caption>
                <v-row>
                  <v-col class="table-cell font-weight-bold">
                    <h2>GPA</h2>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col id="admit-gpa-hs-unweighted-th" class="table-cell">HS Unweighted GPA</v-col>
                  <v-col id="admit-gpa-hs-unweighted" class="table-cell font-italic" headers="admit-gpa admit-gpa-hs-unweighted-th">{{ admit.hsUnweightedGpa }}</v-col>
                </v-row>
                <v-row>
                  <v-col id="admit-gpa-hs-weighted-th" class="table-cell">HS Weighted GPA</v-col>
                  <v-col id="admit-gpa-hs-weighted" class="table-cell font-italic" headers="admit-gpa admit-gpa-hs-weighted-th">{{ admit.hsWeightedGpa }}</v-col>
                </v-row>
                <v-row>
                  <v-col id="admit-gpa-transfer-th" class="table-cell">Transfer GPA</v-col>
                  <v-col id="admit-gpa-transfer" class="table-cell font-italic" headers="admit-gpa admit-gpa-transfer-th">{{ admit.transferGpa }}</v-col>
                </v-row>
                <v-row>
                  <v-col class="pl-0 py-0">
                    <hr />
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </div>
</template>

<script setup>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import router from '@/router'
import {computed, onMounted, ref} from 'vue'
import {DateTime} from 'luxon'
import {get} from 'lodash'
import {getAdmitBySid} from '@/api/admit'
import {scrollToTop, setPageTitle, studentRoutePath, toInt} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()
const admit = ref(undefined)
const currentUser = contextStore.currentUser
const fullName = ref(undefined)
const loading = computed(() => contextStore.loading)

contextStore.loadingStart()

const birthDate = computed(() => {
  let birthDate = DateTime.fromJSDate(admit.value.birthdate)
  if (birthDate > DateTime.now()) {
    birthDate.minus({years: 100})
  }
  return birthDate.toFormat('MMM D, YYYY')
})

onMounted(() => {
  // In demo-mode we do not want to expose SID in browser location bar.
  const sid = currentUser.inDemoMode ? window.atob(sid) : useRoute().params.sid
  getAdmitBySid(sid).then(data => {
    if (data) {
      admit.value = data
      fullName.value = [admit.value.firstName, admit.value.middleName, admit.value.lastName].join(' ')
      setPageTitle(currentUser.inDemoMode ? 'Admitted Student' : fullName.value)
      contextStore.loadingComplete()
      scrollToTop()
    } else {
      router.push({path: '/404'})
    }
  })
})
</script>

<style scoped>
.table-cell {
  font-weight: normal;
  padding: 4px 3px 4px 3px;
  vertical-align: top;
  width: 450px;
}
.row-separator {
  border-top: 1px solid rgb(108, 103, 103);
}
h2 {
  font-size: 16px;
  font-weight: bold;
}
</style>
