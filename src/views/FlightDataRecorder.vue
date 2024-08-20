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
            v-model="deptCode"
            class="select-menu font-size-16 py-1 pl-2 pr-5 w-auto"
          >
            <option
              v-for="d in availableDepartments"
              :id="`department-report-${d.code}`"
              :key="d.code"
              :value="d.code"
              @select="render"
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
import router from '@/router'
import UserReport from '@/components/reports/UserReport'
import {find, includes, map, trim} from 'lodash'
import {getAvailableDepartmentReports} from '@/api/reports'
import {computed, onMounted, ref, watch} from 'vue'
import {useRoute} from 'vue-router'
import {useContextStore} from '@/stores/context'
import {mdiAirplane} from '@mdi/js'

const contextStore = useContextStore()

const availableDepartments = ref(undefined)
const department = ref(undefined)
const deptCode = trim(useRoute().params.deptCode || '').toUpperCase()
const loading = computed(() => contextStore.loading)

watch(deptCode, () => department.value = find(availableDepartments.value, ['code', deptCode]))

contextStore.loadingStart()

onMounted(() => {
  getAvailableDepartmentReports().then(data => {
    if (includes(map(data, 'code'), deptCode)) {
      availableDepartments.value = data
      department.value = find(availableDepartments.value, ['code', deptCode])
      contextStore.loadingComplete('Reports loaded')
    } else {
      router.push({path: '/404'})
    }
  })
})
</script>
