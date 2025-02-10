<template>
  <div>
    <div v-if="user.departments.length >= 3">
      <span class="text-info"><v-icon class="mb-1" :icon="mdiCheckBold" /> Three departments is enough!</span>
    </div>
    <div v-if="user.departments.length < 3" class="pt-2">
      <select
        id="department-select-list"
        v-model="department"
        aria-label="Department"
        class="select-menu w-100"
      >
        <option id="department-null" :value="undefined">
          Select Department...
        </option>
        <option
          v-for="berkeleyDepartment in allBerkeleyDepartments"
          :id="`department-option-${lowerCase(berkeleyDepartment.deptCode)}`"
          :key="berkeleyDepartment.deptCode"
          :disabled="!!find(user.departments, d => d.deptCode === berkeleyDepartment.deptCode)"
          :value="berkeleyDepartment"
        >
          {{ berkeleyDepartment.deptName }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import {BoaUser, Department} from '@/lib/utils'
import {PropType, ref, watch} from 'vue'
import {find, lowerCase} from 'lodash'
import {mdiCheckBold} from '@mdi/js'

defineProps({
  allBerkeleyDepartments: {
    required: true,
    type: Array as PropType<Array<Department>>
  }
})

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const department = ref<Department | undefined>(undefined)

watch(department, (value: Department | undefined) => {
  if (value) {
    user.value.departments.push({
      id: value.id,
      deptCode: value.deptCode,
      deptName: value.deptName,
      memberships: [{role: undefined}]
    })
    department.value = undefined
  }
})
</script>
