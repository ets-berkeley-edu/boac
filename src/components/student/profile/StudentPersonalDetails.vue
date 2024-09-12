<template>
  <div class="mb-1 text-center w-100">
    <v-btn
      id="show-hide-personal-details"
      :aria-expanded="isExpanded"
      class="text-no-wrap"
      color="sky-blue"
      variant="flat"
      @click="toggle"
    >
      <div class="align-center d-flex text-primary">
        <v-icon :icon="isExpanded ? mdiMenuDown : mdiMenuRight" size="24" />
        <div>
          {{ isExpanded ? 'Hide' : 'Show' }} Personal Details
        </div>
      </div>
    </v-btn>
  </div>
  <v-expand-transition>
    <v-card v-if="isExpanded" class="expanded-card pa-2">
      <v-container fluid>
        <v-row>
          <v-col class="text-left" cols="4">
            <h3 class="student-profile-h3">
              Advisor(s)
            </h3>
            <div v-if="size(student.advisors)" id="student-profile-advisors">
              <div
                v-for="(advisor, index) in orderBy(student.advisors, a => a.title && a.title.toLowerCase().includes('director') ? 1 : 0)"
                :id="`student-profile-advisor-${index}`"
                :key="index"
              >
                <div :id="`student-profile-advisor-${index}-role`" class="font-weight-bold">
                  {{ advisor.role }}
                </div>
                <div :id="`student-profile-advisor-${index}-plan`" class="text-grey-darken-2">
                  {{ advisor.plan }}
                </div>
                <div :id="`student-profile-advisor-${index}-name`" class="text-grey-darken-2">
                  {{ join(remove([advisor.firstName, advisor.lastName]), ' ') }}
                </div>
                <div :id="`student-profile-advisor-${index}-email`" class="text-grey-darken-2">
                  {{ advisor.email }}
                </div>
              </div>
            </div>
            <div v-if="!size(student.advisors)" id="student-profile-advisors-none">
              None assigned.
            </div>
          </v-col>
          <v-col class="text-left" cols="4">
            <div id="contact-information-outer">
              <h3 class="student-profile-h3">
                Contact Information
              </h3>
              <div v-if="student.sisProfile.emailAddressAlternate" id="student-profile-other-email-outer">
                <div class="font-weight-bold">
                  Other Email (preferred)
                </div>
                <div id="student-profile-other-email" :class="{'demo-mode-blur': currentUser.inDemoMode}">
                  {{ student.sisProfile.emailAddressAlternate }}
                </div>
              </div>
              <div v-if="student.sisProfile.phoneNumber" id="student-profile-phone-number-outer">
                <div class="font-weight-bold">Phone</div>
                <a
                  id="student-phone-number"
                  :aria-label="`Link to student phone number ${student.sisProfile.phoneNumber}`"
                  :class="{'demo-mode-blur': currentUser.inDemoMode}"
                  :href="`tel:${student.sisProfile.phoneNumber}`"
                >
                  {{ student.sisProfile.phoneNumber }}</a>
              </div>
            </div>
            <div
              v-if="student.sisProfile.transfer || student.sisProfile.matriculation || visaDescription || hasCalCentralProfile"
              id="additional-information-outer"
              class="mt-5"
            >
              <h3 class="student-profile-h3">
                Additional Information
              </h3>
              <div class="text-grey-darken-2">
                <div v-if="student.sisProfile.transfer" id="student-profile-transfer">
                  Transfer
                </div>
                <div
                  v-if="student.sisProfile.matriculation"
                  id="student-bio-matriculation"
                >
                  Entered {{ student.sisProfile.matriculation }}
                </div>
                <div v-if="visaDescription" id="student-profile-visa">
                  {{ visaDescription }}
                </div>
                <div v-if="hasCalCentralProfile">
                  <a
                    id="link-to-calcentral"
                    aria-label="Open CalCentral in new window"
                    class="text-no-wrap"
                    :href="`https://calcentral.berkeley.edu/user/overview/${student.uid}`"
                    target="_blank"
                  >
                    Student profile in CalCentral <v-icon class="mb-1" :icon="mdiOpenInNew" size="18" />
                  </a>
                </div>
                <div class="mt-2">
                  <a
                    id="link-to-perceptive-content"
                    aria-label="Open Perceptive Content (Image Now) documents in new window"
                    :href="`https://imagine-content.berkeley.edu/#documents/view/321Z05B_01EFZBH4W0004XD?simplemode=true&constraint=[field1] = '${student.sid}'`"
                    target="_blank"
                  >
                    Perceptive Content (Image Now) documents <v-icon class="mb-1" :icon="mdiOpenInNew" size="18" />
                  </a>
                </div>
              </div>
            </div>
          </v-col>
          <v-col class="text-left" cols="4">
            <div v-if="student.sisProfile.intendedMajors" id="student-details-intended-majors-outer">
              <h3 v-if="isGraduate(student)" class="student-profile-h3">Intended Academic Plan</h3>
              <h3 v-if="!isGraduate(student)" class="student-profile-h3">Intended Major</h3>
              <div id="student-details-intended-majors">
                <div v-for="plan in student.sisProfile.intendedMajors" :key="plan.description">
                  <div class="font-weight-bold">
                    <span v-if="!plan.degreeProgramUrl" class="text-no-wrap">{{ plan.description }}</span>
                    <a
                      v-if="plan.degreeProgramUrl"
                      :href="plan.degreeProgramUrl"
                      :aria-label="`Open ${plan.description} program page in new window`"
                      target="_blank"
                    >
                      {{ plan.description }}</a>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="inactiveMajors.length" id="student-details-discontinued-majors-outer">
              <h3 class="student-profile-h3">
                Discontinued Major(s)
              </h3>
              <div id="student-details-discontinued-majors">
                <StudentProfilePlan
                  v-for="plan in inactiveMajors"
                  :key="plan.description"
                  :plan="plan"
                  :active="false"
                />
              </div>
            </div>
            <div v-if="inactiveMinors.length" id="student-details-discontinued-minors-outer">
              <h3 class="student-profile-h3">
                Discontinued Minor(s)
              </h3>
              <div id="student-details-discontinued-minors">
                <StudentProfilePlan
                  v-for="plan in inactiveMinors"
                  :key="plan.description"
                  :plan="plan"
                  :active="false"
                />
              </div>
            </div>
            <div v-if="inactiveSubplans.length" id="student-bio-subplans">
              <h3 class="student-profile-h3">Discontinued Subplan(s)</h3>
              <div
                v-for="(subplan, index) in inactiveSubplans"
                :key="index"
                class="font-weight-bold mb-2"
              >
                {{ subplan }}
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-expand-transition>
</template>

<script setup>
import StudentProfilePlan from '@/components/student/profile/StudentProfilePlan'
import {alertScreenReader, toInt} from '@/lib/utils'
import {isGraduate} from '@/berkeley'
import {mdiMenuDown, mdiMenuRight, mdiOpenInNew} from '@mdi/js'
import {find, get, includes, join, orderBy, remove, size} from 'lodash'
import {ref} from 'vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  inactiveMajors: {
    required: true,
    type: Array
  },
  inactiveMinors: {
    required: true,
    type: Array
  },
  inactiveSubplans: {
    required: true,
    type: Array
  },
  student: {
    required: true,
    type: Object
  }
})

const hasCompletedSection = enrollmentTerm => {
  const enrollments = enrollmentTerm.enrollments
  return enrollments.length && find(enrollments, e => {
    return size(e.sections) && find(e.sections, section => section.enrollmentStatus === 'E')
  })
}

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const isExpanded = ref(false)
const mostRecent = find(props.student.enrollmentTerms, e => hasCompletedSection(e))
// In the odd scheme of SIS termIds, a diff of 20 is equivalent to a diff of two years.
const enrolledInPastTwoYears = mostRecent && (contextStore.currentEnrollmentTermId - toInt(mostRecent.termId) <= 20)
const hasCalCentralProfile = enrolledInPastTwoYears || includes(props.student.sisProfile.calnetAffiliations, 'SIS-EXTENDED')
let visaDescription

if (get(props.student, 'demographics.visa.status') === 'G') {
  switch (props.student.demographics.visa.type) {
  case 'F1':
    visaDescription = 'F-1 International Student'
    break
  case 'J1':
    visaDescription = 'J-1 International Student'
    break
  case 'PR':
    visaDescription = 'PR Verified International Student'
    break
  default:
    visaDescription = 'Other Verified International Student'
    break
  }
}

const toggle = () => {
  isExpanded.value = !isExpanded.value
  alertScreenReader(`Student details are ${isExpanded.value ? 'showing' : 'hidden'}.`)
}
</script>

<style scoped>
.expanded-card {
  background-color: #f5fbff;
}
</style>
