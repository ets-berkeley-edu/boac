<template>
  <div>
    <div v-for="department in user.departments" :key="department.deptCode">
      <div class="text-body">
        <span class="font-weight-bold text-success-darken-1">{{ department.deptName }}</span><span v-if="department.memberships.length === 1">, {{ getDistinctRoleNames(department.memberships)[0] }}</span>
      </div>
      <ul v-if="department.memberships.length > 1" class="ml-4">
        <li v-for="roleName in getDistinctRoleNames(department.memberships)" :key="roleName">
          {{ roleName }}
        </li>
      </ul>
    </div>
    <div v-if="user.canEditDegreeProgress || user.canReadDegreeProgress" class="mt-1 text-medium-emphasis">
      <span class="font-weight-bold text-medium-emphasis">Degree Progress: </span>
      <span v-if="user.canEditDegreeProgress && user.canReadDegreeProgress" class="text-body"> Read and write</span>
      <span v-if="!(user.canEditDegreeProgress && user.canReadDegreeProgress) && user.canReadDegreeProgress" class="text-body"> Read-only</span>
      <span v-if="user.automateDegreeProgressPermission" class="text-body"> (automated)</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import type {BoaUser} from '@/lib/types'
import {getDistinctRoleNames} from '@/lib/berkeley-department'

defineProps({
  user: {
    required: true,
    type: Object as PropType<BoaUser>
  }
})
</script>
