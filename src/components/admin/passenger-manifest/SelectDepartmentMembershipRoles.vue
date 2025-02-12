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
import {each, map, size} from 'lodash'
import {ref, watch} from 'vue'
import {findDepartment} from '@/lib/berkeley-department'
import type {
  BoaUser,
  BoaUserDepartment,
  DepartmentMembership,
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

const department: BoaUserDepartment = findDepartment(user.value.departments, props.deptCode)
const membershipRoles = ref<DepartmentMembershipRole[]>(map<DepartmentMembership, DepartmentMembershipRole>(department.memberships, m => m.role))
const options: SelectOption<DepartmentMembershipRole[]>[] = props.hasPeerAdvisingDepartments ?
  [
    {value: ['advisor'], text: 'Advisor'},
    {value: ['advisor', 'peer_advisor_manager'], text: 'Advisor + Peer Advisor Manager'},
    {value: ['director'], text: 'Director'},
    {value: ['director', 'peer_advisor_manager'], text: 'Director + Peer Advisor Manager'},
    {value: ['peer_advisor'], text: 'Peer Advisor'}
  ] :
  [{value: ['advisor'], text: 'Advisor'}, {value: ['director'], text: 'Director'}]

watch(membershipRoles, (roles: DepartmentMembershipRole[]) => {
  if (size(roles)) {
    department.memberships = []
    if (membershipRoles.value.includes('peer_advisor')) {
      user.value.canAccessAdvisingData = false
      user.value.canAccessCanvasData = false
    }
    each(roles, (role: DepartmentMembershipRole) => department.memberships.push({role}))
  }
})
</script>

<style scoped>
.select-department-role {
  background-color: rgb(var('--v-theme-surface'));
  z-index: 1;
}
</style>
