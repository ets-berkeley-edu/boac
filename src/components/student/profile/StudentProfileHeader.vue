<template>
  <div class="d-flex p-3">
    <div class="text-center mb-2 mr-4">
      <StudentAvatar class="mb-2" :student="student" size="large" />
      <StudentGroupSelector :sid="student.sid" />
    </div>
    <div class="w-100">
      <div class="d-flex flex-wrap">
        <div class="flex-grow-1 mb-2">
          <div>
            <h1
              id="student-name-header"
              ref="pageHeader"
              class="student-section-header"
              tabindex="0"
              :class="{'demo-mode-blur': user.inDemoMode}">
              {{ student.name }}
            </h1>
            <h2 class="sr-only">Profile</h2>
            <div
              v-if="student.sisProfile.preferredName !== student.name"
              class="sr-only">
              Preferred name
            </div>
            <div
              v-if="student.sisProfile.preferredName !== student.name"
              id="student-preferred-name"
              class="font-size-20"
              :class="{'demo-mode-blur': user.inDemoMode}">
              {{ student.sisProfile.preferredName }}
            </div>
            <div id="student-bio-sid" class="font-size-14 font-weight-bold">
              SID <span :class="{'demo-mode-blur': user.inDemoMode}">{{ student.sid }}</span>
            </div>
            <div>
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
          <div v-if="isInactive" id="student-bio-inactive" class="font-weight-bolder has-error text-uppercase">
            Inactive
          </div>
          <div v-if="student.athleticsProfile" id="student-bio-athletics">
            <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName">
              <div class="font-weight-bolder">{{ membership.groupName }}</div>
            </div>
          </div>
        </div>
        <div class="mr-4">
          <div id="student-bio-majors">
            <h3 class="sr-only">Major</h3>
            <div v-for="plan in student.sisProfile.plans" :key="plan.description">
              <div class="font-weight-bolder">
                <span v-if="!plan.degreeProgramUrl" class="no-wrap">{{ plan.description }}</span>
                <a
                  v-if="plan.degreeProgramUrl"
                  :href="plan.degreeProgramUrl"
                  target="_blank"
                  :aria-label="`Open ${plan.description} program page in new window`">
                  {{ plan.description }}</a>
              </div>
              <div v-if="plan.program" class="text-muted">
                {{ plan.program }}
              </div>
            </div>
          </div>
          <div id="student-bio-level">
            <h3 class="sr-only">Level</h3>
            <div class="font-weight-bolder">{{ get(student, 'sisProfile.level.description') }}</div>
          </div>
          <div class="text-muted">
            <div v-if="student.sisProfile.termsInAttendance" id="student-bio-terms-in-attendance">
              {{ 'Term' | pluralize(student.sisProfile.termsInAttendance) }} in Attendance
            </div>
            <div
              v-if="student.sisProfile.expectedGraduationTerm && student.sisProfile.level.code !== 'GR'"
              id="student-bio-expected-graduation">
              Expected graduation {{ student.sisProfile.expectedGraduationTerm.name }}
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
    isInactive: undefined
  }),
  created() {
    this.isInactive = this.displayAsInactive(this.student);
  }
};
</script>
