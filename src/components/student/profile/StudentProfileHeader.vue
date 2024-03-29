<template>
  <div id="student-profile-header">
    <div class="d-flex justify-content-between mr-4" :class="{'pb-0 pt-2': compact, 'pb-2 pt-4': !compact}">
      <div class="d-flex flex-row-reverse" :class="{'ml-3': compact, 'ml-5': !compact}">
        <div :class="{'mr-2 pr-2': compact, 'mr-4 pr-4': !compact}">
          <StudentProfileHeaderBio
            :compact="compact"
            :link-to-student-profile="linkToStudentProfile"
            :student="student"
          />
        </div>
        <div class="text-center" :class="{'column-with-avatar-compact': compact, 'column-with-avatar': !compact}">
          <StudentAvatar class="mb-2" :size="compact ? 'medium' : 'large'" :student="student" />
          <ManageStudent
            v-if="!compact"
            domain="default"
            label-class="px-2"
            :student="student"
          />
        </div>
      </div>
      <div class="mr-5">
        <StudentProfileHeaderAcademics
          :discontinued-subplans="discontinuedSubplans"
          :plans-minor-partitioned-by-status="plansMinorPartitionedByStatus"
          :plans-partitioned-by-status="plansPartitionedByStatus"
          :student="student"
        />
      </div>
    </div>
    <div v-if="!compact">
      <div class="d-flex justify-content-center pb-2">
        <div>
          <v-btn
            id="show-hide-personal-details"
            :aria-expanded="isShowingPersonalDetails"
            class="no-wrap"
            variant="link"
            @click="toggleShowDetails"
          >
            <v-icon :icon="isShowingPersonalDetails ? mdiMenuDown : mdiMenuRight" :class="isShowingPersonalDetails ? 'mr-1' : 'ml-1 mr-1'" />
            {{ isShowingPersonalDetails ? 'Hide' : 'Show' }} Personal Details
          </v-btn>
        </div>
      </div>
      <div>
        <StudentPersonalDetails
          :inactive-majors="plansPartitionedByStatus[0].length ? plansPartitionedByStatus[1] : []"
          :inactive-minors="plansMinorPartitionedByStatus[0].length ? plansMinorPartitionedByStatus[1] : []"
          :inactive-subplans="plansPartitionedByStatus[0].length ? discontinuedSubplans : []"
          :is-open="isShowingPersonalDetails"
          :student="student"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import StudentAvatar from '@/components/student/StudentAvatar'
import StudentPersonalDetails from '@/components/student/profile/StudentPersonalDetails'
import StudentProfileHeaderAcademics from '@/components/student/profile/StudentProfileHeaderAcademics'
import StudentProfileHeaderBio from '@/components/student/profile/StudentProfileHeaderBio'
import Util from '@/mixins/Util'

export default {
  name: 'StudentProfileHeader',
  components: {
    ManageStudent,
    StudentAvatar,
    StudentPersonalDetails,
    StudentProfileHeaderAcademics,
    StudentProfileHeaderBio
  },
  mixins: [Context, Util],
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
    discontinuedSubplans: undefined,
    isShowingPersonalDetails: false,
    plansMinorPartitionedByStatus: undefined,
    plansPartitionedByStatus: undefined
  }),
  created() {
    this.plansMinorPartitionedByStatus = this._partition(this.student.sisProfile.plansMinor, (p) => p.status === 'Active')
    this.plansPartitionedByStatus = this._partition(this.student.sisProfile.plans, (p) => p.status === 'Active')
    this.discontinuedSubplans = this._compact(this._map(this.plansPartitionedByStatus[1], 'subplan'))
  },
  mounted() {
    this.putFocusNextTick('student-name-header')
  },
  methods: {
    toggleShowDetails() {
      this.isShowingPersonalDetails = !this.isShowingPersonalDetails
      this.alertScreenReader(`Student details are ${this.isShowingPersonalDetails ? 'showing' : 'hidden'}.`)
    }
  }
}
</script>

<style>
.column-with-avatar {
  margin: 0 64px 0 20px;
  vertical-align: center;
}
.column-with-avatar-compact {
  margin: 16px 32px 0 20px;
  vertical-align: center;
}
</style>
