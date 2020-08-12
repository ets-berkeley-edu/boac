<template>
  <div>
    <div class="ml-4 mr-4 pb-2 pt-4 row">
      <div class="col-sm bb-2 mr-2 text-center">
        <StudentAvatar :student="student" class="mb-2" size="large" />
        <StudentGroupSelector :student="student" />
      </div>
      <div class="col-sm mr-2 pr-2">
        <div>
          <h1
            id="student-name-header"
            ref="pageHeader"
            :class="{'demo-mode-blur': $currentUser.inDemoMode}"
            class="student-section-header"
            tabindex="0"
            v-html="student.name"></h1>
          <h2 class="sr-only">Profile</h2>
          <div
            v-if="student.sisProfile.preferredName !== student.name"
            id="student-preferred-name"
            :class="{'demo-mode-blur': $currentUser.inDemoMode}">
            <span class="sr-only">Preferred name</span>
            <span v-html="student.sisProfile.preferredName"></span>
          </div>
          <div id="student-bio-sid" class="font-size-14 font-weight-bold mb-1">
            SID <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.sid }}</span>
            <span
              v-if="academicCareerStatus === 'Inactive'"
              id="student-bio-inactive"
              class="red-flag-status ml-1">
              INACTIVE
            </span>
            <span
              v-if="academicCareerStatus === 'Completed'"
              class="ml-1"
              uib-tooltip="Graduated"
              tooltip-placement="bottom">
              <font-awesome icon="graduation-cap" />
            </span>
          </div>
          <StudentAcademicStanding v-if="student.academicStanding" :standing="student.academicStanding[0]" />
          <div v-if="student.sisProfile.emailAddress" class="mt-2">
            <span class="sr-only">Email</span>
            <a
              id="student-mailto"
              :href="`mailto:${student.sisProfile.emailAddress}`"
              :class="{'demo-mode-blur': $currentUser.inDemoMode}"
              target="_blank">
              {{ student.sisProfile.emailAddress }}<span class="sr-only"> (will open new browser tab)</span>
            </a>
          </div>
        </div>
        <div v-if="isAscInactive" id="student-bio-inactive-asc" class="font-weight-bolder has-error">
          ASC INACTIVE
        </div>
        <div v-if="isCoeInactive" id="student-bio-inactive-coe" class="font-weight-bolder has-error">
          CoE INACTIVE
        </div>
        <div id="student-bio-level" class="mt-2">
          <h3 class="sr-only">Level</h3>
          <div class="font-weight-bolder">{{ get(student, 'sisProfile.level.description') }}</div>
        </div>
        <div class="text-muted">
          <div v-if="student.sisProfile.termsInAttendance" id="student-bio-terms-in-attendance">
            {{ 'Term' | pluralize(student.sisProfile.termsInAttendance) }} in Attendance
          </div>
          <div
            v-if="student.sisProfile.expectedGraduationTerm && get(student.sisProfile, 'level.code') !== 'GR'"
            id="student-bio-expected-graduation">
            Expected graduation {{ student.sisProfile.expectedGraduationTerm.name }}
          </div>
          <div v-if="student.athleticsProfile" id="student-bio-athletics">
            <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName">
              {{ membership.groupName }}
            </div>
          </div>
        </div>
      </div>
      <div class="col-sm mr-2 pr-2">
        <div v-if="academicCareerStatus !== 'Completed'">
          <div v-if="plansPartitionedByStatus[0].length" id="student-bio-majors" class="mb-3">
            <h3 class="student-profile-section-header">Major</h3>
            <StudentProfilePlan
              v-for="plan in plansPartitionedByStatus[0]"
              :key="plan.description"
              :plan="plan"
              :active="true" />
          </div>
          <div v-if="plansMinorPartitionedByStatus[0].length" id="student-bio-minors" class="mb-3">
            <h3 class="student-profile-section-header">Minor</h3>
            <StudentProfilePlan
              v-for="plan in plansMinorPartitionedByStatus[0]"
              :key="plan.description"
              :plan="plan"
              :active="true" />
          </div>
          <div v-if="!isEmpty(student.sisProfile.subplans)" id="student-bio-subplans" class="mb-3">
            <h3 class="student-profile-section-header">Subplan</h3>
            <div
              v-for="subplan in student.sisProfile.subplans"
              :key="subplan"
              class="font-weight-bolder mb-2">
              {{ subplan }}
            </div>
          </div>
          <div v-if="!plansPartitionedByStatus[0].length && plansPartitionedByStatus[1].length" id="student-details-discontinued-majors-outer" class="mb-3">
            <h3 class="student-profile-section-header">
              Discontinued Major(s)
            </h3>
            <div id="student-details-discontinued-majors">
              <StudentProfilePlan
                v-for="plan in plansPartitionedByStatus[1]"
                :key="plan.description"
                :plan="plan"
                :active="false" />
            </div>
          </div>
          <div v-if="!plansPartitionedByStatus[0].length && plansMinorPartitionedByStatus[1].length" id="student-details-discontinued-minors-outer" class="mb-3">
            <h3 class="student-profile-section-header">
              Discontinued Minor(s)
            </h3>
            <div id="student-details-discontinued-minors">
              <StudentProfilePlan
                v-for="plan in plansMinorPartitionedByStatus[1]"
                :key="plan.description"
                :plan="plan"
                :active="false" />
            </div>
          </div>
        </div>
        <div v-if="academicCareerStatus === 'Completed' && student.sisProfile.degree" class="mb-3">
          <h3 class="student-profile-section-header">Degree</h3>
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
    <div class="d-flex justify-content-center pb-2">
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
      <StudentPersonalDetails
        :inactive-majors="belowTheFoldMajors"
        :inactive-minors="belowTheFoldMinors"
        :is-open="isShowingPersonalDetails"
        :student="student" />
    </div>
  </div>
</template>

<script>
import StudentAcademicStanding from "@/components/student/profile/StudentAcademicStanding";
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentGroupSelector from '@/components/student/profile/StudentGroupSelector';
import StudentMetadata from '@/mixins/StudentMetadata';
import StudentPersonalDetails from "@/components/student/profile/StudentPersonalDetails";
import StudentProfilePlan from "@/components/student/profile/StudentProfilePlan";
import Util from '@/mixins/Util';

export default {
  name: 'StudentProfileHeader',
  components: {
    StudentAcademicStanding,
    StudentAvatar,
    StudentGroupSelector,
    StudentPersonalDetails,
    StudentProfilePlan
  },
  mixins: [StudentMetadata, Util],
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
    belowTheFoldMajors() {
      // Send inactive majors below the fold only if we have active majors to show above the fold.
      return this.plansPartitionedByStatus[0].length ? this.plansPartitionedByStatus[1] : [];
    },
    belowTheFoldMinors() {
      // Send inactive minors below the fold only if we have active majors to show above the fold.
      return this.plansPartitionedByStatus[0].length ? this.plansMinorPartitionedByStatus[1] : [];
    },
    plansPartitionedByStatus() {
      return this.partition(this.student.sisProfile.plans, (p) => p.status === 'Active');
    },
    plansMinorPartitionedByStatus() {
      return this.partition(this.student.sisProfile.plansMinor, (p) => p.status === 'Active');
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

<style>
.student-profile-section-header {
  border-bottom: 1px #999 solid;
  color: #999;
  font-size: 12px;
  font-weight: bold;
  margin: 0 0 5px 0;
  padding: 0 0 5px 0;
  text-transform: uppercase;
}
</style>
