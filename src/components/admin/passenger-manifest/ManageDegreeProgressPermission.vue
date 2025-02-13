<template>
  <div>
    <label class="font-weight-black" for="degree-progress-permission-select">Degree Progress Permission</label>
    <div class="mt-1">
      <select
        id="degree-progress-permission-select"
        v-model="permission"
        class="select-menu w-50"
      >
        <option id="department-null" :value="undefined">None</option>
        <option
          v-for="option in [{value: 'read', text: 'Read-only'}, {value: 'read_write', text: 'Read and write'}]"
          :key="option.value"
          :value="option.value"
        >
          {{ option.text }}
        </option>
      </select>
    </div>
    <div class="mt-1">
      <v-checkbox
        id="automate-degree-progress-permission"
        v-model="user.automateDegreeProgressPermission"
        density="compact"
        color="primary"
        label="Automate Degree Progress permissions"
        :hide-details="true"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {ref, watch} from 'vue'
import type {BoaUser} from '@/lib/types'

const user = defineModel<BoaUser>({
  required: true,
  type: Object as PropType<BoaUser>
})

const permission = ref<string | undefined>()

watch(permission, (value: string | undefined) => user.value.degreeProgressPermission = value)
</script>
