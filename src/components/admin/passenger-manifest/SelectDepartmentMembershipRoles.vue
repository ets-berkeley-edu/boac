<template>
  <div>
    <label
      class="font-weight-black text-medium-emphasis"
      :for="`select-department-${deptCode}-role`"
    >
      Department Roles:
    </label>
    <div class="mt-1">
      <select
        :id="`select-department-${deptCode.toLowerCase()}-role`"
        v-model="roles"
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
          :id="normalizeId(`department-role-${option.value.join('-')}`)"
          :key="option.text"
          :disabled="option.disabled"
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
import {each, map, size} from 'lodash'
import {findDepartment, isPeerAdvisingRole} from '@/lib/berkeley-department'
import type {
  BoaUser,
  BoaUserDepartment,
  DepartmentMembership,
  DepartmentMembershipRole,
  SelectOption,
} from '@/lib/types'
import {normalizeId} from '@/lib/utils'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const props = defineProps({
  deptCode: {
    required: true,
    type: String
  },
  isDepartmentWithPeerAdvising: {
    required: true,
    type: Boolean
  }
})

const department: BoaUserDepartment = findDepartment(user.value.departments, props.deptCode)
const options = ref<SelectOption<DepartmentMembershipRole[]>[]>([])
const roles = ref<DepartmentMembershipRole[]>([])

watch(roles, (value: DepartmentMembershipRole[]) => {
  if (size(value)) {
    department.memberships = []
    each(value, (role: DepartmentMembershipRole) => {
      const membership = ['advisor', 'director'].includes(role) ? {automateMembership: true, role} : {role}
      department.memberships.push(membership)
    })
    if (value.includes('peer_advisor')) {
      user.value.canAccessAdvisingData = false
      user.value.canAccessCanvasData = false
    }
    if (value.includes('peer_advisor_manager')) {
      user.value.canAccessAdvisingData = true
    }
  }
})

watch(() => user.value.departments, () => refreshSelectOptions(), {deep: true})

onMounted(() => {
  refreshSelectOptions()
  roles.value = map<DepartmentMembership, DepartmentMembershipRole>(department.memberships, m => m.role)
})

const refreshSelectOptions = () => {
  type Option = SelectOption<DepartmentMembershipRole[]>
  const advisor: Option = {value: ['advisor'], text: 'Advisor'}
  const director: Option = {value: ['director'], text: 'Director'}
  options.value = []
  if (props.isDepartmentWithPeerAdvising) {
    const hasPeerAdvisingRoleElsewhere = user.value.departments.some(d => {
      return d.deptCode !== props.deptCode && d.memberships.some(m => isPeerAdvisingRole(m.role))
    })
    options.value.push(
      advisor,
      {
        disabled: hasPeerAdvisingRoleElsewhere,
        text: 'Advisor + Peer Advisor Manager',
        value: ['advisor', 'peer_advisor_manager']
      },
      director,
      {
        disabled: hasPeerAdvisingRoleElsewhere,
        text: 'Director + Peer Advisor Manager',
        value: ['director', 'peer_advisor_manager']
      },
      {
        disabled: hasPeerAdvisingRoleElsewhere,
        text: 'Peer Advisor',
        value: ['peer_advisor']
      }
    )
  } else {
    options.value.push(advisor, director)
  }
}
</script>

<style scoped>
.select-department-role {
  background-color: rgb(var('--v-theme-surface'));
  z-index: 1;
}
</style>
