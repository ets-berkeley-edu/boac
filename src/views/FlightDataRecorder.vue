<template>
  <div v-if="!loading" class="default-margins">
    <div class="align-center d-flex pb-0">
      <div class="pr-2">
        <v-icon :icon="mdiAirplane" color="primary" size="42" />
      </div>
      <div class="pt-2">
        <h1 class="page-section-header">Flight Data Recorder</h1>
      </div>
    </div>
    <NotesReport :department="department" />
    <div class="pb-4 pt-4">
      <h2 class="page-section-header-sub ma-0 pt-0" :class="{'sr-only': availableDepartments.length !== 1}">{{ department.name }}</h2>
      <div v-if="availableDepartments.length > 1" class="align-items-center d-flex">
        <label class="sr-only" for="available-department-reports">Departments:</label>
        <div>
          <select
            id="available-department-reports"
            v-model="selected"
            class="select-menu"
          >
            <option
              v-for="d in availableDepartments"
              :id="`department-report-${d.code}`"
              :key="d.code"
              :value="d.code"
            >
              {{ d.name }}
            </option>
          </select>
        </div>
      </div>
    </div>
    <UserReport :department="department" />
  </div>
</template>

<script setup>
import NotesReport from '@/components/reports/NotesReport'
import UserReport from '@/components/reports/UserReport'
import {find, trim} from 'lodash'
import {getAvailableDepartmentReports} from '@/api/reports'
import {computed, onMounted, ref, watch} from 'vue'
import {useRoute} from 'vue-router'
import {useContextStore} from '@/stores/context'
import {mdiAirplane} from '@mdi/js'

const DEFAULT_DEPT_CODE = 'QCADV'

const contextStore = useContextStore()

const availableDepartments = ref([])
const department = ref(undefined)
const loading = computed(() => contextStore.loading)
const selected = ref(undefined)

watch(selected, () => {
  department.value = getDepartment(selected.value) || getDepartment(DEFAULT_DEPT_CODE)
})

contextStore.loadingStart()

onMounted(() => {
  const deptCode = useRoute().params.deptCode
  getAvailableDepartmentReports().then(data => {
    availableDepartments.value = data
    selected.value = trim(deptCode).toUpperCase()
    contextStore.loadingComplete('Reports loaded')
  })
})

const getDepartment = deptCode => find(availableDepartments.value, ['code', deptCode])
</script>
