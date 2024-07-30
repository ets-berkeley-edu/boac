<template>
  <v-list density="compact">
    <v-list-item class="pa-0">
      <div class="align-center d-flex font-size-18 font-weight-bold justify-space-between mb-1 pretty-hover">
        <div>
          Cohorts
        </div>
        <NavLink id="cohort-create" aria-label="Create cohort" path="/cohort/new">
          <v-icon color="white" :icon="mdiPlus" size="22" />
        </NavLink>
      </div>
      <div
        v-for="cohort in myCohorts"
        :key="cohort.id"
        class="pretty-hover"
      >
        <NavLink
          :id="`sidebar-cohort-${cohort.id}`"
          :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} students`"
          class="align-center d-flex font-weight-medium justify-space-between text-secondary w-100"
          :path="`/cohort/${cohort.id}`"
          :title="cohort.name"
        >
          <div class="truncate-with-ellipsis">
            {{ cohort.name }}
          </div>
          <div :id="`sidebar-cohort-${cohort.id}-total-student-count`" class="sidebar-pill">
            {{ cohort.totalStudentCount }}<span class="sr-only"> {{ pluralize('student', cohort.totalStudentCount) }}</span>
          </div>
        </NavLink>
      </div>
    </v-list-item>
    <hr class="sidebar-section-divider" />
    <v-list-item class="pa-0">
      <div class="align-center d-flex font-weight-bold justify-space-between mb-1 pretty-hover">
        <div class="font-size-18">
          Curated Groups
        </div>
        <NavLink
          id="create-curated-group-from-sidebar"
          :aria-label="`Create a new ${describeCuratedGroupDomain('default')}.`"
          path="/curate"
          :query-args="{domain: 'default'}"
        >
          <v-icon color="white" :icon="mdiPlus" size="22" />
        </NavLink>
      </div>
      <div
        v-for="(group, index) in myCuratedGroups"
        :key="group.id"
        class="pretty-hover"
      >
        <NavLink
          :id="`sidebar-${describeCuratedGroupDomain('default', false).replace(' ', '-')}-${index}`"
          :aria-label="`${capitalize(describeCuratedGroupDomain('default', false))} ${group.name} has ${group.totalStudentCount} students.`"
          class="align-center d-flex font-weight-medium justify-space-between pr-1 text-secondary w-100"
          :path="`/curated/${group.id}`"
        >
          <div class="truncate-with-ellipsis">
            {{ group.name }}
          </div>
          <div :id="`sidebar-curated-${index}-count`" class="sidebar-pill">
            {{ group.totalStudentCount }}<span class="sr-only"> {{ pluralize('student', group.totalStudentCount) }}</span>
          </div>
        </NavLink>
      </div>
    </v-list-item>
    <hr v-if="currentUser.canAccessAdmittedStudents" class="sidebar-section-divider" />
    <v-list-item v-if="currentUser.canAccessAdmittedStudents" class="mt-2 pa-0">
      <div class="font-size-18 font-weight-bold pl-3">
        Admitted Students
      </div>
      <div class="align-center d-flex font-weight-bold justify-space-between mb-1 pretty-hover pt-1">
        <NavLink
          id="admitted-students-all"
          aria-label="View CE3 Admissions"
          path="/admit/students"
        >
          CE3 Cohorts
        </NavLink>
        <NavLink
          id="admitted-students-cohort-create"
          aria-label="Create a CE3 Admissions cohort"
          path="/cohort/new"
          :query-args="{domain: 'admitted_students'}"
        >
          <v-icon class="text-white" :icon="mdiPlus" size="22" />
        </NavLink>
      </div>
      <div
        v-for="(cohort, index) in myAdmitCohorts"
        :key="cohort.id"
        class="pretty-hover"
      >
        <NavLink
          :id="`sidebar-admitted-students-cohort-${index}`"
          :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} admits`"
          class="align-center d-flex font-weight-medium justify-space-between pr-1 text-secondary w-100"
          :path="`/cohort/${cohort.id}`"
        >
          <div class="truncate-with-ellipsis">
            {{ cohort.name }}
          </div>
          <div :id="`sidebar-admitted-students-cohort-${cohort.id}-total-student-count`" class="sidebar-pill">
            {{ cohort.totalStudentCount }}<span class="sr-only"> {{ pluralize('admits', cohort.totalStudentCount) }}</span>
          </div>
        </NavLink>
      </div>
    </v-list-item>
    <v-list-item v-if="currentUser.canAccessAdmittedStudents" class="pa-0">
      <div
        class="align-center d-flex font-weight-bold justify-space-between mb-1 pretty-hover"
        :class="{'mt-2': myAdmitCohorts.length}"
      >
        <div>
          CE3 Groups
        </div>
        <NavLink
          :id="`create-${describeCuratedGroupDomain('admitted_students', false).replace(' ', '-')}-from-sidebar`"
          :aria-label="`Create a new ${describeCuratedGroupDomain('admitted_students', false)}.`"
          path="/curate"
          :query-args="{domain: 'admitted_students'}"
        >
          <v-icon color="white" :icon="mdiPlus" size="22" />
        </NavLink>
      </div>
      <div
        v-for="(group, index) in myAdmitCuratedGroups"
        :key="group.id"
        class="pretty-hover"
      >
        <NavLink
          :id="`sidebar-admitted-students-curated-${index}`"
          :aria-label="`${capitalize(describeCuratedGroupDomain('admitted_students', false))} ${group.name} has ${group.totalStudentCount} students.`"
          class="align-center d-flex font-weight-medium justify-space-between pr-1 text-secondary w-100"
          :path="`/curated/${group.id}`"
        >
          <div class="truncate-with-ellipsis">
            {{ group.name }}
          </div>
          <div :id="`sidebar-admitted-students-curated-${index}-count`" class="sidebar-pill">
            {{ group.totalStudentCount }}<span class="sr-only"> {{ pluralize('student', group.totalStudentCount) }}</span>
          </div>
        </NavLink>
      </div>
    </v-list-item>
    <hr class="sidebar-section-divider" />
    <v-list-item class="pa-0">
      <div class="font-weight-medium pretty-hover">
        <router-link id="cohorts-all" to="/cohorts/all">
          Everyone's Cohorts
        </router-link>
      </div>
      <div class="font-weight-medium mt-1 pretty-hover">
        <router-link id="groups-all" to="/groups/all">
          Everyone's Groups
        </router-link>
      </div>
    </v-list-item>
    <v-list-item v-if="!$vuetify.display.mdAndUp" class="px-0 pt-4">
      <SidebarFooter />
    </v-list-item>
  </v-list>
</template>

<script lang="ts" setup>
import {capitalize} from 'lodash'
import {computed} from 'vue'
import {describeCuratedGroupDomain} from '@/berkeley'
import {filter} from 'lodash'
import {mdiPlus} from '@mdi/js'
import NavLink from '@/components/util/NavLink.vue'
import {pluralize} from '@/lib/utils'
import SidebarFooter from '@/components/sidebar/SidebarFooter.vue'
import {useContextStore} from '@/stores/context'

const extract = (domain: string, objects: any[]) => filter(objects, ['domain', domain])
const currentUser = useContextStore().currentUser
const myAdmitCohorts = computed(() => extract('admitted_students', currentUser.myCohorts))
const myAdmitCuratedGroups = computed(() => extract('admitted_students', currentUser.myCuratedGroups))
const myCohorts = computed(() => extract('default', currentUser.myCohorts))
const myCuratedGroups = computed(() => extract('default', currentUser.myCuratedGroups))
</script>

<style scoped>
.pretty-hover {
  border-left: 6px solid transparent;
  padding: 0 8px 0 6px;
}
.pretty-hover:hover,
.pretty-hover:focus,
.pretty-hover:focus-within,
.pretty-hover:active {
  background-color: rgb(var(--v-theme-quaternary));
  border: 0;
  border-left: 6px solid rgb(var(--v-theme-warning)) !important;
  color: rgb(var(--v-theme-warning));
  text-decoration: none;
  outline-style: none;
}
.pretty-hover:hover .sidebar-pill,
.pretty-hover:focus .sidebar-pill,
.pretty-hover:focus-within .sidebar-pill,
.pretty-hover:active .sidebar-pill {
  background-color: rgb(var(--v-theme-warning));
}
.pretty-hover a:link,
.pretty-hover a:visited {
  text-decoration: none;
  border: 0;
  color: inherit;
  outline-style: none;
}
.sidebar-section-divider {
  background-color: #4a90e2;
  border: none;
  color: #4a90e2;
  height: 1px;
  margin: 12px;
}
.z-index-0 {
  z-index: 0;
}
</style>
