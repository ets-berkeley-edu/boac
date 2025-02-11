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
    <v-card-text>
      <div v-for="membership in userDepartment.memberships" :key="membership.role">
        <!-- For each membership in the department, manage role. -->
        <label
          class="font-weight-black text-medium-emphasis mr-2"
          :for="`select-department-${userDepartment.deptCode}-role`"
        >
          <span v-if="membership.peerAdvisingDepartmentId">Peer Advising Role</span>
          <span v-if="!membership.peerAdvisingDepartmentId">Role:</span>
        </label>
        <div class="align-center d-flex">
          <SelectDepartmentMembershipRoles
            v-model="user"
            :all-berkeley-departments="allBerkeleyDepartments"
            :membership="membership"
            :user-department="userDepartment"
          />
          <div v-if="membership.role && !membership.peerAdvisingDepartmentId" class="ml-2">
            <v-checkbox
              :id="`automate-membership-${userDepartment.deptCode}`"
              v-model="membership.automateMembership"
              color="primary"
              density="compact"
              hide-details
              label="Automated"
            />
          </div>
        </div>
        <v-expand-transition>
          <ManagePeerAdvisingMembership
            v-show="membership.role && hasPeerAdvisingDepartments(allBerkeleyDepartments, userDepartment.deptCode)"
            v-model="user"
            :all-berkeley-departments="allBerkeleyDepartments"
            :dept-code="userDepartment.deptCode"
            :membership="membership"
          />
        </v-expand-transition>
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
import {hasPeerAdvisingDepartments} from '@/lib/berkeley-department'

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

<style scoped>
.select-department-role {
  background-color: rgb(var('--v-theme-surface'));
  min-width: 120px;
  z-index: 1;
}
</style>
