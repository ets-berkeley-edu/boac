<template>
  <div>
    <div>
      <div v-if="linkToStudentProfile">
        <router-link :to="`/student/${student.uid}`">
          <h1
            :class="{
              'demo-mode-blur': $currentUser.inDemoMode,
              'font-size-20 font-weight-bolder mb-1': compact,
              'student-section-header': !compact
            }"
            v-html="student.name"
          ></h1>
        </router-link>
      </div>
      <h1
        v-if="!linkToStudentProfile"
        id="student-name-header"
        :class="{'demo-mode-blur': $currentUser.inDemoMode}"
        class="student-section-header"
        v-html="student.name"
      ></h1>
      <h2 class="sr-only">Profile</h2>
      <div
        v-if="student.sisProfile.preferredName !== student.name"
        id="student-preferred-name"
        :class="{'demo-mode-blur': $currentUser.inDemoMode}"
      >
        <span class="sr-only">Preferred name</span>
        <span v-html="student.sisProfile.preferredName"></span>
      </div>
      <div
        v-if="_get(student, 'sisProfile.pronouns.description')"
        id="student-pronouns"
        class="student-text font-size-14 mb-1"
      >
        Pronouns: {{ student.sisProfile.pronouns.description }}
      </div>
      <div id="student-bio-sid" class="font-size-14 font-weight-bold mb-1">
        SID <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.sid }}</span>
        <span
          v-if="academicCareerStatus === 'Inactive'"
          id="student-bio-inactive"
          class="red-flag-status ml-1"
        >
          INACTIVE
        </span>
        <span
          v-if="academicCareerStatus === 'Completed'"
          class="ml-1"
          uib-tooltip="Graduated"
          aria-label="Graduated"
          tooltip-placement="bottom"
        >
          <font-awesome icon="graduation-cap" />
        </span>
      </div>
      <StudentAcademicStanding v-if="_get(student, 'sisProfile.academicStanding')" :standing="student.sisProfile.academicStanding" />
      <div v-if="!compact">
        <div v-if="student.sisProfile.emailAddress" class="mt-2">
          <a
            id="student-mailto"
            :href="`mailto:${student.sisProfile.emailAddress}`"
            :class="{'demo-mode-blur': $currentUser.inDemoMode}"
            target="_blank"
          >
            <span class="sr-only">Email student at </span> {{ student.sisProfile.emailAddress }}<span class="sr-only"> (will open new browser tab)</span>
          </a>
        </div>
      </div>
      <div v-if="isAscInactive" id="student-bio-inactive-asc" class="font-weight-bolder has-error">
        ASC INACTIVE
      </div>
      <div v-if="isCoeInactive" id="student-bio-inactive-coe" class="font-weight-bolder has-error">
        CoE INACTIVE
      </div>
    </div>
    <div id="student-bio-level" :class="{'mt-2': !compact}">
      <h3 class="sr-only">Level</h3>
      <div class="font-weight-bolder">{{ _get(student, 'sisProfile.level.description') }}</div>
    </div>
    <div class="text-muted">
      <div v-if="student.sisProfile.termsInAttendance" id="student-bio-terms-in-attendance">
        {{ pluralize('Term', student.sisProfile.termsInAttendance) }} in Attendance
      </div>
      <div
        v-if="student.sisProfile.expectedGraduationTerm && !['5', '6', '7', '8', 'GR'].includes(_get(student.sisProfile, 'level.code'))"
        id="student-bio-expected-graduation"
      >
        Expected graduation {{ student.sisProfile.expectedGraduationTerm.name }}
      </div>
      <div v-if="student.athleticsProfile" id="student-bio-athletics">
        <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName">
          {{ membership.groupName }}
          <span v-if="student.athleticsProfile.isActiveAsc === false"> (Inactive)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StudentAcademicStanding from '@/components/student/profile/StudentAcademicStanding'
import StudentMetadata from '@/mixins/StudentMetadata'
import Util from '@/mixins/Util'

export default {
  name: 'StudentProfileHeaderBio',
  components: {StudentAcademicStanding},
  mixins: [StudentMetadata, Util],
  props: {
    compact: {
      required: false,
      type: Boolean
    },
    linkToStudentProfile: {
      required: false,
      type: Boolean
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    academicCareerStatus: undefined,
    isAscInactive: undefined,
    isCoeInactive: undefined
  }),
  created() {
    this.academicCareerStatus = this._get(this.student, 'sisProfile.academicCareerStatus')
    this.isAscInactive = this.displayAsAscInactive(this.student)
    this.isCoeInactive = this.displayAsCoeInactive(this.student)
  }
}
</script>
