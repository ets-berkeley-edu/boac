<template>
  <div aria-labelledby="student-name-header student-name-header-sr" class="d-flex flex-wrap mr-4 pb-2 pt-4" role="region">
    <div class="d-flex flex-row-reverse me-auto">
      <StudentProfileHeaderBio
        :compact="compact"
        :link-to-student-profile="linkToStudentProfile"
        :student="student"
        :suppress-grad-programs="suppressGradPrograms"
      />
      <div class="text-center" :class="{'column-with-avatar-compact': compact, 'column-with-avatar': !compact}">
        <StudentAvatar :size="compact ? 'medium' : 'large'" :student="student" />
        <ManageStudent
          v-if="!compact"
          class="manage-student"
          domain="default"
          :student="student"
        />
      </div>
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
import {compact as _compact, map, partition, size} from 'lodash'
import {onMounted, ref} from 'vue'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import StudentAvatar from '@/components/student/StudentAvatar'
import StudentPersonalDetails from '@/components/student/profile/StudentPersonalDetails'
import StudentProfileHeaderAcademics from '@/components/student/profile/StudentProfileHeaderAcademics'
import StudentProfileHeaderBio from '@/components/student/profile/StudentProfileHeaderBio'

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
  },
  suppressGradPrograms: {
    required: false,
    type: Boolean
  }
})

const plansMinorPartitionedByStatus = ref([])
const plansPartitionedByStatus = ref([])
const discontinuedSubplans = ref([])

onMounted(() => {
  if (!(props.suppressGradPrograms && props.student.sisProfile.academicCareer === 'GRAD')) {
    const planFilter = p => p.status === 'Active'
    plansMinorPartitionedByStatus.value = partition(props.student.sisProfile.plansMinor, planFilter)
    plansPartitionedByStatus.value = partition(props.student.sisProfile.plans, planFilter)
    discontinuedSubplans.value = _compact(map(plansPartitionedByStatus.value[1], 'subplan'))
  }
})
</script>

<style>
.column-with-avatar {
  margin: 0 36px;
  vertical-align: center;
}
.column-with-avatar-compact {
  margin: 16px 32px 0 20px;
  vertical-align: center;
}
.manage-student {
  min-width: 170px;
}
</style>
