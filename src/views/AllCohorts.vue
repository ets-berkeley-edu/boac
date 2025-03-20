<template>
  <div v-if="!loading" class="default-margins">
    <div class="align-center d-flex">
      <h1 id="page-header">Everyone's {{ modeLabel }}s</h1>
      <div class="align-center d-flex font-size-13 mb-1 ml-1">
        <v-btn
          v-if="countExpandedDepartments"
          id="collapse-all-departments"
          aria-controls="department-expansion-panels"
          aria-label="Collapse all departments"
          color="primary"
          slim
          text="Collapse all"
          variant="text"
          @click="collapseAllDepartments"
        />
        <div v-if="countExpandedDepartments && countExpandedDepartments < departments.length" class="mb-1">|</div>
        <v-btn
          v-if="countExpandedDepartments < departments.length"
          id="expand-all-departments"
          aria-controls="department-expansion-panels"
          aria-label="Expand all departments"
          color="primary"
          slim
          text="Expand all"
          variant="text"
          @click="expandAllDepartments"
        />
      </div>
    </div>
    <div v-if="currentUser.canAccessAdmittedStudents" class="pl-1">
      <v-icon class="mr-1 vertical-bottom" color="warning" :icon="mdiStar" />
      <span class="sr-only">Star icon</span>denotes a {{ modeLabel.toLowerCase() }} of admitted students.
    </div>
    <v-expansion-panels
      id="department-expansion-panels"
      v-model="panels"
      class="mt-1"
      flat
      multiple
    >
      <template
        v-for="department in departments"
        :key="department.id"
      >
        <v-expansion-panel
          :bg-color="department.isOpen ? 'pale-blue' : 'transparent'"
          class="sortable-group"
          :class="department.isOpen ? 'border-1 pb-6' : 'border-0'"
          hide-actions
          rounded
          :value="department.deptCode"
          @group:selected="open => onClickExpansionPanel(department, open)"
        >
          <v-expansion-panel-title
            :id="`department-${department.deptCode.toLowerCase()}`"
            class="bg-transparent pl-2 py-1 w-100"
            hide-actions
          >
            <template #default="{expanded}">
              <div class="align-center d-flex justify-space-between w-100">
                <div class="align-center d-flex">
                  <div class="expand-icon-container">
                    <v-progress-circular
                      v-if="department.isFetching"
                      color="primary"
                      indeterminate
                      size="x-small"
                      width="2"
                    />
                    <v-icon
                      v-if="!department.isFetching"
                      color="primary"
                      :icon="expanded ? mdiMenuDown : mdiMenuRight"
                      size="large"
                    />
                  </div>
                  <h2 class="page-section-header-sub pr-8 text-primary">
                    <span class="sr-only">{{ `${department.isOpen ? 'Hide' : 'Show'} details for ${department.deptName} ` }}</span>
                    {{ department.deptName }}
                  </h2>
                </div>
              </div>
            </template>
          </v-expansion-panel-title>
          <v-expansion-panel-text class="bg-transparent">
            <div v-if="department.isFetching" class="px-8 pt-8">
              <v-progress-linear
                color="primary"
                height="2"
                indeterminate
                size="x-small"
              />
            </div>
            <div v-if="!department.isFetching" class="ml-14">
              <div class="font-size-14 font-weight-bold text-medium-emphasis" :class="{'mb-3': department.users.length}">
                {{ department.users.length || 'Zero' }} out of
                <span v-if="department.deptCode === 'ZZZZZ'">{{ department.memberCount }}</span>
                <span v-if="department.deptCode !== 'ZZZZZ'">
                  <span v-if="department.deptName.includes('Advisors')">{{ department.memberCount }} {{ department.deptName }}</span>
                  <span v-if="!department.deptName.includes('Advisors')">{{ pluralize(`${department.deptName} advisor`, department.memberCount) }}</span>
                </span>
                {{ department.users.length === 1 ? 'has' : 'have' }} {{ modeLabel.toLowerCase() }}s.
              </div>
              <div
                v-for="(user, index) in department.users"
                :id="`users-of-department-${department.deptCode.toLowerCase()}`"
                :key="index"
                :class="{'mt-3': index > 0}"
              >
                <h3 :id="`user-${user.uid}-name`" class="font-size-14">
                  <span class="sr-only">{{ modeLabel }}s of</span>
                  <span v-if="user.name">{{ user.name }}</span>
                  <span v-if="!user.name">UID: {{ user.uid }}</span>
                </h3>
                <ul
                  :id="`${mode}s-of-user-${user.uid}`"
                  :aria-labelledby="`user-${user.uid}`"
                  class="mt-1"
                >
                  <li v-for="object in (mode === 'cohort' ? user.cohorts : user.curatedGroups)" :key="object.id" class="ml-8">
                    <span v-if="object.domain === 'admitted_students'" class="mr-1">
                      <v-icon class="vertical-bottom" color="warning" :icon="mdiStar" />
                      <span class="sr-only">Star: Admitted Students {{ mode }}</span>
                    </span>
                    <router-link :id="`${mode}-${object.id}`" :to="`/${mode}/${object.id}`">{{ object.name }}</router-link>
                    (<span :id="`${mode}-${object.id}-student-count`">{{ object.totalStudentCount }}</span><span class="sr-only">students</span>)
                  </li>
                </ul>
              </div>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </template>
    </v-expansion-panels>
  </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {filter as _filter, each, get, isNil, map, startsWith, toLower} from 'lodash'
import {mdiMenuDown, mdiMenuRight, mdiStar} from '@mdi/js'
import {useRoute} from 'vue-router'
import {alertScreenReader, pluralize, setPageTitle} from '@/lib/utils'
import {getUsersWithCohortsByDeptCode} from '@/api/cohort'
import {getUsersWithCuratedGroupsByDeptCode} from '@/api/curated'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const countExpandedDepartments = computed(() => _filter(departments, ['isOpen', true]).length)
const currentUser = contextStore.currentUser
const departments = contextStore.allBerkeleyDepartments
const loading = computed(() => contextStore.loading)
const mode = ref(undefined)
const modeLabel = ref(undefined)
const panels = ref([])

contextStore.loadingStart()

onMounted(() => {
  // This component is used for both "All Cohorts" and "All Curated Groups".
  const param = toLower(get(useRoute().params, 'mode'))
  mode.value = startsWith(param, 'cohort') ? 'cohort' : 'curated'
  modeLabel.value = mode.value === 'cohort' ? 'Cohort' : 'Curated Group'
  setPageTitle(`All ${modeLabel.value}s`)
  contextStore.loadingComplete('List of departments has loaded')
})

const collapseAllDepartments = () => {
  panels.value = []
  each(departments, department => department.isOpen = false)
}

const expandAllDepartments = () => {
  panels.value = map(departments, 'deptCode')
  each(departments, department => department.isOpen = true)
}

const onClickExpansionPanel = (department, isOpen) => {
  department.isOpen = isOpen.value
  if (isOpen) {
    alertScreenReader(`Showing ${mode.value}s of ${department.deptName} department`)
    if (isNil(department.users)) {
      department.isFetching = true
      const api = mode.value === 'cohort' ? getUsersWithCohortsByDeptCode : getUsersWithCuratedGroupsByDeptCode
      api(department.deptCode).then(data => {
        department.users = data
        department.isFetching = false
      })
    }
  } else {
    alertScreenReader(`Hiding ${mode.value}s of ${department.deptName} department`)
  }
}
</script>

<style scoped>
.expand-icon-container {
  max-width: 40px;
  min-width: 40px;
  text-align: center;
}
.sortable-group {
  border: 1px solid rgb(var(--v-theme-primary));
}
</style>

<style lang="scss">
.sortable-group {
  &.v-expansion-panel::after {
    border: none !important;
  }
  .v-expansion-panel-text__wrapper {
    padding: 0;
  }
}
</style>
