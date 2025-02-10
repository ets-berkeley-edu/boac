<template>
  <h4 class="sr-only">Departments</h4>
  <v-card
    v-for="userDepartment in user.departments"
    :key="userDepartment.deptCode"
    class="bg-grey-lighten-4 border-md mt-1"
    flat
  >
    <v-card-title class="align-center d-flex">
      <h5 class="text-wrap font-size-16">{{ userDepartment.deptName }} ({{ userDepartment.deptCode }})</h5>
      <v-btn
        :id="`remove-userDepartment-${userDepartment.deptCode}`"
        :aria-label="`Remove department '${userDepartment.deptName}'`"
        class="align-self-start bg-grey-lighten-4 ml-auto text-error"
        density="comfortable"
        :icon="mdiCloseCircleOutline"
        title="Remove"
        variant="flat"
        @click="() => removeDepartment(userDepartment.deptCode)"
      />
    </v-card-title>
    <v-card-text class="pl-4">
      <div v-for="membership in userDepartment.memberships" :key="membership.role">
        <div class="align-center d-flex" :class="{'mt-2 pl-10': membership.peerAdvisingDepartmentId}">
          <label class="font-weight-black mr-2" :for="`select-department-${userDepartment.deptCode}-role`">Role</label>
          <select
            :id="`select-department-${userDepartment.deptCode}-role-${membership.role}`"
            v-model="membership.role"
            class="select-menu select-department-role"
          >
            <option
              id="department-role-null"
              :value="undefined"
            >
              Select...
            </option>
            <option
              v-for="option in membership.peerAdvisingDepartmentId ? [{value: 'peer_advisor', text: 'Peer Advisor'}, {value: 'peer_advisor_manager', text: 'Peer Advisor Manager'}] : [{value: 'advisor', text: 'Advisor'}, {value: 'director', text: 'Director'}]"
              :id="`department-role-${lowerCase(option.value)}`"
              :key="option.value"
              :disabled="isRoleOptionDisabled(userDepartment.deptCode, option.value)"
              :value="option.value"
            >
              {{ option.text }}
            </option>
          </select>
        </div>
        <div class="pl-11">
          <v-checkbox
            v-if="!membership.peerAdvisingDepartmentId"
            :id="`automate-membership-${userDepartment.deptCode}`"
            v-model="membership.automateMembership"
            color="primary"
            density="compact"
            hide-details
            label="Automated"
          />
          <v-expand-transition>
            <div v-show="membership.role && hasPeerAdvisingDepartments(userDepartment.deptCode)">
              <div>
                <h6 class="font-size-14 my-1 text-medium-emphasis">
                  Peer Advising Management <span class="font-weight-light">(optional)</span>
                </h6>
                <select
                  id="peer-advising-department-select"
                  v-model="selectPeerAdvisingDepartment"
                  aria-label="Department"
                  class="select-menu select-department-role"
                >
                  <option id="department-null" :value="undefined">
                    Select Peer Advising Department...
                  </option>
                  <option
                    v-for="peerAdvisingDepartment in getBerkeleyDepartment(userDepartment.deptCode).peerAdvisingDepartments"
                    :id="`department-option-${lowerCase(toString(peerAdvisingDepartment.id))}`"
                    :key="peerAdvisingDepartment.id"
                    :disabled="isDepartmentOptionDisabled(peerAdvisingDepartment.id)"
                    :value="{peerAdvisingDepartment, userDepartment}"
                  >
                    {{ peerAdvisingDepartment.name }}
                  </option>
                </select>
              </div>
              <div
                v-for="(d, index) in getUserDepartmentsWithRoles(user, ['peer_advisor', 'peer_advisor_manager'])"
                :key="index"
                class="align-center d-flex"
              >
                <div v-for="m in d.memberships" :key="m.role">
                  <div class="text-wrap font-size-16">{{ m.peerAdvisingDepartmentName }}</div>
                  <v-btn
                    :id="`remove-membership-${d.deptCode}-${m.role}`"
                    :aria-label="`Remove department '${m.peerAdvisingDepartmentName}'`"
                    class="align-self-start bg-grey-lighten-4 ml-auto text-error"
                    density="comfortable"
                    :icon="mdiCloseCircleOutline"
                    title="Remove"
                    variant="flat"
                    @click="() => removePeerAdvisingMembership(m.peerAdvisingDepartmentId)"
                  />
                </div>
              </div>
            </div>
          </v-expand-transition>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import {PropType, ref, watch} from 'vue'
import {BoaUser, BoaUserDepartment, Department, PeerAdvisingDepartment} from '@/lib/utils'
import {filter as _filter, each, find, lowerCase, map, toString} from 'lodash'
import {getUserDepartmentsWithRoles} from '@/berkeley'
import {mdiCloseCircleOutline} from '@mdi/js'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const props = defineProps({
  allBerkeleyDepartments: {
    required: true,
    type: Array as PropType<Array<Department>>
  }
})

interface SelectPeerAdvisingDepartment {
  peerAdvisingDepartment: PeerAdvisingDepartment,
  userDepartment: BoaUserDepartment
}
const selectPeerAdvisingDepartment = ref<SelectPeerAdvisingDepartment | undefined>(undefined)

watch(selectPeerAdvisingDepartment, (value: SelectPeerAdvisingDepartment | undefined) => {
  if (value) {
    value.userDepartment.memberships.push({
      peerAdvisingDepartmentId: value.peerAdvisingDepartment.id,
      peerAdvisingDepartmentName: value.peerAdvisingDepartment.name,
      role: undefined
    })
    selectPeerAdvisingDepartment.value = undefined
  }
})

const getBerkeleyDepartment = (deptCode: string): Department => {
  const department = find(props.allBerkeleyDepartments, ['deptCode', deptCode])
  if (!department) {
    throw new TypeError('Invalid deptCode: ' + deptCode)
  }
  return department
}

const hasPeerAdvisingDepartments = (deptCode: string) => {
  return !!getBerkeleyDepartment(deptCode).peerAdvisingDepartments?.length
}

const isDepartmentOptionDisabled = deptCode => {
  return !deptCode
  // TODO:
  // const existing_roles = map(_filter(user.value.departments, ['deptCode', deptCode]), 'role')
  // return existing_roles.length === 2 && existing_roles.includes('peer_advisor_manager')
}

const isRoleOptionDisabled = (deptCode, role) => {
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

const removeDepartment = (deptCode: string) => {
  user.value.departments = _filter(user.value.departments, d => d.deptCode !== deptCode)
}

const removePeerAdvisingMembership = (peerAdvisingDepartmentId: number | undefined) => {
  each(user.value.departments, department => {
    department.memberships = _filter(department.memberships, m => m.peerAdvisingDepartmentId !== peerAdvisingDepartmentId)
  })
}
</script>

<style scoped>
.select-department-role {
  background-color: rgb(var('--v-theme-surface'));
  min-width: 120px;
  z-index: 1;
}
</style>
