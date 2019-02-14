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
          class="student-preferred-name mb-2"
          :class="{'demo-mode-blur': user.inDemoMode}">
          {{ student.sisProfile.preferredName }}
        </div>
        <div id="student-bio-sid" class="student-bio-sid font-weight-bold mb-2">
          SID <span :class="{'demo-mode-blur': user.inDemoMode}">{{ student.sid }}</span>
        </div>
        <div class="mb-1">
          <i class="fas fa-envelope"></i>
          <span class="sr-only">Email</span>
          <a
            id="student-mailto"
            :href="`mailto:${student.sisProfile.emailAddress}`"
            :class="{'demo-mode-blur': user.inDemoMode}"
            target="_blank">
            {{ student.sisProfile.emailAddress }}</a>
        </div>
        <div v-if="student.sisProfile.phoneNumber">
          <i class="fas fa-phone"></i>
          <span class="sr-only">Phone number</span>
          <a
            id="student-phone-number"
            :href="`tel:${student.sisProfile.phoneNumber}`"
            :class="{'demo-mode-blur': user.inDemoMode}"
            tabindex="0">
            {{ student.sisProfile.phoneNumber }}</a>
        </div>
      </div>
      <div v-if="isInactive" id="student-bio-inactive">
        <div class="student-bio-header student-bio-inactive">Inactive</div>
      </div>
      <div v-if="student.athleticsProfile" id="student-bio-athletics">
        <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName">
          <div class="student-bio-header">{{ membership.groupName }}</div>
        </div>
      </div>
    </div>
    <div class="ml-auto m-3 mr-5 pr-5">
      <div id="student-bio-majors">
        <h3 class="sr-only">Major</h3>
        <div v-for="plan in student.sisProfile.plans" :key="plan.description">
          <div class="student-bio-header">
            <span v-if="!plan.degreeProgramUrl">{{ plan.description }}</span>
            <a
              v-if="plan.degreeProgramUrl"
              :href="plan.degreeProgramUrl"
              target="_blank"
              :aria-label="`Open ${plan.description} program page in new window`">
              {{ plan.description }}</a>
          </div>
          <div v-if="plan.program" class="student-bio-details">
            {{ plan.program }}
          </div>
        </div>
      </div>
      <div id="student-bio-level">
        <h3 class="sr-only">Level</h3>
        <div class="student-bio-header">{{ get(student, 'sisProfile.level.description') }}</div>
      </div>
      <div>
        <div
          v-if="student.sisProfile.termsInAttendance"
          id="student-bio-terms-in-attendance"
          class="student-bio-details">
          {{ 'Term' | pluralize(student.sisProfile.termsInAttendance) }} in Attendance
        </div>
        <div
          v-if="student.sisProfile.expectedGraduationTerm && student.sisProfile.level.code !== 'GR'"
          id="student-bio-expected-graduation"
          class="student-bio-details">
          Expected graduation {{ student.sisProfile.expectedGraduationTerm.name }}
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
.student-bio-details {
  color: #999;
  font-size: 14px;
}
.student-bio-header {
  font-size: 16px;
  font-weight: 600;
}
.student-bio-inactive {
  color: #cf1715;
  text-transform: uppercase;
}
.student-bio-sid {
  font-size: 14px;
}
.student-preferred-name {
  font-size: 20px;
  font-weight: 400;
}
</style>
