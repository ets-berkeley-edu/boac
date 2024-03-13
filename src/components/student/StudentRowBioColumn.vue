<template>
  <div>
    <div>
      <div>
        <router-link
          v-if="student.uid"
          :id="`link-to-student-${student.uid}`"
          :to="studentRoutePath(student.uid, currentUser.inDemoMode)"
        >
          <h3
            v-if="sortedBy !== 'first_name'"
            :id="`row-${rowIndex}-student-name`"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            class="student-name"
            v-html="lastNameFirst(student)"
          />
          <h3
            v-if="sortedBy === 'first_name'"
            :id="`row-${rowIndex}-student-name`"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            class="student-name"
          >
            {{ student.firstName }} {{ student.lastName }}
          </h3>
        </router-link>
        <span v-if="!student.uid">
          <span
            v-if="sortedBy === 'first_name'"
            :id="`student-${student.sid}-has-no-uid`"
            class="font-weight-500 student-name"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            v-html="lastNameFirst(student)"
          />
          <span
            v-if="sortedBy !== 'first_name'"
            :id="`student-${student.sid}-has-no-uid`"
            class="font-size-16 m-0"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
          >
            {{ student.firstName }} {{ student.lastName }}
          </span>
        </span>
      </div>
    </div>
    <div :class="{'demo-mode-blur': currentUser.inDemoMode}" class="d-flex student-sid">
      <div :id="`row-${rowIndex}-student-sid`">{{ student.sid }}</div>
      <div
        v-if="student.academicCareerStatus === 'Inactive'"
        :id="`row-${rowIndex}-inactive`"
        class="red-flag-status ml-1"
      >
        INACTIVE
      </div>
      <div
        v-if="student.academicCareerStatus === 'Completed'"
        class="ml-1"
        uib-tooltip="Graduated"
        tooltip-placement="bottom"
      >
        <v-icon :icon="mdiSchool" />
      </div>
    </div>
    <div
      v-if="displayAsAscInactive(student)"
      :id="`row-${rowIndex}-inactive-asc`"
      class="d-flex student-sid red-flag-status"
    >
      ASC INACTIVE
    </div>
    <div
      v-if="displayAsCoeInactive(student)"
      :id="`row-${rowIndex}-inactive-coe`"
      class="d-flex student-sid red-flag-status"
    >
      CoE INACTIVE
    </div>
    <div v-if="student.withdrawalCancel" :id="`row-${rowIndex}-withdrawal-cancel`">
      <span class="red-flag-small">
        {{ student.withdrawalCancel.description }}
        {{ DateTime.fromJSDate(student.withdrawalCancel.date).toFormat('MMM DD, YYYY') }}
      </span>
    </div>
    <StudentAcademicStanding v-if="student.academicStanding" :standing="student.academicStanding" :row-index="`row-${rowIndex}`" />
    <div v-if="student.academicCareerStatus !== 'Completed'">
      <div
        :id="`row-${rowIndex}-student-level`"
        class="student-text"
      >
        {{ student.level }}
      </div>
      <div
        v-if="student.matriculation"
        :id="`row-${rowIndex}-student-matriculation`"
        class="student-text"
        aria-label="Entering term"
      >
        Entered {{ student.matriculation }}
      </div>
      <div
        v-if="student.expectedGraduationTerm"
        :id="`row-${rowIndex}-student-grad-term`"
        class="student-text"
        aria-label="Expected graduation term"
      >
        Grad:&nbsp;{{ student.expectedGraduationTerm.name }}
      </div>
      <div
        v-if="student.termsInAttendance"
        :id="`row-${rowIndex}-student-terms-in-attendance`"
        class="student-text"
        aria-label="Terms in attendance"
      >
        Terms in Attendance:&nbsp;{{ student.termsInAttendance }}
      </div>
      <div
        v-for="(major, index) in student.majors"
        :key="index"
        class="student-text"
      >
        <span :id="`row-${rowIndex}-student-major-${index}`">{{ major }}</span>
      </div>
    </div>
    <div v-if="student.academicCareerStatus === 'Completed'">
      <div
        v-if="student.matriculation"
        :id="`row-${rowIndex}-student-matriculation`"
        class="student-text"
        aria-label="Entering term"
      >
        Entered {{ student.matriculation }}
      </div>
      <DegreesAwarded :student="student" />
      <div v-for="owner in degreePlanOwners" :key="owner" class="student-text">
        <span class="student-text">{{ owner }}</span>
      </div>
    </div>
    <div v-if="student.athleticsProfile" class="student-teams-container">
      <div
        v-for="(team, index) in student.athleticsProfile.athletics"
        :key="index"
        class="student-text"
      >
        <span :id="`row-${rowIndex}-student-team-${index}`">{{ team.groupName }}</span>
        <span v-if="student.athleticsProfile.isActiveAsc === false"> (Inactive)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiSchool} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import DegreesAwarded from '@/components/student/DegreesAwarded'
import StudentAcademicStanding from '@/components/student/profile/StudentAcademicStanding'
import Util from '@/mixins/Util.vue'
import {displayAsAscInactive, displayAsCoeInactive} from '@/berkeley'
import {DateTime} from 'luxon'

export default {
  name: 'StudentRowBioColumn',
  components: {DegreesAwarded, StudentAcademicStanding},
  mixins: [Context, Util],
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
      const plans = this._get(this.student, 'degree.plans')
      if (plans) {
        return this._uniq(this._map(plans, 'group'))
      } else {
        return []
      }
    }
  },
  methods: {
    displayAsAscInactive,
    displayAsCoeInactive
  }
}
</script>
