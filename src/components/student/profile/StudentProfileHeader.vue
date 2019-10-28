<template>
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
              v-html="student.name"
              class="student-section-header"
              tabindex="0"></h1>
            <h2 class="sr-only">Profile</h2>
            <div
              v-if="student.sisProfile.preferredName !== student.name"
              class="sr-only">
              Preferred name
            </div>
            <div
              id="student-preferred-name"
              v-if="student.sisProfile.preferredName !== student.name"
              :class="{'demo-mode-blur': user.inDemoMode}"
              v-html="student.sisProfile.preferredName"
              class="font-size-20"></div>
            <div id="student-bio-sid" class="font-size-14 font-weight-bold mt-1 mb-1">
              SID <span :class="{'demo-mode-blur': user.inDemoMode}">{{ student.sid }}</span>
              <span
                id="student-bio-inactive"
                v-if="academicCareerStatus === 'Inactive'"
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
                {{ student.sisProfile.emailAddress }}</a>
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
          <div id="student-bio-inactive-asc" v-if="isAscInactive" class="font-weight-bolder has-error">
            ASC INACTIVE
          </div>
          <div id="student-bio-inactive-coe" v-if="isCoeInactive" class="font-weight-bolder has-error">
            CoE INACTIVE
          </div>
          <div id="student-bio-athletics" v-if="student.athleticsProfile">
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
              <div id="student-bio-terms-in-attendance" v-if="student.sisProfile.termsInAttendance">
                {{ 'Term' | pluralize(student.sisProfile.termsInAttendance) }} in Attendance
              </div>
              <div
                id="student-bio-matriculation"
                v-if="student.sisProfile.matriculation">
                Entered {{ student.sisProfile.matriculation }}
              </div>
              <div
                id="student-bio-expected-graduation"
                v-if="student.sisProfile.expectedGraduationTerm && get(student.sisProfile, 'level.code') !== 'GR'">
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
  </div>
</template>

<script>
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentGroupSelector from '@/components/student/profile/StudentGroupSelector';
import StudentMetadata from '@/mixins/StudentMetadata';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'StudentProfileHeader',
  components: {
    StudentGroupSelector,
    StudentAvatar
  },
  mixins: [StudentMetadata, UserMetadata, Util],
  props: {
    student: Object
  },
  data: () => ({
    degreePlans: [],
    degreePlanOwners: [],
    isAscInactive: undefined,
    isCoeInactive: undefined
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
