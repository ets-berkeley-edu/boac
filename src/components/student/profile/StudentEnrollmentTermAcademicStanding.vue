<template>
  <div class="align-baseline d-flex flex-wrap mb-1">
    <h3 :id="`term-${term.termId}-header`" class="font-size-18">{{ term.termName }}</h3>
    <div v-if="isConcurrent" class="font-size-14 text-grey-darken-2">&nbsp;UCBX</div>
    <StudentAcademicStanding
      v-if="term.academicStanding"
      class="font-size-14 ml-1"
      :standing="term.academicStanding"
    />
    <StudentWithdrawalCancel
      v-if="student.sisProfile.withdrawalCancel"
      class="font-size-14 ml-1"
      :term-id="term.termId"
      :withdrawal="student.sisProfile.withdrawalCancel"
    />
  </div>
</template>

<script setup>
import StudentWithdrawalCancel from '@/components/student/profile/StudentWithdrawalCancel.vue'
import StudentAcademicStanding from '@/components/student/profile/StudentAcademicStanding.vue'
import {some} from 'lodash'

const props = defineProps({
  student: {
    required: true,
    type: Object
  },
  term: {
    required: true,
    type: Object
  }
})
const isConcurrent = some(props.term.enrollments, {'academicCareer': 'UCBX'})
</script>

<style scoped>

</style>
