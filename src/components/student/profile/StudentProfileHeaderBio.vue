<template>
  <div>
    <div>
      <router-link v-if="linkToStudentProfile" :to="`/student/${student.uid}`">
        <h1
          id="student-name-header"
          class="mb-1"
          :class="{
            'demo-mode-blur': currentUser.inDemoMode,
            'font-size-20 font-weight-bold mb-1': compact,
            'student-section-header': !compact
          }"
          v-html="student.name"
        />
      </router-link>
      <h1
        v-if="!linkToStudentProfile"
        id="student-name-header"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        class="mb-1 student-section-header"
        v-html="student.name"
      />
      <h2 id="student-name-header-sr" class="sr-only">Profile</h2>
      <div
        v-if="student.sisProfile.preferredName !== student.name"
        id="student-preferred-name"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
      >
        <span class="sr-only">Preferred name</span>
        <span v-html="student.sisProfile.preferredName" />
      </div>
      <div
        v-if="get(student, 'sisProfile.pronouns.description')"
        id="student-pronouns"
        class="text-medium-emphasis font-size-14 mb-1"
      >
        Pronouns: {{ student.sisProfile.pronouns.description }}
      </div>
      <div id="student-bio-sid" class="align-center d-flex font-size-14 font-weight-bold">
        <div class="mr-1">
          SID <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.sid }}</span>
        </div>
        <div
          v-if="academicCareerStatus === 'Inactive'"
          id="student-bio-inactive"
          class="font-weight-bold mr-1 text-error"
        >
          INACTIVE
        </div>
        <div
          v-if="academicCareerStatus === 'Completed'"
          aria-label="Graduated"
        >
          <v-icon :icon="mdiSchool" />
          <v-tooltip activator="parent" location="bottom">
            Graduated
          </v-tooltip>
        </div>
      </div>
      <StudentAcademicStanding
        v-if="get(student, 'sisProfile.academicStanding')"
        id-prefix="profile"
        :standing="student.sisProfile.academicStanding"
      />
      <div v-if="!compact">
        <div v-if="student.sisProfile.emailAddress">
          <a
            id="student-mailto"
            :href="`mailto:${student.sisProfile.emailAddress}`"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            target="_blank"
          >
            <span class="sr-only">Email student at </span> {{ student.sisProfile.emailAddress }} <span class="sr-only"> (will open new browser tab)</span>
          </a>
        </div>
      </div>
      <div v-if="isAscInactive" id="student-bio-inactive-asc" class="font-weight-bold text-error">
        ASC INACTIVE
      </div>
      <div v-if="isCoeInactive" id="student-bio-inactive-coe" class="font-weight-bold text-error">
        CoE INACTIVE
      </div>
    </div>
    <div id="student-bio-level" :class="{'mt-2': !compact}">
      <h3 class="sr-only">Level</h3>
      <div class="font-weight-medium">{{ get(student, 'sisProfile.level.description') }}</div>
    </div>
    <div class="text-medium-emphasis">
      <div v-if="student.sisProfile.termsInAttendance" id="student-bio-terms-in-attendance">
        {{ pluralize('Term', student.sisProfile.termsInAttendance) }} in Attendance
      </div>
      <div
        v-if="student.sisProfile.expectedGraduationTerm && !['5', '6', '7', '8', 'GR'].includes(get(student.sisProfile, 'level.code'))"
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

<script setup>
import StudentAcademicStanding from '@/components/student/profile/StudentAcademicStanding'
import {displayAsAscInactive, displayAsCoeInactive} from '@/berkeley'
import {get} from 'lodash'
import {mdiSchool} from '@mdi/js'
import {pluralize} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
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
})

const academicCareerStatus = get(props.student, 'sisProfile.academicCareerStatus')
const currentUser = useContextStore().currentUser
const isAscInactive = displayAsAscInactive(props.student)
const isCoeInactive = displayAsCoeInactive(props.student)
</script>
