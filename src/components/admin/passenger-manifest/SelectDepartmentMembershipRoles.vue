<template>
  <select
    :id="`select-department-${deptCode}-role`"
    v-model="membershipRoles"
    class="select-menu select-department-role"
  >
    <option
      id="department-role-null"
      :value="undefined"
    >
      Select...
    </option>
    <option
      v-for="option in getMembershipRoleOptions()"
      :id="`department-role-${option.value.join('-')}`"
      :key="option.text"
      :value="option.value"
    >
      {{ option.text }}
    </option>
  </select>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {ref, watch} from 'vue'
import {each, find, size} from 'lodash'
import {hasPeerAdvisingDepartments} from '@/lib/berkeley-department'
import type {
  BoaUser,
  BoaUserDepartment,
  Department,
  DepartmentMembership,
  DepartmentMembershipRole,
  SelectOption,
} from '@/lib/types'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const props = defineProps({
  allBerkeleyDepartments: {
    required: true,
    type: Array as PropType<Array<Department>>
  },
  deptCode: {
    required: true,
    type: String
  },
  membership: {
    required: true,
    type: Object as PropType<DepartmentMembership>
  }
})

const membershipRoles = ref<DepartmentMembershipRole[]>([])

watch(membershipRoles, (roles: DepartmentMembershipRole[] | undefined) => {
  if (size(roles)) {
    const department: BoaUserDepartment | undefined = find(user.value.departments, ['deptCode', props.deptCode])
    if (department) {
      each(roles, (role: DepartmentMembershipRole) => {
        const membership = {role}
        const isPeerAdvisingRelated = role.includes('peer')
        if (isPeerAdvisingRelated) {
          Object.assign(membership, {
            peerAdvisingDepartmentId: 0,
            peerAdvisingDepartmentName: '???'
          })
        }
        department.memberships.push(membership)
      })
    }
    membershipRoles.value = []
  }
})

const getMembershipRoleOptions = (): SelectOption<DepartmentMembershipRole[]>[] => {
  const options: SelectOption<DepartmentMembershipRole[]>[] = []
  if (hasPeerAdvisingDepartments(props.allBerkeleyDepartments, props.deptCode)) {
    options.push(
      {value: ['advisor'], text: 'Advisor'},
      {value: ['advisor', 'peer_advisor_manager'], text: 'Advisor + Peer Advisor Manager'},
      {value: ['director'], text: 'Director'},
      {value: ['director', 'peer_advisor_manager'], text: 'Director + Peer Advisor Manager'},
      {value: ['peer_advisor'], text: 'Peer Advisor'},
    )
  } else {
    options.push({value: ['advisor'], text: 'Advisor'}, {value: ['director'], text: 'Director'})
  }
  return options
}
</script>
