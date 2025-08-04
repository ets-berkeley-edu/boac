<template>
  <div class="text-medium-emphasis">
    <span :id="`${idPrefix}-university-department`">{{ peerAdvisingDepartment.deptName }}</span><!--
    --><span v-if="peerAdvisingDepartment.name !== peerAdvisingDepartment.deptName" :id="`${idPrefix}-peer-advising-department`">, {{ peerAdvisingDepartment.name }}</span>
  </div>
</template>

<script setup lang="ts">
import {findPeerAdvisingDepartment} from '@/lib/berkeley-department'

const props = defineProps({
  idPrefix: {
    required: true,
    type: String
  },
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  }
})

const peerAdvisingDepartment = findPeerAdvisingDepartment(props.peerAdvisingDepartmentId)
</script>
