<template>
  <div class="d-flex flex-wrap mr-4 pb-2 pt-4">
    <div class="d-flex ml-3 me-auto">
      <div class="text-center" :class="{'column-with-avatar-compact': compact, 'column-with-avatar': !compact}">
        <StudentAvatar :size="compact ? 'medium' : 'large'" :student="student" />
        <ManageStudent
          v-if="!compact"
          button-variant="flat"
          domain="default"
          :student="student"
        />
      </div>
      <StudentProfileHeaderBio
        :compact="compact"
        :link-to-student-profile="linkToStudentProfile"
        :student="student"
      />
    </div>
    <div class="ml-3 mr-12" :class="{'pl-6 pt-3': $vuetify.display.mdAndDown}">
      <StudentProfileHeaderAcademics
        :discontinued-subplans="discontinuedSubplans"
        :plans-minor-partitioned-by-status="plansMinorPartitionedByStatus"
        :plans-partitioned-by-status="plansPartitionedByStatus"
        :student="student"
      />
    </div>
  </div>
  <div class="text-center">
    <StudentPersonalDetails
      v-if="!compact"
      :inactive-majors="plansPartitionedByStatus[0].length ? plansPartitionedByStatus[1] : []"
      :inactive-minors="plansMinorPartitionedByStatus[0].length ? plansMinorPartitionedByStatus[1] : []"
      :inactive-subplans="plansPartitionedByStatus[0].length ? discontinuedSubplans : []"
      :student="student"
    />
  </div>
</template>

<script setup>
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import StudentAvatar from '@/components/student/StudentAvatar'
import StudentPersonalDetails from '@/components/student/profile/StudentPersonalDetails'
import StudentProfileHeaderAcademics from '@/components/student/profile/StudentProfileHeaderAcademics'
import StudentProfileHeaderBio from '@/components/student/profile/StudentProfileHeaderBio'
import {compact as _compact, map, partition} from 'lodash'
import {onMounted} from 'vue'
import {putFocusNextTick} from '@/lib/utils'

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

const plansMinorPartitionedByStatus = partition(props.student.sisProfile.plansMinor, (p) => p.status === 'Active')
const plansPartitionedByStatus = partition(props.student.sisProfile.plans, (p) => p.status === 'Active')
const discontinuedSubplans = _compact(map(plansPartitionedByStatus[1], 'subplan'))

onMounted(() => {
  putFocusNextTick('student-name-header')
})
</script>

<style>
.column-with-avatar {
  margin: 0 48px;
  vertical-align: center;
}
.column-with-avatar-compact {
  margin: 16px 32px 0 20px;
  vertical-align: center;
}
</style>
