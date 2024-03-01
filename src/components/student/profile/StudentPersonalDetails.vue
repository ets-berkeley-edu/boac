<template>
  <transition name="drawer">
    <div v-show="isOpen" :aria-expanded="isOpen" class="drawer">
      <div class="ml-4 mr-4 pb-4 pt-4 row">
        <div class="col-sm mr-2 pr-2">
          <h3 class="student-profile-h3">
            Advisor(s)
          </h3>
          <div v-if="_size(student.advisors)" id="student-profile-advisors">
            <div
              v-for="(advisor, index) in advisorsSorted"
              :id="`student-profile-advisor-${index}`"
              :key="index"
              class="mb-2"
            >
              <div :id="`student-profile-advisor-${index}-role`">
                <strong>{{ advisor.role }}</strong>
              </div>
              <div :id="`student-profile-advisor-${index}-plan`" class="text-muted">
                {{ advisor.plan }}
              </div>
              <div :id="`student-profile-advisor-${index}-name`" class="text-muted">
                {{ advisorName(advisor) }}
              </div>
              <div :id="`student-profile-advisor-${index}-email`" class="text-muted">
                {{ advisor.email }}
              </div>
            </div>
          </div>
          <div v-if="!_size(student.advisors)" id="student-profile-advisors-none">
            None assigned.
          </div>
        </div>
        <div class="col-sm mr-2 pr-2">
          <div id="contact-information-outer" class="mb-4">
            <h3 class="student-profile-h3">
              Contact Information
            </h3>
            <div v-if="student.sisProfile.emailAddressAlternate" id="student-profile-other-email-outer" class="mb-2">
              <div>
                <strong>Other Email (preferred)</strong>
              </div>
              <div id="student-profile-other-email" :class="{'demo-mode-blur': currentUser.inDemoMode}">
                {{ student.sisProfile.emailAddressAlternate }}
              </div>
            </div>
            <div v-if="student.sisProfile.phoneNumber" id="student-profile-phone-number-outer" class="mb-2">
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
          >
            <h3 class="student-profile-h3">
              Additional Information
            </h3>
            <div class="text-muted">
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
              <div v-if="hasCalCentralProfile" class="no-wrap mt-1">
                <a
                  id="link-to-calcentral"
                  :href="`https://calcentral.berkeley.edu/user/overview/${student.uid}`"
                  target="_blank"
                  aria-label="Open CalCentral in new window"
                >Student profile in CalCentral <v-icon :icon="mdiOpenInNew" class="pl-1" /></a>
              </div>
              <div>
                <a
                  id="link-to-perceptive-content"
                  :href="`https://imagine-content.berkeley.edu/#documents/view/321Z05B_01EFZBH4W0004XD?simplemode=true&constraint=[field1] = '${student.sid}'`"
                  target="_blank"
                  aria-label="Open Perceptive Content (Image Now) documents in new window"
                >Perceptive Content (Image Now) documents <v-icon :icon="mdiOpenInNew" class="pl-1" /></a>
              </div>
            </div>
          </div>
        </div>
        <div class="col-sm pr-2 mr-2">
          <div v-if="student.sisProfile.intendedMajors" id="student-details-intended-majors-outer" class="mb-4">
            <h3 v-if="isGraduate(student)" class="student-profile-h3">Intended Academic Plan</h3>
            <h3 v-if="!isGraduate(student)" class="student-profile-h3">Intended Major</h3>
            <div id="student-details-intended-majors">
              <div v-for="plan in student.sisProfile.intendedMajors" :key="plan.description" class="mb-2">
                <div class="font-weight-bolder">
                  <span v-if="!plan.degreeProgramUrl" class="no-wrap">{{ plan.description }}</span>
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
          <div v-if="inactiveMajors.length" id="student-details-discontinued-majors-outer" class="mb-3">
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
          <div v-if="inactiveMinors.length" id="student-details-discontinued-minors-outer" class="mb-3">
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
          <div v-if="inactiveSubplans.length" id="student-bio-subplans" class="mb-3">
            <h3 class="student-profile-h3">Discontinued Subplan(s)</h3>
            <div
              v-for="(subplan, index) in inactiveSubplans"
              :key="index"
              class="font-weight-bolder mb-2"
            >
              {{ subplan }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import {mdiOpenInNew} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import StudentProfilePlan from '@/components/student/profile/StudentProfilePlan'
import Util from '@/mixins/Util'
import {isGraduate} from '@/berkeley'

export default {
  name: 'StudentPersonalDetails',
  components: {StudentProfilePlan},
  mixins: [Context, Util],
  props: {
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
    isOpen: {
      required: true,
      type: Boolean
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    hasCalCentralProfile: undefined
  }),
  computed: {
    advisorsSorted() {
      return this._orderBy(this.student.advisors, this.getAdvisorSortOrder)
    },
    getAdvisorSortOrder(advisor) {
      return advisor.title && advisor.title.toLowerCase().includes('director') ? 1 : 0
    },
    visaDescription() {
      if (this._get(this.student, 'demographics.visa.status') !== 'G') {
        return null
      }
      switch (this.student.demographics.visa.type) {
      case 'F1':
        return 'F-1 International Student'
      case 'J1':
        return 'J-1 International Student'
      case 'PR':
        return 'PR Verified International Student'
      default:
        return 'Other Verified International Student'
      }
    }
  },
  created() {
    this.hasCalCentralProfile = this.enrolledInPastTwoYears() || this._includes(this.student.sisProfile.calnetAffiliations, 'SIS-EXTENDED')
  },
  methods: {
    advisorName(advisor) {
      return this._join(this._remove([advisor.firstName, advisor.lastName]), ' ')
    },
    enrolledInPastTwoYears() {
      // In the odd scheme of SIS termIds, a diff of 20 is equivalent to a diff of two years.
      const hasCompletedSection = enrollmentTerm => {
        const enrollments = enrollmentTerm.enrollments
        return enrollments.length && this._find(enrollments, e => {
          return this._size(e.sections) && this._find(e.sections, section => section.enrollmentStatus === 'E')
        })
      }
      const mostRecent = this._find(this.student.enrollmentTerms, e => hasCompletedSection(e))
      return mostRecent && (this.config.currentEnrollmentTermId - this.toInt(mostRecent.termId) <= 20)
    },
    isGraduate
  }
}
</script>

<style scoped>
.drawer {
  background-color: #f5fbff;
}
</style>
