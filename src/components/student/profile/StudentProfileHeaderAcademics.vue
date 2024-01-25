<template>
  <div>
    <div v-if="academicCareerStatus !== 'Completed'">
      <div v-if="plansPartitionedByStatus[0].length" id="student-bio-majors" class="mb-3">
        <h3 v-if="isGraduate(student)" class="student-profile-h3">Academic Plan</h3>
        <h3 v-if="!isGraduate(student)" class="student-profile-h3">Major</h3>
        <StudentProfilePlan
          v-for="plan in plansPartitionedByStatus[0]"
          :key="plan.description"
          :plan="plan"
          :active="true"
        />
      </div>
      <div v-if="plansMinorPartitionedByStatus[0].length" id="student-bio-minors" class="mb-3">
        <h3 v-if="plansMinorPartitionedByStatus[0].length > 1" class="student-profile-h3">Minors</h3>
        <h3 v-if="plansMinorPartitionedByStatus[0].length === 1" class="student-profile-h3">Minor</h3>
        <StudentProfilePlan
          v-for="plan in plansMinorPartitionedByStatus[0]"
          :key="plan.description"
          :plan="plan"
          :active="true"
        />
      </div>
      <div v-if="_size(activeSubplans)" id="student-bio-subplans" class="mb-3">
        <h3 class="student-profile-h3">{{ pluralize('Subplan', activeSubplans.length) }}</h3>
        <div
          v-for="(subplan, index) in activeSubplans"
          :key="index"
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
      <div v-if="!plansPartitionedByStatus[0].length && _size(discontinuedSubplans)" id="student-bio-subplans" class="mb-3">
        <h3 class="student-profile-h3">{{ pluralize('Discontinued Subplan', discontinuedSubplans.length) }}</h3>
        <div
          v-for="(subplan, index) in discontinuedSubplans"
          :key="index"
          class="font-weight-bolder mb-2"
        >
          {{ subplan }}
        </div>
      </div>
    </div>
    <div v-if="academicCareerStatus === 'Completed' && _size(student.sisProfile.degrees)" class="mb-3">
      <h3 class="student-profile-h3">Degree{{ _size(student.sisProfile.degrees) === 1 ? '' : 's' }}</h3>
      <div v-for="(degree, index) in student.sisProfile.degrees" :key="degree.plan">
        <div :id="`student-bio-degree-type-${index}`" class="font-weight-bolder" :class="{'mt-2': index > 0}">
          <span v-if="!_includes(degree.planOwners, 'Graduate Division')">
            {{ degree.description }} in
          </span>
          {{ degree.plans.filter(plan => planTypes.includes(plan.type)).map(degree => degree.plan).join(', ') }}
        </div>
        <div id="student-bio-degree-date">
          <span class="student-text">Awarded {{ moment(degree.dateAwarded).format('MMM DD, YYYY') }}</span>
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
          <span class="student-text">Awarded {{ moment(degree.dateAwarded).format('MMM DD, YYYY') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StudentMetadata from '@/mixins/StudentMetadata'
import StudentProfilePlan from '@/components/student/profile/StudentProfilePlan'
import Util from '@/mixins/Util'

export default {
  name: 'StudentProfileHeaderAcademics',
  mixins: [StudentMetadata, Util],
  components: {StudentProfilePlan},
  props: {
    compact: {
      required: false,
      type: Boolean
    },
    discontinuedSubplans: {
      default: () => [],
      required: false,
      type: Array
    },
    linkToStudentProfile: {
      required: false,
      type: Boolean
    },
    plansMinorPartitionedByStatus: {
      default: () => [],
      required: false,
      type: Array
    },
    plansPartitionedByStatus: {
      default: () => [],
      required: false,
      type: Array
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    academicCareerStatus: undefined,
    activeSubplans: undefined,
    planTypes: ['MAJ', 'SS', 'SP', 'SH', 'CRT']
  }),
  created() {
    this._each(this.student.sisProfile.degrees, degree => {
      degree.planOwners = this._uniq(this._map(degree.plans, 'group'))
      degree.minorPlans = degree.plans.filter(plan => plan.type === 'MIN').map(minor => minor.plan).map(part => part.replace('Minor in ', ''))
    })
    this.academicCareerStatus = this._get(this.student, 'sisProfile.academicCareerStatus')
    this.activeSubplans = this._compact(this._map(this.plansPartitionedByStatus[0], 'subplan'))
  }
}
</script>
