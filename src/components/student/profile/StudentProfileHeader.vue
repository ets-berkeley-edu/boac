<template>
  <div class="d-flex">
    <div>
      <StudentAvatar class="pr-3" :student="student" size="large"/>
      <CuratedGroupSelector :isStudentProfileView="true"
                            :students="[ student ]"/>
    </div>
    <div>
      <div>
        <h1 id="student-name-header"
            class="student-section-header mb-1"
            ref="pageHeader"
            tabindex="0"
            :class="{'demo-mode-blur': user.inDemoMode}">
          {{ student.name }}
        </h1>
        <h2 class="sr-only">Profile</h2>
        <div class="sr-only"
             v-if="student.sisProfile.preferredName !== student.name">Preferred name</div>
        <div id="student-preferred-name"
             class="student-preferred-name"
             :class="{'demo-mode-blur': user.inDemoMode}"
             v-if="student.sisProfile.preferredName !== student.name">
          {{ student.sisProfile.preferredName }}</div>
        <div id="student-bio-sid" class="student-bio-sid font-weight-bold pb-2">
          SID <span :class="{'demo-mode-blur': user.inDemoMode}">{{ student.sid }}</span>
        </div>
        <div>
          <i class="fas fa-envelope"></i>
          <span class="sr-only">Email</span>
          <a id="student-mailto"
             :href="`mailto:${student.sisProfile.emailAddress}`"
             :class="{'demo-mode-blur': user.inDemoMode}">
             {{ student.sisProfile.emailAddress }}</a>
        </div>
        <div v-if="student.sisProfile.phoneNumber">
          <i class="fas fa-phone"></i>
          <span class="sr-only">Phone number</span>
          <span id="student-phone-number"
                :class="{'demo-mode-blur': user.inDemoMode}"
                tabindex="0">
            {{ student.sisProfile.phoneNumber }}</span>
        </div>
      </div>
      <div id="student-bio-inactive" v-if="isInactive">
        <div class="student-bio-header student-bio-inactive">Inactive</div>
      </div>
      <div id="student-bio-athletics" v-if="student.athleticsProfile">
        <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName">
          <div class="student-bio-header">{{ membership.groupName }}</div>
        </div>
      </div>
    </div>
    <div class="ml-auto mr-5">
      <div id="student-bio-majors">
        <h3 class="sr-only">Major</h3>
        <div v-for="plan in student.sisProfile.plans" :key="plan.description">
          <div class="student-bio-header">
            <span v-if="!plan.degreeProgramUrl">{{ plan.description }}</span>
            <a :href="plan.degreeProgramUrl"
               target="_blank"
               :aria-label="`Open ${plan.description} program page in new window`"
               v-if="plan.degreeProgramUrl">
               {{ plan.description }}</a>
          </div>
          <div class="student-bio-details" v-if="plan.program">
            {{ plan.program }}
          </div>
        </div>
      </div>
      <div id="student-bio-level">
        <h3 class="sr-only">Level</h3>
        <div class="student-bio-header">{{ get(student, 'sisProfile.level.description') }}</div>
      </div>
      <div>
        <div id="student-bio-terms-in-attendance"
             class="student-bio-details"
             v-if="student.sisProfile.termsInAttendance">
          {{ 'Term' | pluralize(student.sisProfile.termsInAttendance) }} in Attendance
        </div>
        <div class="student-bio-details"
             id="student-bio-expected-graduation"
             v-if="student.sisProfile.expectedGraduationTerm && student.sisProfile.level.code !== 'GR'">
          Expected graduation {{ student.sisProfile.expectedGraduationTerm.name }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentMetadata from '@/mixins/StudentMetadata';
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'StudentProfileHeader',
  mixins: [StudentMetadata, UserMetadata, Util],
  components: {
    CuratedGroupSelector,
    StudentAvatar
  },
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
