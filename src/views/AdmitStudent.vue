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
        <div>
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
      <div class="d-flex flex-wrap justify-space-between">
        <div class="border-t-sm mt-6 pt-3" :class="{'category': $vuetify.display.mdAndUp, 'w-100': !$vuetify.display.mdAndUp}">
          <h2>Academic Details</h2>
          <v-container fluid>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">ApplyUC CPID</v-col>
              <v-col id="admit-apply-uc-cpid" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.applyucCpid }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">CS Empl ID</v-col>
              <v-col id="admit-sid" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.sid }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Birthdate</v-col>
              <v-col id="admit-birthdate" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ birthDate || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Freshman or Transfer</v-col>
              <v-col id="admit.freshman-or-transfer" class="table-cell font-italic">{{ admit.freshmanOrTransfer || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Admit Status</v-col>
              <v-col id="admit-admit-status" class="table-cell font-italic">{{ admit.admitStatus || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Current SIR</v-col>
              <v-col id="admit-current-sir" class="table-cell font-italic">{{ admit.currentSir || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">College</v-col>
              <v-col id="admit-college" class="table-cell font-italic">{{ admit.college || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Admit Term</v-col>
              <v-col id="admit-admit-term" class="table-cell font-italic">{{ admit.admitTerm || '&mdash;' }}</v-col>
            </v-row>
          </v-container>
        </div>
        <div class="border-t-sm mt-6 pt-3" :class="{'category': $vuetify.display.mdAndUp, 'w-100': !$vuetify.display.mdAndUp}">
          <h2>Eligibility Details</h2>
          <v-container fluid>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Application Fee Waiver Flag</v-col>
              <v-col id="admit-application-fee-waiver-flag" class="table-cell font-italic">{{ admit.applicationFeeWaiverFlag || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Family Income</v-col>
              <v-col id="admit-family-income" class="table-cell font-italic">{{ admit.familyIncome ? `$${toInt(admit.familyIncome).toLocaleString()}` : '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Student Income</v-col>
              <v-col id="admit-student-income" class="table-cell font-italic">{{ admit.studentIncome ? `$${toInt(admit.studentIncome).toLocaleString()}` : '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">First Generation College</v-col>
              <v-col id="admit-first-generation-college" class="table-cell font-italic">{{ admit.firstGenerationCollege }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Parent 1 Education Level</v-col>
              <v-col id="admit-parent-1-education-level" class="table-cell font-italic">{{ admit.parent1EducationLevel }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Parent 2 Education Level</v-col>
              <v-col id="admit-parent-2-education-level" class="table-cell font-italic">{{ admit.parent2EducationLevel }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Highest Parent Education Level</v-col>
              <v-col id="admit-highest-parent-education-level" class="table-cell font-italic">{{ admit.highestParentEducationLevel }}</v-col>
            </v-row>
          </v-container>
        </div>
      </div>
      <div class="d-flex flex-wrap justify-space-between w-100">
        <div class="border-t-sm mt-6 pt-3" :class="{'category': $vuetify.display.mdAndUp, 'w-100': !$vuetify.display.mdAndUp}">
          <h2>Demographic Information</h2>
          <v-container fluid>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">XEthnic</v-col>
              <v-col id="admit-x-ethnic" class="table-cell font-italic">{{ admit.xethnic || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Hispanic</v-col>
              <v-col id="admit-hispanic" class="table-cell font-italic">{{ admit.hispanic || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">UREM</v-col>
              <v-col id="admit-urem" class="table-cell font-italic">{{ admit.urem || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Residency Category</v-col>
              <v-col id="admit-residency-category" class="table-cell font-italic">{{ admit.residencyCategory || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">US Citizenship Status</v-col>
              <v-col id="admit-us-citizenship-status" class="table-cell font-italic">{{ admit.usCitizenshipStatus || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">US Non Citizen Status</v-col>
              <v-col id="admit-us-non-citizen-status" class="table-cell font-italic">{{ admit.usNonCitizenStatus || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Citizenship Country</v-col>
              <v-col id="admit-citizenship-country" class="table-cell font-italic">{{ admit.citizenshipCountry || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Permanent Residence Country</v-col>
              <v-col id="admit-permanent-residence-country" class="table-cell font-italic">{{ admit.permanentResidenceCountry || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Non Immigrant Visa Current</v-col>
              <v-col id="admit-non-immigrant-visa-current" class="table-cell font-italic">{{ admit.nonImmigrantVisaCurrent || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Non Immigrant Visa Planned</v-col>
              <v-col id="admit-non-immigrant-visa-planned" class="table-cell font-italic">{{ admit.nonImmigrantVisaPlanned || '&mdash;' }}</v-col>
            </v-row>
          </v-container>
        </div>
        <div class="border-t-sm mt-6 pt-3" :class="{'category': $vuetify.display.mdAndUp, 'w-100': !$vuetify.display.mdAndUp}">
          <h2>Family and Status Information</h2>
          <v-container fluid>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Foster Care Flag</v-col>
              <v-col id="admit-foster-care-flag" class="table-cell font-italic">{{ admit.fosterCareFlag || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Family Is Single Parent</v-col>
              <v-col id="admit-family-is-single-parent" class="table-cell font-italic">{{ admit.familyIsSingleParent || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Student Is Single Parent</v-col>
              <v-col id="admit-student-is-single-parent" class="table-cell font-italic">{{ admit.studentIsSingleParent || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Family Dependents No.</v-col>
              <v-col id="admit-family-dependents-num" class="table-cell font-italic">{{ admit.familyDependentsNum || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Student Dependents No.</v-col>
              <v-col id="admit-student-dependents-num" class="table-cell font-italic">{{ admit.studentDependentsNum || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Is Military Dependent</v-col>
              <v-col class="table-cell font-italic">{{ admit.isMilitaryDependent || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Military Status</v-col>
              <v-col id="admit-military-status" class="table-cell font-italic">{{ admit.militaryStatus || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Re-entry Status</v-col>
              <v-col id="admit-reentry-status" class="table-cell font-italic">{{ admit.reentryStatus || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Athlete Status</v-col>
              <v-col id="admit-athlete-status" class="table-cell font-italic">{{ admit.athleteStatus || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Summer Bridge Status</v-col>
              <v-col id="admit-summer-bridge-status" class="table-cell font-italic">{{ admit.summerBridgeStatus || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Last School LCFF+ Flag</v-col>
              <v-col id="admit-last-school-lcff-plus-flag" class="table-cell font-italic">{{ admit.lastSchoolLcffPlusFlag || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Special Program - CEP</v-col>
              <v-col id="admit-special-program-cep" class="table-cell font-italic">{{ admit.specialProgramCep || '&mdash;' }}</v-col>
            </v-row>
          </v-container>
        </div>
      </div>
      <div class="d-flex flex-wrap justify-space-between">
        <div class="border-t-sm mt-6 pt-3" :class="{'category': $vuetify.display.mdAndUp, 'w-100': !$vuetify.display.mdAndUp}">
          <h2>Contact Information</h2>
          <v-container fluid>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Email</v-col>
              <v-col id="admit-email" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.email || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Campus Email</v-col>
              <v-col id="admit-campus-email" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.campusEmail1 || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Daytime Phone</v-col>
              <v-col
                id="admit-daytime-phone"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
                class="table-cell font-italic"
              >
                {{ admit.daytimePhone || '&mdash;' }}
              </v-col>
            </v-row>
            <v-row>
              <v-col class="font-weight-medium" cols="5">Mobile</v-col>
              <v-col id="admit-mobile" :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">{{ admit.mobile || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col class="font-weight-medium" cols="5">Address</v-col>
              <v-col :class="{'demo-mode-blur': currentUser.inDemoMode}" class="table-cell font-italic">
                <div id="admit-permanent-street-1">{{ admit.permanentStreet1 }}</div>
                <div id="admit-permanent-street-2">{{ admit.permanentStreet2 }}</div>
                <div id="admit-permanent-city-region-postal">{{ admit.permanentCity }}, {{ admit.permanentRegion }}  {{ admit.permanentPostal }}</div>
                <div id="admit-permanent-country">{{ admit.permanentCountry }}</div>
              </v-col>
            </v-row>
          </v-container>
        </div>
        <div class="border-t-sm mt-6 pt-3" :class="{'category': $vuetify.display.mdAndUp, 'w-100': !$vuetify.display.mdAndUp}">
          <h2>GPA</h2>
          <v-container fluid>
            <v-row class="bg-grey-lighten-4">
              <v-col id="admit-gpa-hs-unweighted-th" class="font-weight-medium" cols="5">HS Unweighted GPA</v-col>
              <v-col id="admit-gpa-hs-unweighted" class="table-cell font-italic" headers="admit-gpa admit-gpa-hs-unweighted-th">{{ admit.hsUnweightedGpa || '&mdash;' }}</v-col>
            </v-row>
            <v-row>
              <v-col id="admit-gpa-hs-weighted-th" class="font-weight-medium" cols="5">HS Weighted GPA</v-col>
              <v-col id="admit-gpa-hs-weighted" class="table-cell font-italic" headers="admit-gpa admit-gpa-hs-weighted-th">{{ admit.hsWeightedGpa || '&mdash;' }}</v-col>
            </v-row>
            <v-row class="bg-grey-lighten-4">
              <v-col id="admit-gpa-transfer-th" class="font-weight-medium" cols="5">Transfer GPA</v-col>
              <v-col id="admit-gpa-transfer" class="table-cell font-italic" headers="admit-gpa admit-gpa-transfer-th">{{ admit.transferGpa || '&mdash;' }}</v-col>
            </v-row>
          </v-container>
        </div>
      </div>
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
let birthDate = undefined
const currentUser = contextStore.currentUser
const fullName = ref(undefined)
const loading = computed(() => contextStore.loading)

contextStore.loadingStart()

onMounted(() => {
  // In demo-mode we do not want to expose SID in browser location bar.
  const sid = currentUser.inDemoMode ? window.atob(sid) : useRoute().params.sid
  getAdmitBySid(sid).then(data => {
    if (data) {
      admit.value = data
      fullName.value = [admit.value.firstName, admit.value.middleName, admit.value.lastName].join(' ')
      birthDate = DateTime.fromISO(admit.value.birthdate)
      if (birthDate > DateTime.now()) {
        birthDate.minus({years: 100})
      }
      birthDate = birthDate.toFormat('MMM d, yyyy')
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
h2 {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
}
.category {
  width: 49%;
}
</style>
