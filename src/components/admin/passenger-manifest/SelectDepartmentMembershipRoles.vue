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
      <v-expand-transition v-if="!isUndefined(error)">
        <div
          v-show="error"
          id="edit-user-error"
          aria-live="polite"
          class="font-weight-bold my-1 opacity-60 text-error font-size-13"
          role="alert"
        >
          {{ error }}
        </div>
      </v-expand-transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {computed, onMounted, ref, watch} from 'vue'
import {each, find, isUndefined, map, size} from 'lodash'
import type {
  BoaUser,
  BoaUserDepartment,
  DepartmentMembership,
  DepartmentMembershipRole,
  SelectOption,
} from '@/lib/types'
import {
  ADVISING_ROLE_TYPES,
  findDepartment,
  getPeerAdvisingDepartments,
  isPeerAdvisingRole,
} from '@/lib/berkeley-department'
import {normalizeId} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useManifestStore} from '@/stores/manifest'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const props = defineProps({
  deptCode: {
    required: true,
    type: String
  }
})

const contextStore = useContextStore()
const manifestStore = useManifestStore()
const department: BoaUserDepartment = findDepartment(user.value.departments, props.deptCode)
const error = computed<string | undefined>(() => {
  let error: string | undefined
  const isValidRoles = !roles.value.length || find(options.value, option => option.value.every(role => roles.value.includes(role)))
  if (!isValidRoles) {
    if (roles.value.length === 1 && roles.value[0] === 'peer_advisor_manager') {
      error = 'Peer Advisor Managers MUST also have the Advisor role and this user has only the former. ' +
        'Please select a valid role combination from available options.'
    } else {
      error = `Uh oh! Department roles are in an invalid state: ${roles.value.join(', ')}.`
    }
  }
  return error
})
const options = ref<SelectOption<DepartmentMembershipRole[]>[]>([])
const roles = ref<DepartmentMembershipRole[]>([])

watch(roles, (value: DepartmentMembershipRole[]) => {
  if (size(value)) {
    department.memberships = []
    each(value, (role: DepartmentMembershipRole) => {
      const membership = ADVISING_ROLE_TYPES.includes(role) ? {automateMembership: true, role} : {role}
      department.memberships.push(membership)
    })
    if (department.memberships.length) {
      user.value.isAdmin = false
    }
    if (value.includes('peer_advisor')) {
      user.value.canAccessAdvisingData = false
      user.value.canAccessCanvasData = false
      user.value.isAdmin = false
      user.value.isBlocked = true
    }
    if (value.includes('peer_advisor_manager')) {
      user.value.canAccessAdvisingData = true
      user.value.isAdmin = false
    }
  }
  contextStore.broadcast('passenger-manifest-select-department-membership-role', roles)
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
  if (getPeerAdvisingDepartments(manifestStore.allBerkeleyDepartments, props.deptCode).length) {
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
