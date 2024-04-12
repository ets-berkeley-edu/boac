<template>
  <div>
    <div>
      <router-link
        v-if="student.uid"
        :id="`link-to-student-${student.uid}`"
        :to="studentRoutePath(student.uid, useContextStore().currentUser.inDemoMode)"
      >
        <h3
          :id="`row-${rowIndex}-student-name`"
          class="font-size-16"
          :class="{'demo-mode-blur': useContextStore().currentUser.inDemoMode}"
        >
          {{ studentName }}
        </h3>
      </router-link>
      <span
        v-if="!student.uid"
        :id="`student-${student.sid}-has-no-uid`"
        class="font-size-16 font-weight-500"
        :class="{'demo-mode-blur': useContextStore().currentUser.inDemoMode}"
      >
        {{ studentName }}
      </span>
    </div>
    <div
      :class="{'demo-mode-blur': useContextStore().currentUser.inDemoMode}"
      class="d-flex align-center font-weight-bold font-size-13"
    >
      <div :id="`row-${rowIndex}-student-sid`">{{ student.sid }}</div>
      <div
        v-if="student.academicCareerStatus === 'Inactive'"
        :id="`row-${rowIndex}-inactive`"
        class="text-error ml-1"
      >
        INACTIVE
      </div>
      <v-icon
        v-if="student.academicCareerStatus === 'Completed'"
        aria-label="Graduated"
        class="ml-1"
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
      {{ DateTime.fromSQL(student.withdrawalCancel.date).toLocaleString(DateTime.DATE_MED) }}
    </div>
    <StudentAcademicStanding
      v-if="student.academicStanding"
      class="font-size-14"
      :standing="student.academicStanding"
      :row-index="`row-${rowIndex}`"
    />
    <div v-if="student.academicCareerStatus !== 'Completed'" class="font-size-13 text-medium-emphasis">
      <div :id="`row-${rowIndex}-student-level`">
        {{ student.level }}
      </div>
      <div
        v-if="student.matriculation"
        :id="`row-${rowIndex}-student-matriculation`"
        aria-label="Entering term"
      >
        Entered {{ student.matriculation }}
      </div>
      <div
        v-if="student.expectedGraduationTerm"
        :id="`row-${rowIndex}-student-grad-term`"
        aria-label="Expected graduation term"
      >
        Grad:&nbsp;{{ student.expectedGraduationTerm.name }}
      </div>
      <div
        v-if="student.termsInAttendance"
        :id="`row-${rowIndex}-student-terms-in-attendance`"
        aria-label="Terms in attendance"
      >
        Terms in Attendance:&nbsp;{{ student.termsInAttendance }}
      </div>
      <div v-for="(major, index) in student.majors" :key="index">
        <span :id="`row-${rowIndex}-student-major-${index}`">{{ major }}</span>
      </div>
    </div>
    <div v-if="student.academicCareerStatus === 'Completed'" class="font-size-13 text-medium-emphasis">
      <div
        v-if="student.matriculation"
        :id="`row-${rowIndex}-student-matriculation`"
        aria-label="Entering term"
      >
        Entered {{ student.matriculation }}
      </div>
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
import {DateTime} from 'luxon'
import {displayAsAscInactive, displayAsCoeInactive} from '@/berkeley'
import {get, map, uniq} from 'lodash'
import {lastNameFirst, studentRoutePath} from '@/lib/utils'
import {mdiSchool} from '@mdi/js'
import {useContextStore} from '@/stores/context'
</script>

<script>
import DegreesAwarded from '@/components/student/DegreesAwarded'
import StudentAcademicStanding from '@/components/student/profile/StudentAcademicStanding'

export default {
  name: 'StudentRowBioColumn',
  components: {DegreesAwarded, StudentAcademicStanding},
  props: {
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
  },
  computed: {
    degreePlanOwners() {
      const plans = get(this.student, 'degree.plans')
      if (plans) {
        return uniq(map(plans, 'group'))
      } else {
        return []
      }
    },
    studentName() {
      return this.sortedBy === 'first_name' ? `${this.student.firstName} ${this.student.lastName}` : lastNameFirst(this.student)
    }
  }
}
</script>
