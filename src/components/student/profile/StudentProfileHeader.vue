<template>
  <div class="d-flex justify-space-between mr-4" :class="{'pb-0 pt-2': compact, 'pb-2 pt-4': !compact}">
    <div class="d-flex flex-row-reverse" :class="{'ml-3': compact, 'ml-12': !compact}">
      <StudentProfileHeaderBio
        :class="{'mx-2 pr-2': compact, 'mx-4 pr-4': !compact}"
        :compact="compact"
        :link-to-student-profile="linkToStudentProfile"
        :student="student"
      />
      <div class="text-center" :class="{'column-with-avatar-compact': compact, 'column-with-avatar': !compact}">
        <StudentAvatar :size="compact ? 'medium' : 'large'" :student="student" />
        <ManageStudent
          v-if="!compact"
          domain="default"
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
  <StudentPersonalDetails
    v-if="!compact"
    class="my-1 text-center"
    :inactive-majors="plansPartitionedByStatus[0].length ? plansPartitionedByStatus[1] : []"
    :inactive-minors="plansMinorPartitionedByStatus[0].length ? plansMinorPartitionedByStatus[1] : []"
    :inactive-subplans="plansPartitionedByStatus[0].length ? discontinuedSubplans : []"
    :student="student"
  />
</template>

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
