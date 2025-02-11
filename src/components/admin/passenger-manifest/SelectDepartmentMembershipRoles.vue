<template>
  <select
    :id="`select-department-${userDepartment.deptCode}-role`"
    v-model="membershipRole"
    class="select-menu select-department-role"
  >
    <option
      id="department-role-null"
      :value="undefined"
    >
      Select...
    </option>
    <option
      v-for="option in getMembershipRoleOptions(membership, userDepartment)"
      :id="`department-role-${lowerCase(option.value)}`"
      :key="option.value"
      :disabled="isRoleOptionDisabled(userDepartment.deptCode, option.value)"
      :value="option.value"
    >
      {{ option.text }}
    </option>
  </select>
</template>

<script setup lang="ts">
import {
  BoaUser,
  BoaUserDepartment,
  Department,
  DepartmentMembership,
  DepartmentMembershipRole,
  SelectOption,
} from '@/lib/types'
import {PropType, ref, watch} from 'vue'
import {hasPeerAdvisingDepartments} from '@/lib/berkeley-department'
import {filter as _filter, find, lowerCase, map} from 'lodash'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const props = defineProps({
  allBerkeleyDepartments: {
    required: true,
    type: Array as PropType<Array<Department>>
  },
  userDepartment: {
    required: true,
    type: Object as PropType<BoaUserDepartment>
  },
  membership: {
    required: true,
    type: Object as PropType<DepartmentMembership>
  }
})

const membershipRole = ref<DepartmentMembershipRole | undefined>(undefined)

watch(membershipRole, (role: DepartmentMembershipRole | undefined) => {
  if (role) {
    const deptCode: string = props.userDepartment.deptCode
    const department: BoaUserDepartment | undefined = find(user.value.departments, ['deptCode', deptCode])
    if (department) {
      const m: DepartmentMembership | undefined = find(department.memberships, ['peerAdvisingDepartmentId', props.membership.peerAdvisingDepartmentId])
      if (m) {
        m.role = role
      }
    }
    membershipRole.value = undefined
  }
})

const getMembershipRoleOptions = (membership: DepartmentMembership, userDepartment: BoaUserDepartment): SelectOption[] => {
  const options: SelectOption[] = []
  if (hasPeerAdvisingDepartments(props.allBerkeleyDepartments, userDepartment.deptCode)) {
    options.push(
      {value: 'advisor', text: 'Advisor'},
      {value: 'peer_advisor', text: 'Advisor + Peer Advisor Manager'},
      {value: 'director', text: 'Director'},
      {value: 'peer_advisor', text: 'Director + Peer Advisor Manager'},
      {value: 'peer_advisor', text: 'Peer Advisor'},
    )
  } else {
    options.push({value: 'advisor', text: 'Advisor'}, {value: 'director', text: 'Director'})
  }
  return options
}

const isRoleOptionDisabled = (deptCode: string, role: string) => {
  let isDisabled = false
  const memberships_per_dept_code = _filter(user.value.departments, ['deptCode', deptCode])
  if (memberships_per_dept_code.length > 1) {
    const existing_roles = map(memberships_per_dept_code, 'role')
    if (['advisor', 'director'].includes(role)) {
      isDisabled = existing_roles.includes('advisor') || existing_roles.includes('director')
    } else if (role === 'peer_advisor_manager') {
      isDisabled = existing_roles.includes('peer_advisor_manager')
    }
  }
  return isDisabled
}
</script>
