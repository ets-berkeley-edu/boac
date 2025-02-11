<template>
  <div>
    <label
      class="font-weight-black text-medium-emphasis"
      :for="`select-department-${deptCode}-role`"
    >
      <span>Department Roles:</span>
    </label>
    <div class="mt-1">
      <select
        :id="`select-department-${deptCode}-role`"
        v-model="membershipRoles"
        class="select-menu select-department-role"
      >
        <option
          id="department-role-null"
          :value="[]"
        >
          Select...
        </option>
        <option
          v-for="option in options"
          :id="`department-role-${option.value.join('-')}`"
          :key="option.text"
          :value="option.value"
        >
          {{ option.text }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {onMounted, ref, watch} from 'vue'
import {each, size} from 'lodash'
import {findDepartment} from '@/lib/berkeley-department'
import type {
  BoaUser,
  BoaUserDepartment,
  DepartmentMembershipRole,
  SelectOption,
} from '@/lib/types'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const props = defineProps({
  deptCode: {
    required: true,
    type: String
  },
  hasPeerAdvisingDepartments: {
    required: true,
    type: Boolean
  }
})

const membershipRoles = ref<DepartmentMembershipRole[]>([])
const options = ref<SelectOption<DepartmentMembershipRole[]>[]>([])

watch(membershipRoles, (roles: DepartmentMembershipRole[]) => {
  if (size(roles)) {
    const department: BoaUserDepartment = findDepartment(user.value.departments, props.deptCode)
    each(roles, (role: DepartmentMembershipRole) => department.memberships.push({role}))
  }
})

onMounted(() => {
  if (props.hasPeerAdvisingDepartments) {
    options.value.push(
      {value: ['advisor'], text: 'Advisor'},
      {value: ['advisor', 'peer_advisor_manager'], text: 'Advisor + Peer Advisor Manager'},
      {value: ['director'], text: 'Director'},
      {value: ['director', 'peer_advisor_manager'], text: 'Director + Peer Advisor Manager'},
      {value: ['peer_advisor'], text: 'Peer Advisor'},
    )
  } else {
    options.value.push({value: ['advisor'], text: 'Advisor'}, {value: ['director'], text: 'Director'})
  }
})
</script>

<style scoped>
.select-department-role {
  background-color: rgb(var('--v-theme-surface'));
  z-index: 1;
}
</style>
