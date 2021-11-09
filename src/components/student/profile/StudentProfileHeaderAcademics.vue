<template>
  <div>
    <div v-if="academicCareerStatus !== 'Completed'">
      <div v-if="plansPartitionedByStatus[0].length" id="student-bio-majors" class="mb-3">
        <h3 class="student-profile-h3">Major</h3>
        <StudentProfilePlan
          v-for="plan in plansPartitionedByStatus[0]"
          :key="plan.description"
          :plan="plan"
          :active="true"
        />
      </div>
      <div v-if="plansMinorPartitionedByStatus[0].length" id="student-bio-minors" class="mb-3">
        <h3 v-if="plansMinorPartitionedByStatus.length > 1" class="student-profile-h3">Minors</h3>
        <h3 v-if="plansMinorPartitionedByStatus.length === 1" class="student-profile-h3">Minor</h3>
        <StudentProfilePlan
          v-for="plan in plansMinorPartitionedByStatus[0]"
          :key="plan.description"
          :plan="plan"
          :active="true"
        />
      </div>
      <div v-if="!$_.isEmpty(student.sisProfile.subplans)" id="student-bio-subplans" class="mb-3">
        <h3 class="student-profile-h3">{{ pluralize('Subplan', student.sisProfile.subplans.length) }}</h3>
        <div
          v-for="subplan in student.sisProfile.subplans"
          :key="subplan"
          class="font-weight-bolder mb-2"
        >
          {{ subplan }}
        </div>
      </div>
      <div v-if="!plansPartitionedByStatus[0].length && plansPartitionedByStatus[1].length" id="student-details-discontinued-majors-outer" class="mb-3">
        <h3 class="student-profile-h3">
          Discontinued Major(s)
        </h3>
        <div id="student-details-discontinued-majors">
          <StudentProfilePlan
            v-for="plan in plansPartitionedByStatus[1]"
            :key="plan.description"
            :plan="plan"
            :active="false"
          />
        </div>
      </div>
      <div v-if="!plansPartitionedByStatus[0].length && plansMinorPartitionedByStatus[1].length" id="student-details-discontinued-minors-outer" class="mb-3">
        <h3 class="student-profile-h3">
          Discontinued Minor(s)
        </h3>
        <div id="student-details-discontinued-minors">
          <StudentProfilePlan
            v-for="plan in plansMinorPartitionedByStatus[1]"
            :key="plan.description"
            :plan="plan"
            :active="false"
          />
        </div>
      </div>
    </div>
    <div v-if="academicCareerStatus === 'Completed' && $_.size(student.sisProfile.degrees)" class="mb-3">
      <h3 class="student-profile-h3">Degree{{ $_.size(student.sisProfile.degrees) === 1 ? '' : 's' }}</h3>
      <div v-for="(degree, index) in student.sisProfile.degrees" :key="degree.plan">
        <div :id="`student-bio-degree-type-${index}`" class="font-weight-bolder" :class="{'mt-2': index > 0}">
          <span v-if="!$_.includes(degree.planOwners, 'Graduate Division')">
            {{ degree.description }} in
          </span>
          {{ degree.plans.filter(plan => planTypes.includes(plan.type)).map(degree => degree.plan).join(', ') }}
        </div>
        <div id="student-bio-degree-date">
          <span class="student-text">Awarded {{ degree.dateAwarded | moment('MMM DD, YYYY') }}</span>
        </div>
        <div v-for="owner in degree.planOwners" :key="owner" class="student-text">
          <span class="student-text">{{ owner }}</span>
        </div>
        <div v-if="degree.minorPlans.length > 0">
          <h3 v-if="degree.minorPlans.length === 1" class="student-profile-h3 mt-3">Minor</h3>
          <h3 v-if="degree.minorPlans.length > 1" class="student-profile-h3 mt-3">Minors</h3>
          <div v-for="minorPlan in degree.minorPlans" :key="minorPlan">
            <div id="student-bio-degree-type" class="font-weight-bolder">
              {{ minorPlan + " UG" }}
            </div>
          </div>
          <span class="student-text">Awarded {{ degree.dateAwarded | moment('MMM DD, YYYY') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StudentProfilePlan from '@/components/student/profile/StudentProfilePlan'
import Util from '@/mixins/Util'

export default {
  name: 'StudentProfileHeaderAcademics',
  mixins: [Util],
  components: {StudentProfilePlan},
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
    plansMinorPartitionedByStatus: undefined,
    plansPartitionedByStatus: undefined,
    planTypes: ['MAJ', 'SS', 'SP', 'SH', 'CRT']
  }),
  created() {
    this.$_.each(this.student.sisProfile.degrees, degree => {
      degree.planOwners = this.$_.uniq(this.$_.map(degree.plans, 'group'))
      degree.minorPlans = degree.plans.filter(plan => plan.type === 'MIN').map(minor => minor.plan).map(part => part.replace('Minor in ', ''))
    })
    this.academicCareerStatus = this.$_.get(this.student, 'sisProfile.academicCareerStatus')
    this.plansMinorPartitionedByStatus = this.$_.partition(this.student.sisProfile.plansMinor, p => p.status === 'Active')
    this.plansPartitionedByStatus = this.$_.partition(this.student.sisProfile.plans, p => p.status === 'Active')
  }
}
</script>
