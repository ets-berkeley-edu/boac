<template>
  <div class="d-flex">
    <div class="text-center m-3">
      <StudentAvatar class="mb-2" :student="student" size="large" />
      <StudentGroupSelector :sid="student.sid" />
    </div>
    <div class="ml-3">
      <div class="mt-3">
        <h1
          id="student-name-header"
          ref="pageHeader"
          class="student-section-header mb-1"
          tabindex="0"
          :class="{'demo-mode-blur': get(user, 'inDemoMode', true)}">
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
          class="student-preferred-name mb-2"
          :class="{'demo-mode-blur': get(user, 'inDemoMode', true)}">
          {{ student.sisProfile.preferredName }}
        </div>
        <div id="student-bio-sid" class="student-sid font-weight-bold mb-2">
          SID <span :class="{'demo-mode-blur': get(user, 'inDemoMode', true)}">{{ student.sid }}</span>
        </div>
        <div class="mb-1">
          <i class="fas fa-envelope"></i>
          <span class="sr-only">Email</span>
          <a
            id="student-mailto"
            :href="`mailto:${student.sisProfile.emailAddress}`"
            :class="{'demo-mode-blur': get(user, 'inDemoMode', true)}"
            target="_blank">
            {{ student.sisProfile.emailAddress }}</a>
        </div>
        <div v-if="student.sisProfile.phoneNumber">
          <i class="fas fa-phone"></i>
          <span class="sr-only">Phone number</span>
          <a
            id="student-phone-number"
            :href="`tel:${student.sisProfile.phoneNumber}`"
            :class="{'demo-mode-blur': get(user, 'inDemoMode', true)}"
            tabindex="0">
            {{ student.sisProfile.phoneNumber }}</a>
        </div>
      </div>
      <div v-if="isInactive" id="student-bio-inactive" class="bio-header inactive-student mt-1">
        Inactive
      </div>
      <div v-if="student.athleticsProfile" id="student-bio-athletics">
        <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName">
          <div class="bio-header">{{ membership.groupName }}</div>
        </div>
      </div>
    </div>
    <div class="ml-auto m-3 mr-5">
      <div id="student-bio-majors">
        <h3 class="sr-only">Major</h3>
        <div v-for="plan in student.sisProfile.plans" :key="plan.description">
          <div class="bio-header">
            <span v-if="!plan.degreeProgramUrl" class="no-wrap">{{ plan.description }}</span>
            <a
              v-if="plan.degreeProgramUrl"
              :href="plan.degreeProgramUrl"
              target="_blank"
              :aria-label="`Open ${plan.description} program page in new window`">
              {{ plan.description }}</a>
          </div>
          <div v-if="plan.program" class="bio-details">
            {{ plan.program }}
          </div>
        </div>
      </div>
      <div id="student-bio-level">
        <h3 class="sr-only">Level</h3>
        <div class="bio-header">{{ get(student, 'sisProfile.level.description') }}</div>
      </div>
      <div class="bio-details">
        <div v-if="student.sisProfile.termsInAttendance" id="student-bio-terms-in-attendance">
          {{ 'Term' | pluralize(student.sisProfile.termsInAttendance) }} in Attendance
        </div>
        <div
          v-if="student.sisProfile.expectedGraduationTerm && student.sisProfile.level.code !== 'GR'"
          id="student-bio-expected-graduation">
          Expected graduation {{ student.sisProfile.expectedGraduationTerm.name }}
        </div>
        <div class="no-wrap mt-2">
          <a
            id="link-to-calcentral"
            :href="`https://calcentral.berkeley.edu/user/overview/${student.uid}`"
            target="_blank"
            aria-label="Open CalCentral in new window">Student profile in CalCentral <i class="pr-1 fas fa-external-link-alt"></i></a>
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

<style scoped>
.bio-details {
  color: #999;
  font-size: 14px;
}
.bio-header {
  font-size: 16px;
  font-weight: 600;
}
.inactive-student {
  color: #cf1715;
  text-transform: uppercase;
}
.student-sid {
  font-size: 14px;
}
.student-preferred-name {
  font-size: 20px;
  font-weight: 400;
}
</style>
