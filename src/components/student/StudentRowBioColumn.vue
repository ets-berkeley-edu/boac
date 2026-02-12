<template>
  <div>
    <router-link
      v-if="student.uid"
      :id="`link-to-student-${student.uid}`"
      :to="studentRoutePath(student.uid, currentUser.inDemoMode)"
      class="font-size-16 font-weight-bold"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
    >
      {{ studentName }} <span class="sr-only">Profile page</span>
    </router-link>
    <span
      v-if="!student.uid"
      :id="`student-${student.sid}-has-no-uid`"
      class="font-size-16 font-weight-500"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
    >
      {{ studentName }}
    </span>
    <div class="d-flex align-center font-weight-bold font-size-13">
      <div :id="`row-${rowIndex}-student-sid`" :class="{'demo-mode-blur': currentUser.inDemoMode}">
        <span class="sr-only">S I D</span> {{ student.sid }}
      </div>
      <div
        v-if="student.academicCareerStatus === 'Inactive'"
        :id="`row-${rowIndex}-inactive`"
        class="text-error ml-1"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
      >
        INACTIVE
      </div>
      <v-icon
        v-if="student.academicCareerStatus === 'Completed'"
        aria-label="Graduated"
        class="ml-1"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        :icon="mdiSchool"
        size="small"
      />
    </div>
    <div
      v-if="displayAsAscInactive(student)"
      :id="`row-${rowIndex}-inactive-asc`"
      class="text-error font-weight-bold font-size-13 text-no-wrap"
    >
      ASC INACTIVE
    </div>
    <div
      v-if="displayAsCoeInactive(student)"
      :id="`row-${rowIndex}-inactive-coe`"
      class="text-error font-weight-bold font-size-13 text-no-wrap"
    >
      CoE INACTIVE
    </div>
    <div
      v-if="student.withdrawalCancel"
      :id="`row-${rowIndex}-withdrawal-cancel`"
      class="text-error font-weight-bold font-size-13 text-no-wrap"
    >
      {{ student.withdrawalCancel.description }}
      <Date :date="student.withdrawalCancel.date" />
    </div>
    <StudentAcademicStanding
      v-if="student.academicStanding"
      class="font-size-13"
      :id-prefix="`student-${student.sid}`"
      :standing="student.academicStanding"
    />
    <div
      v-if="displayCoeAcademicStanding(student)"
      :id="`row-${rowIndex}-acad-standing-coe`"
      class="text-error font-weight-bold font-size-13"
    >
      {{ student.coeProfile.acadStatusDescription }} ({{ termNameForSisId(student.coeProfile.acadStatusTermId) }}, COE)
    </div>
    <dl
      v-if="student.academicCareerStatus !== 'Completed'"
      class="font-size-13 text-medium-emphasis"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
    >
      <dt class="sr-only">Level</dt>
      <dd :id="`row-${rowIndex}-student-level`" class="ma-0 ml-0">
        {{ student.level }}
      </dd>
      <template v-if="student.matriculation">
        <dt class="sr-only">Entering term</dt>
        <dd :id="`row-${rowIndex}-student-matriculation`" class="ma-0 ml-0">
          Entered {{ student.matriculation }}
        </dd>
      </template>
      <template v-if="student.expectedGraduationTerm">
        <dt class="sr-only">Expected graduation term</dt>
        <dd :id="`row-${rowIndex}-student-grad-term`" class="ma-0 ml-0">
          <span aria-hidden="true">Grad:</span>
          {{ student.expectedGraduationTerm.name }}
        </dd>
      </template>
      <template v-if="student.termsInAttendance">
        <dt>Terms in attendance</dt>
        <dd :id="`row-${rowIndex}-student-terms-in-attendance`" class="ma-0 ml-0">
          {{ student.termsInAttendance }}
        </dd>
      </template>
      <template v-if="student.majors && student.majors.length">
        <dt class="sr-only">Major</dt>
        <dd
          v-for="(major, index) in student.majors"
          :id="`row-${rowIndex}-student-major-${index}`"
          :key="index"
          class="ma-0 ml-0"
        >
          {{ major }}
        </dd>
      </template>
    </dl>
    <div v-if="student.academicCareerStatus === 'Completed'" class="font-size-13 text-medium-emphasis">
      <dl v-if="student.matriculation" class="ma-0">
        <dt class="sr-only">Entering term</dt>
        <dd :id="`row-${rowIndex}-student-matriculation`" class="ma-0 ml-0">
          Entered {{ student.matriculation }}
        </dd>
      </dl>
      <DegreesAwarded :student="student" />
      <div v-for="(owner, index) in degreePlanOwners" :key="owner">
        <span :id="`row-${rowIndex}-student-degree-plan-owner-${index}`">{{ owner }}</span>
      </div>
    </div>
    <div v-if="student.athleticsProfile" class="student-teams-container font-size-13 text-medium-emphasis">
      <div
        v-for="(team, index) in student.athleticsProfile.athletics"
        :key="index"
      >
        <span :id="`row-${rowIndex}-student-team-${index}`">{{ team.groupName }}</span>
        <span v-if="student.athleticsProfile.isActiveAsc === false"> (Inactive)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import {get, map, uniq} from 'lodash'
import {mdiSchool} from '@mdi/js'
import Date from '@/components/util/Date.vue'
import DegreesAwarded from '@/components/student/DegreesAwarded'
import StudentAcademicStanding from '@/components/student/profile/StudentAcademicStanding'
import {displayAsAscInactive, displayAsCoeInactive, displayCoeAcademicStanding} from '@/lib/student'
import {lastNameFirst, studentRoutePath} from '@/lib/utils'
import {termNameForSisId} from '@/lib/berkeley-utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  rowIndex: {
    required: true,
    type: Number
  },
  sortedBy: {
    required: true,
    type: String
  },
  student: {
    required: true,
    type: Object
  }
})

const currentUser = useContextStore().currentUser

const degreePlanOwners = computed(() => {
  const plans = get(props.student, 'degree.plans')
  return plans ? uniq(map(plans, 'group')) : []
})
const studentName = computed(() => {
  return props.sortedBy === 'first_name' ? `${props.student.firstName} ${props.student.lastName}` : lastNameFirst(props.student)
})
</script>
