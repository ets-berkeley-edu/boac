<template>
  <div>
    <div>
      <h6 class="font-size-14 text-medium-emphasis">
        Peer Advising Management
      </h6>
      <select
        id="peer-advising-department-select"
        v-model="model"
        aria-label="Department"
        class="select-menu select-department-role"
      >
        <option id="department-null" :value="undefined">
          Select...
        </option>
        <option
          v-for="peerAdvisingDepartment in peerAdvisingDepartments"
          :id="`department-option-${lowerCase(toString(peerAdvisingDepartment.id))}`"
          :key="peerAdvisingDepartment.id"
          :value="peerAdvisingDepartment"
        >
          {{ peerAdvisingDepartment.name }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import {lowerCase, toString} from 'lodash'
import type {PropType} from 'vue'
import {ref, watch} from 'vue'
import type {
  BoaUser,
  BoaUserDepartment,
  DepartmentMembership, DepartmentMembershipRole,
  PeerAdvisingDepartment,
} from '@/lib/types'
import {findDepartment, findMembership} from '@/lib/berkeley-department'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const props = defineProps({
  deptCode: {
    required: true,
    type: String
  },
  role: {
    required: true,
    type: Object as PropType<DepartmentMembershipRole>
  },
  peerAdvisingDepartments: {
    required: true,
    type: Array as PropType<Array<PeerAdvisingDepartment>>
  }
})

const model = ref<PeerAdvisingDepartment | undefined>(undefined)

watch(model, (value: PeerAdvisingDepartment | undefined) => {
  if (value) {
    const department: BoaUserDepartment = findDepartment(user.value.departments, props.deptCode)
    const membership: DepartmentMembership = findMembership(department, props.role)
    membership.peerAdvisingDepartmentId = value.id
    membership.peerAdvisingDepartmentName = value.name
    model.value = undefined
  }
})
</script>

<style scoped>
.select-department-role {
  background-color: rgb(var('--v-theme-surface'));
  min-width: 120px;
  z-index: 1;
}
</style>
