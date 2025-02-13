<template>
  <h4 class="sr-only">Departments</h4>
  <v-card
    v-for="userDepartment in user.departments"
    :key="userDepartment.deptCode"
    class="bg-grey-lighten-4 border-md mt-1"
    flat
  >
    <v-card-title class="align-center d-flex pb-0">
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
    <v-card-text>
      <SelectDepartmentMembershipRoles
        v-model="user"
        :dept-code="userDepartment.deptCode"
        :is-department-with-peer-advising="hasPeerAdvisingDepartments(allBerkeleyDepartments, userDepartment.deptCode)"
      />
      <div v-for="membership in userDepartment.memberships" :key="membership.role">
        <v-checkbox
          v-if="!isPeerAdvisingRole(membership.role)"
          :id="`automate-membership-${userDepartment.deptCode}`"
          v-model="membership.automateMembership"
          color="primary"
          density="compact"
          hide-details
          :label="`Automate ${membership.role} membership`"
        />
        <ManagePeerAdvisingMembership
          v-if="isPeerAdvisingRole(membership.role)"
          v-model="user"
          class="mt-2"
          :dept-code="userDepartment.deptCode"
          :membership="membership"
          :peer-advising-departments="findDepartment(allBerkeleyDepartments, userDepartment.deptCode).peerAdvisingDepartments"
        />
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {filter as _filter} from 'lodash'
import {mdiCloseCircleOutline} from '@mdi/js'
import ManagePeerAdvisingMembership from '@/components/admin/passenger-manifest/ManagePeerAdvisingMembership.vue'
import SelectDepartmentMembershipRoles from '@/components/admin/passenger-manifest/SelectDepartmentMembershipRoles.vue'
import type {BoaUser, Department} from '@/lib/types'
import {findDepartment, hasPeerAdvisingDepartments, isPeerAdvisingRole} from '@/lib/berkeley-department'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

defineProps({
  allBerkeleyDepartments: {
    required: true,
    type: Array as PropType<Array<Department>>
  }
})

const removeDepartment = (deptCode: string) => {
  user.value.departments = _filter(user.value.departments, d => d.deptCode !== deptCode)
}
</script>
