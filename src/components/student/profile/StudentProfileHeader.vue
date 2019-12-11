<template>
  <div>
    <div class="d-flex p-3">
      <div class="text-center mb-2 mr-4">
        <StudentAvatar :student="student" class="mb-2" size="large" />
        <StudentGroupSelector :student="student" />
      </div>
      <div class="w-100">
        <div class="d-flex flex-wrap">
          <div class="flex-grow-1 mb-2">
            <div>
              <h1
                id="student-name-header"
                ref="pageHeader"
                :class="{'demo-mode-blur': user.inDemoMode}"
                class="student-section-header"
                tabindex="0"
                v-html="student.name"></h1>
              <h2 class="sr-only">Profile</h2>
              <div
                v-if="student.sisProfile.preferredName !== student.name"
                class="sr-only">
                Preferred name
              </div>
              <div
                v-if="student.sisProfile.preferredName !== student.name"
                id="student-preferred-name"
                :class="{'demo-mode-blur': user.inDemoMode}"
                class="font-size-20"
                v-html="student.sisProfile.preferredName"></div>
              <div id="student-bio-sid" class="font-size-14 font-weight-bold mt-1 mb-1">
                SID <span :class="{'demo-mode-blur': user.inDemoMode}">{{ student.sid }}</span>
                <span
                  v-if="academicCareerStatus === 'Inactive'"
                  id="student-bio-inactive"
                  class="red-flag-status ml-1">
                  INACTIVE
                </span>
              </div>
              <div v-if="student.sisProfile.emailAddress">
                <font-awesome icon="envelope" />
                <span class="sr-only">Email</span>
                <a
                  id="student-mailto"
                  :href="`mailto:${student.sisProfile.emailAddress}`"
                  :class="{'demo-mode-blur': user.inDemoMode}"
                  target="_blank">
                  {{ student.sisProfile.emailAddress }}<span class="sr-only"> (will open new browser tab)</span>
                </a>
              </div>
              <div v-if="student.sisProfile.phoneNumber">
                <font-awesome icon="phone" />
                <span class="sr-only">Phone number</span>
                <a
                  id="student-phone-number"
                  :href="`tel:${student.sisProfile.phoneNumber}`"
                  :class="{'demo-mode-blur': user.inDemoMode}"
                  tabindex="0">
                  {{ student.sisProfile.phoneNumber }}</a>
              </div>
            </div>
            <div v-if="isAscInactive" id="student-bio-inactive-asc" class="font-weight-bolder has-error">
              ASC INACTIVE
            </div>
            <div v-if="isCoeInactive" id="student-bio-inactive-coe" class="font-weight-bolder has-error">
              CoE INACTIVE
            </div>
            <div v-if="student.athleticsProfile" id="student-bio-athletics">
              <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName">
                {{ membership.groupName }}
              </div>
            </div>
          </div>
          <div class="mr-4">
            <div v-if="academicCareerStatus !== 'Completed'">
              <div id="student-bio-majors">
                <h3 class="sr-only">Major</h3>
                <div v-for="plan in sortedPlans" :key="plan.description" class="mb-2">
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
                  <div v-if="plan.status !== 'Active'" class="font-weight-bolder has-error small text-uppercase">
                    {{ plan.status }}
                  </div>
                </div>
              </div>
              <div id="student-bio-level">
                <h3 class="sr-only">Level</h3>
                <div class="font-weight-bolder">{{ get(student, 'sisProfile.level.description') }}</div>
              </div>
              <div class="text-muted">
                <div v-if="student.sisProfile.transfer">
                  Transfer
                </div>
                <div v-if="student.sisProfile.termsInAttendance" id="student-bio-terms-in-attendance">
                  {{ 'Term' | pluralize(student.sisProfile.termsInAttendance) }} in Attendance
                </div>
                <div
                  v-if="student.sisProfile.matriculation"
                  id="student-bio-matriculation">
                  Entered {{ student.sisProfile.matriculation }}
                </div>
                <div
                  v-if="student.sisProfile.expectedGraduationTerm && get(student.sisProfile, 'level.code') !== 'GR'"
                  id="student-bio-expected-graduation">
                  Expected graduation {{ student.sisProfile.expectedGraduationTerm.name }}
                </div>
              </div>
            </div>
            <div v-if="academicCareerStatus === 'Completed' && student.sisProfile.degree">
              <h3 class="sr-only">Degree</h3>
              <div id="student-bio-degree-type" class="font-weight-bolder">
                <span v-if="!includes(degreePlanOwners, 'Graduate Division')">
                  {{ student.sisProfile.degree.description }} in
                </span>
                {{ degreePlans.join(', ') }}
              </div>
              <div id="student-bio-degree-date">
                <span class="student-text">Awarded {{ student.sisProfile.degree.dateAwarded | moment('MMM DD, YYYY') }}</span>
              </div>
              <div v-for="owner in degreePlanOwners" :key="owner" class="student-text">
                <span class="student-text">{{ owner }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="d-flex justify-content-center">
      <div>
        <b-btn
          id="show-hide-personal-details"
          :aria-label="isShowingPersonalDetails ? 'Hide personal details' : 'Show personal details'"
          class="no-wrap"
          variant="link"
          @click="isShowingPersonalDetails = !isShowingPersonalDetails">
          <font-awesome :icon="isShowingPersonalDetails ? 'caret-down' : 'caret-right'" :class="isShowingPersonalDetails ? 'mr-1' : 'ml-1 mr-1'" />
          {{ isShowingPersonalDetails ? 'Hide' : 'Show' }} Personal Details
        </b-btn>
      </div>
    </div>
    <div>
      <StudentPersonalDetails :is-open="isShowingPersonalDetails" :student="student" />
    </div>
  </div>
</template>

<script>
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentGroupSelector from '@/components/student/profile/StudentGroupSelector';
import StudentMetadata from '@/mixins/StudentMetadata';
import StudentPersonalDetails from "@/components/student/profile/StudentPersonalDetails";
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'StudentProfileHeader',
  components: {
    StudentAvatar,
    StudentGroupSelector,
    StudentPersonalDetails
  },
  mixins: [StudentMetadata, UserMetadata, Util],
  props: {
    student: Object
  },
  data: () => ({
    degreePlans: [],
    degreePlanOwners: [],
    isAscInactive: undefined,
    isCoeInactive: undefined,
    isShowingPersonalDetails: false
  }),
  computed: {
    academicCareerStatus() {
      return this.get(this.student, 'sisProfile.academicCareerStatus');
    },
    sortedPlans() {
      return this.orderBy(this.student.sisProfile.plans, 'status');
    }
  },
  created() {
    this.isAscInactive = this.displayAsAscInactive(this.student);
    this.isCoeInactive = this.displayAsCoeInactive(this.student);
    const plans = this.get(this.student, 'sisProfile.degree.plans');
    if (plans) {
      this.degreePlans = this.uniq(this.map(plans, 'plan'));
      this.degreePlanOwners = this.uniq(this.map(plans, 'group'));
    }
  }
};
</script>
