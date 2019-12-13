<template>
  <transition name="drawer">
    <div v-show="isOpen" class="drawer">
      <div class="ml-4 mr-4 pb-4 pt-4 row">
        <div class="col-sm mr-2 pr-2">
          <h3 class="student-profile-section-header">
            Advisor(s)
          </h3>
          <div v-if="student.advisors.length" id="student-profile-advisors">
            <div
              v-for="(advisor, index) in student.advisors"
              :id="`student-profile-advisor-${index}`"
              :key="advisor.uid"
              class="mb-2">
              <div :id="`student-profile-advisor-${index}-role`">
                <strong>{{ advisor.role }}</strong>
              </div>
              <div :id="`student-profile-advisor-${index}-plan`" class="text-muted">
                {{ advisor.plan }}
              </div>
              <div :id="`student-profile-advisor-${index}-name`" class="text-muted">
                {{ advisor.firstName }} {{ advisor.lastName }}
              </div>
              <div :id="`student-profile-advisor-${index}-email`" class="text-muted">
                {{ advisor.email }}
              </div>
            </div>
          </div>
          <div v-if="!student.advisors.length" id="student-profile-advisors-none">
            None assigned.
          </div>
        </div>
        <div class="col-sm mr-2 pr-2">
          <div id="contact-information-outer" class="mb-4">
            <h3 class="student-profile-section-header">
              Contact Information
            </h3>
            <div v-if="student.sisProfile.emailAddressAlternate" id="student-profile-other-email-outer" class="mb-2">
              <div>
                <strong>Other Email (preferred)</strong>
              </div>
              <div id="student-profile-other-email">
                {{ student.sisProfile.emailAddressAlternate }}
              </div>
            </div>
            <div v-if="student.sisProfile.phoneNumber" id="student-profile-phone-number-outer" class="mb-2">
              <div>
                <strong>Phone</strong>
              </div>
              <a
                id="student-phone-number"
                :href="`tel:${student.sisProfile.phoneNumber}`"
                :class="{'demo-mode-blur': user.inDemoMode}"
                tabindex="0">
                {{ student.sisProfile.phoneNumber }}</a>
            </div>
          </div>
          <div id="additional-information-outer">
            <h3 class="student-profile-section-header">
              Additional Information
            </h3>
            <div class="text-muted">
              <div v-if="student.sisProfile.transfer" id="student-profile-transfer">
                Transfer
              </div>
              <div
                v-if="student.sisProfile.matriculation"
                id="student-bio-matriculation">
                Entered {{ student.sisProfile.matriculation }}
              </div>
              <div v-if="visaDescription" id="student-profile-visa">
                {{ visaDescription }}
              </div>
              <div v-if="student.athleticsProfile" id="student-bio-athletics">
                <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName">
                  {{ membership.groupName }}
                </div>
              </div>
              <div class="no-wrap mt-1">
                <a
                  id="link-to-calcentral"
                  :href="`https://calcentral.berkeley.edu/user/overview/${student.uid}`"
                  target="_blank"
                  aria-label="Open CalCentral in new window">Student profile in CalCentral <font-awesome icon="external-link-alt" class="pr-1" /></a>
              </div>
            </div>
          </div>
        </div>
        <div class="col-sm pr-2 mr-2">
          <div v-if="student.sisProfile.intendedMajors" id="student-details-intended-majors-outer" class="mb-4">
            <h3 class="student-profile-section-header">
              Intended Major
            </h3>
            <div id="student-details-intended-majors">
              <div v-for="plan in student.sisProfile.intendedMajors" :key="plan.description" class="mb-2">
                <div class="font-weight-bolder">
                  <span v-if="!plan.degreeProgramUrl" class="no-wrap">{{ plan.description }}</span>
                  <a
                    v-if="plan.degreeProgramUrl"
                    :href="plan.degreeProgramUrl"
                    :aria-label="`Open ${plan.description} program page in new window`"
                    target="_blank">
                    {{ plan.description }}</a>
                </div>
              </div>
            </div>
          </div>
          <div v-if="inactivePlans.length" id="student-details-discontinued-majors-outer" class="mb-3">
            <h3 class="student-profile-section-header">
              Discontinued Major(s)
            </h3>
            <div id="student-details-discontinued-majors">
              <div v-for="plan in inactivePlans" :key="plan.description" class="mb-2">
                <div class="font-weight-bolder">
                  <span v-if="!plan.degreeProgramUrl" class="no-wrap">{{ plan.description }}</span>
                  <a
                    v-if="plan.degreeProgramUrl"
                    :href="plan.degreeProgramUrl"
                    :aria-label="`Open ${plan.description} program page in new window`"
                    target="_blank">
                    {{ plan.description }}</a>
                </div>
                <div v-if="plan.program" class="text-muted">
                  {{ plan.program }}
                </div>
                <div class="font-weight-bolder has-error small text-uppercase">
                  {{ plan.status }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'StudentPersonalDetails',
  mixins: [UserMetadata, Util],
  props: {
    inactivePlans: {
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
  computed: {
    visaDescription() {
      if (this.get(this.student, 'demographics.visa.status') !== 'G') {
        return null;
      }
      switch (this.student.demographics.visa.type) {
        case 'F1':
          return 'F-1 International Student';
        case 'J1':
          return 'J-1 International Student';
        case 'PR':
          return 'PR Verified International Student';
        default:
          return 'Other Verified International Student';
      }
    }
  }
}
</script>

<style scoped>
.drawer {
  background-color: #f5fbff;
}
.drawer-enter-active {
   -webkit-transition-duration: 0.3s;
   transition-duration: 0.3s;
   -webkit-transition-timing-function: ease-in;
   transition-timing-function: ease-in;
}
.drawer-leave-active {
   -webkit-transition-duration: 0.3s;
   transition-duration: 0.5s;
   -webkit-transition-timing-function: cubic-bezier(0, 1, 0.5, 1);
   transition-timing-function: cubic-bezier(0, 1, 0.5, 1);
}
.drawer-enter-to, .drawer-leave {
  max-height: 280px;
  overflow: hidden;
}
.drawer-enter, .drawer-leave-to {
  overflow: hidden;
  max-height: 0;
}
</style>
