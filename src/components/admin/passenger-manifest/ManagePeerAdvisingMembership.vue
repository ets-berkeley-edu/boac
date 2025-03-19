<template>
  <div>
    <div>
      <h6 class="font-size-14 text-medium-emphasis">
        {{ membership.role === 'peer_advisor' ? 'Peer Advisor\'s Department' : 'Peer Advising Departments' }}
      </h6>
      <select
        id="peer-advising-department-select"
        v-model="selected"
        aria-label="Department"
        class="mt-1 select-menu select-department-role"
      >
        <option id="department-null" :value="undefined">
          Select...
        </option>
        <option
          v-for="peerAdvisingDepartment in peerAdvisingDepartments"
          :id="`department-option-${normalizeId(peerAdvisingDepartment.name)}`"
          :key="peerAdvisingDepartment.id"
          :value="peerAdvisingDepartment"
        >
          {{ peerAdvisingDepartment.name }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {find, get} from 'lodash'
import {nextTick, onMounted, ref, watch} from 'vue'
import type {
  BoaUser,
  BoaUserDepartment, Department,
  DepartmentMembership,
  PeerAdvisingDepartment,
} from '@/lib/types'
import {findDepartment, findMembership} from '@/lib/berkeley-department'
import {normalizeId} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const props = defineProps({
  deptCode: {
    required: true,
    type: String
  },
  membership: {
    required: true,
    type: Object as PropType<DepartmentMembership>
  }
})

const contextStore = useContextStore()
const departments = contextStore.allBerkeleyDepartments
const peerAdvisingDepartments = findDepartment<Department>(departments, props.deptCode).peerAdvisingDepartments
const selected = ref<PeerAdvisingDepartment | undefined>()

watch(selected, (value: PeerAdvisingDepartment | undefined) => {
  const department: BoaUserDepartment = findDepartment(user.value.departments, props.deptCode)
  const membership: DepartmentMembership = findMembership(department, props.membership.role)
  membership.peerAdvisingDepartmentId = get(value, 'id') || undefined
  membership.peerAdvisingDepartmentName = get(value, 'name') || undefined
})

onMounted(() => {
  const peerAdvisingDepartmentId = props.membership.peerAdvisingDepartmentId
  if (peerAdvisingDepartmentId) {
    selected.value = find(peerAdvisingDepartments, ['id', peerAdvisingDepartmentId])
  }
  nextTick(() => {
    contextStore.setEventHandler('passenger-manifest-select-department-membership-role', () => {
      selected.value = undefined
    })
  })
})
</script>

<style scoped>
.select-department-role {
  background-color: rgb(var('--v-theme-surface'));
  min-width: 120px;
  z-index: 1;
}
</style>
