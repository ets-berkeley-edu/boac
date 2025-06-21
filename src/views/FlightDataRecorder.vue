<template>
  <div v-if="!loading" class="default-margins">
    <div class="align-start d-flex">
      <v-icon
        class="mr-2"
        color="primary"
        :icon="mdiAirplane"
        size="42"
      />
      <h1 id="page-header" class="mt-1">Flight Data Recorder</h1>
    </div>
    <div v-if="department" class="border-sm mt-3 pa-4">
      <NotesReport :department="department" />
    </div>
    <div class="mt-6 pt-4">
      <h2 class="page-section-header-sub">Departments</h2>
      <div v-if="availableDepartments.length > 1" class="my-2">
        <label class="sr-only" for="available-department-reports">Departments:</label>
        <select
          id="available-department-reports"
          v-model="selected"
          class="select-menu"
        >
          <option
            v-for="d in availableDepartments"
            :id="`department-report-${d.deptCode}`"
            :key="d.deptCode"
            :value="d.deptCode"
          >
            {{ d.deptName }}
          </option>
        </select>
      </div>
    </div>
    <UserReport :department="department" />
  </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {find, trim} from 'lodash'
import {mdiAirplane} from '@mdi/js'
import {useRoute} from 'vue-router'
import type {Department} from '@/lib/types'
import NotesReport from '@/components/reports/NotesReport.vue'
import UserReport from '@/components/reports/UserReport.vue'
import {getAvailableDepartmentReports} from '@/api/admin-reports.js'
import {useContextStore} from '@/stores/context'

const DEFAULT_DEPT_CODE = 'QCADV'

const contextStore = useContextStore()
const availableDepartments = ref<Department[]>([])
const department = ref<Department | undefined>(undefined)
const loading = computed(() => contextStore.loading)
const selected = ref<string>()

watch(selected, () => {
  department.value = selected.value ? getDepartment(selected.value) : getDepartment(DEFAULT_DEPT_CODE)
})

contextStore.loadingStart()

onMounted(() => {
  const deptCode = useRoute().params.deptCode.toString()
  if (deptCode) {
    getAvailableDepartmentReports().then(data => {
      availableDepartments.value = data
      selected.value = trim(deptCode).toUpperCase()
      contextStore.loadingComplete('Reports loaded')
    })
  }
})

const getDepartment = (deptCode: string): Department | undefined => find(availableDepartments.value, ['deptCode', deptCode])
</script>
