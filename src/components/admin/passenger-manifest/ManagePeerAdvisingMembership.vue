<template>
  <div
    class="pa-2"
    :class="{
      'bg-pale-blue border-b-sm border-dashed border-e-sm border-t-sm pa-2': membership.peerAdvisingDepartmentId
    }"
  >
    <div>
      <h6 class="font-size-14 mt-3 text-medium-emphasis">
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
          v-for="peerAdvisingDepartment in peerAdvisingDepartments"
          :id="`department-option-${lowerCase(toString(peerAdvisingDepartment.id))}`"
          :key="peerAdvisingDepartment.id"
          :disabled="isDepartmentOptionDisabled(peerAdvisingDepartment)"
          :value="peerAdvisingDepartment"
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
</template>

<script setup lang="ts">
import {filter as _filter, each, find, lowerCase, toString} from 'lodash'
import {mdiCloseCircleOutline} from '@mdi/js'
import type {PropType} from 'vue'
import {onMounted, ref, watch} from 'vue'
import type {
  BoaUser,
  BoaUserDepartment,
  Department,
  DepartmentMembership,
  PeerAdvisingDepartment
} from '@/lib/types'
import {findDepartment, getUserDepartmentsWithRoles} from '@/lib/berkeley-department'

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

const peerAdvisingDepartments = ref<PeerAdvisingDepartment[]>([])
const selectPeerAdvisingDepartment = ref<PeerAdvisingDepartment | undefined>(undefined)

watch(selectPeerAdvisingDepartment, (peerAdvisingDepartment: PeerAdvisingDepartment | undefined) => {
  if (peerAdvisingDepartment) {
    const department: BoaUserDepartment | undefined = find(user.value.departments, ['deptCode', props.deptCode])
    if (department) {
      department.memberships.push({
        peerAdvisingDepartmentId: peerAdvisingDepartment.id,
        peerAdvisingDepartmentName: peerAdvisingDepartment.name,
        role: undefined
      })
    }
    selectPeerAdvisingDepartment.value = undefined
  }
})

onMounted(() => {
  const berkeleyDepartment = findDepartment(props.allBerkeleyDepartments, props.deptCode)
  peerAdvisingDepartments.value = berkeleyDepartment.peerAdvisingDepartments
})
const isDepartmentOptionDisabled = (peerAdvisingDepartment: PeerAdvisingDepartment) => {
  return !peerAdvisingDepartment
  // TODO:
  // const existing_roles = map(_filter(user.value.departments, ['deptCode', deptCode]), 'role')
  // return existing_roles.length === 2 && existing_roles.includes('peer_advisor_manager')
}

const removePeerAdvisingMembership = (peerAdvisingDepartmentId: number | undefined) => {
  each(user.value.departments, department => {
    department.memberships = _filter(department.memberships, m => m.peerAdvisingDepartmentId !== peerAdvisingDepartmentId)
  })
}
</script>
