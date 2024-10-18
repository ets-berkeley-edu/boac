<template>
  <div aria-labelledby="student-name-header student-name-header-sr" class="d-flex flex-wrap mr-4 pb-2 pt-4" role="region">
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
      :inactive-majors="size(plansPartitionedByStatus[0]) ? plansPartitionedByStatus[1] : []"
      :inactive-minors="size(plansMinorPartitionedByStatus[0]) ? plansMinorPartitionedByStatus[1] : []"
      :inactive-subplans="size(plansPartitionedByStatus[0]) ? discontinuedSubplans : []"
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
import {compact as _compact, map, partition, size} from 'lodash'
import {onMounted, ref} from 'vue'

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

const plansMinorPartitionedByStatus = ref([])
const plansPartitionedByStatus = ref([])
const discontinuedSubplans = ref([])

onMounted(() => {
  plansMinorPartitionedByStatus.value = partition(props.student.sisProfile.plansMinor, (p) => p.status === 'Active')
  plansPartitionedByStatus.value = partition(props.student.sisProfile.plans, (p) => p.status === 'Active')
  discontinuedSubplans.value = _compact(map(plansPartitionedByStatus.value[1], 'subplan'))
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
