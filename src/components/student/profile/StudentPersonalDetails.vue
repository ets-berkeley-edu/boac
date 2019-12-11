<template>
  <transition name="drawer">
    <div v-show="isOpen" class="drawer">
      <div class="ml-4 mr-4 pb-4 pt-4 row">
        <div class="col-sm mr-2 pr-2">
          <h3 class="student-profile-section-header">
            Advisor(s)
          </h3>
          <div>
            <div>
              <strong>College Advisor</strong>
            </div>
            <div class="text-muted">
              Letters & Sci Undeclared UG
            </div>
            <div class="text-muted">
              Paulette Jacobs
            </div>
            <div>
              paulette.jacobs@berkeley.edu
            </div>
          </div>
        </div>
        <div class="col-sm mr-2 pr-2">
          <div id="contact-information-outer" class="mb-3">
            <h3 class="student-profile-section-header">
              Contact Information
            </h3>
            <div>
              <div>
                <strong>Other Email (preferred)</strong>
              </div>
              <div>
                paulette.jacobs@berkeley.edu
              </div>
            </div>
            <div v-if="student.sisProfile.phoneNumber">
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
          <div id="additional-information-outer" class="mb-3">
            <h3 class="student-profile-section-header">
              Additional Information
            </h3>
            <div class="text-muted">
              <div
                v-if="student.sisProfile.matriculation"
                id="student-bio-matriculation">
                Entered {{ student.sisProfile.matriculation }}
              </div>
              <div v-if="student.athleticsProfile" id="student-bio-athletics">
                <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName">
                  {{ membership.groupName }}
                </div>
              </div>
              <div v-if="student.sisProfile.transfer">
                Transfer
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
          <div v-if="student.sisProfile.intendedMajors" id="student-details-intended-majors-outer" class="mb-3">
            <h3 class="student-profile-section-header">
              Intended Major
            </h3>
            <div id="student-details-intended-majors">
              <div v-for="plan in student.sisProfile.intendedMajors" :key="plan.description" class="mb-2">
                <strong class="no-wrap">{{ plan.description }}</strong>
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

export default {
  name: 'StudentPersonalDetails',
  mixins: [UserMetadata],
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
