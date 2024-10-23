<template>
  <v-list density="compact" role="none">
    <v-list-item class="pa-0 min-height-unset">
      <a id="skip-nav-link" class="sr-only" href="#content">skip navigation</a>
      <h2 id="nav-header" class="scroll-margins sr-only" tabindex="-1">Main Menu</h2>
    </v-list-item>
    <v-list-item aria-labelledby="sidebar-cohorts-header" class="pa-0" role="region">
      <div class="align-center d-flex font-size-18 font-weight-bold justify-space-between pretty-hover py-1">
        <div id="sidebar-cohorts-header">
          Cohorts
        </div>
        <NavLink
          id="cohort-create"
          class="d-flex align-center"
          path="/cohort/new"
          title="Create a new cohort"
        >
          <v-icon color="white" :icon="mdiPlus" size="22" />
        </NavLink>
      </div>
      <div
        v-for="cohort in _filter(currentUser.myCohorts, ['domain', 'default'])"
        :key="cohort.id"
        class="pretty-hover"
      >
        <NavLink
          :id="`sidebar-cohort-${cohort.id}`"
          :aria-label="`Cohort ${cohort.name} has ${pluralize('student', cohort.totalStudentCount)}`"
          class="align-center d-flex font-weight-medium justify-space-between text-secondary w-100"
          :path="`/cohort/${cohort.id}`"
          :title="cohort.name"
        >
          <div :aria-hidden="true" class="truncate-with-ellipsis">
            {{ cohort.name }}
          </div>
          <PillCount
            :id="`sidebar-cohort-${cohort.id}-total-student-count`"
            :aria-hidden="true"
            class="text-quaternary sidebar-pill"
            color="secondary"
          >
            {{ cohort.totalStudentCount }}
          </PillCount>
        </NavLink>
      </div>
    </v-list-item>
    <hr class="sidebar-section-divider" />
    <v-list-item aria-labelledby="sidebar-curated-groups-header" class="pa-0" role="region">
      <div class="align-center d-flex font-weight-bold justify-space-between pretty-hover py-1">
        <div id="sidebar-curated-groups-header" class="font-size-18">
          Curated Groups
        </div>
        <NavLink
          id="create-curated-group-from-sidebar"
          class="d-flex align-center"
          path="/curate"
          :query-args="{domain: 'default'}"
          :title="`Create a new ${describeCuratedGroupDomain('default')}`"
        >
          <v-icon color="white" :icon="mdiPlus" size="22" />
        </NavLink>
      </div>
      <div
        v-for="(group, index) in _filter(currentUser.myCuratedGroups, ['domain', 'default'])"
        :key="group.id"
        class="pretty-hover"
      >
        <NavLink
          :id="`sidebar-${describeCuratedGroupDomain('default', false).replace(' ', '-')}-${index}`"
          :aria-label="`${capitalize(describeCuratedGroupDomain('default', false))} ${group.name} has ${pluralize('student', group.totalStudentCount)}`"
          class="align-center d-flex font-weight-medium justify-space-between pr-1 text-secondary w-100"
          :path="`/curated/${group.id}`"
          :title="group.name"
        >
          <div :aria-hidden="true" class="truncate-with-ellipsis">
            {{ group.name }}
          </div>
          <PillCount
            :id="`sidebar-curated-${index}-count`"
            :aria-hidden="true"
            class="text-quaternary sidebar-pill"
            color="secondary"
          >
            {{ group.totalStudentCount }}
          </PillCount>
        </NavLink>
      </div>
    </v-list-item>
    <hr v-if="currentUser.canAccessAdmittedStudents" class="sidebar-section-divider" />
    <v-list-item
      v-if="currentUser.canAccessAdmittedStudents"
      aria-labelledby="sidebar-admitted-students-header admitted-students-all"
      class="mt-2 pa-0"
      role="region"
    >
      <div id="sidebar-admitted-students-header" class="font-size-18 font-weight-bold pl-3">
        Admitted Students
      </div>
      <div class="align-center d-flex font-weight-bold justify-space-between pretty-hover py-1">
        <NavLink
          id="admitted-students-all"
          path="/admit/students"
        >
          CE3 Cohorts
        </NavLink>
        <NavLink
          id="admitted-students-cohort-create"
          class="d-flex align-center"
          path="/cohort/new"
          :query-args="{domain: 'admitted_students'}"
          title="Create a new CE3 Admissions cohort"
        >
          <v-icon class="text-white" :icon="mdiPlus" size="22" />
        </NavLink>
      </div>
      <div
        v-for="(cohort, index) in _filter(currentUser.myCohorts, ['domain', 'admitted_students'])"
        :key="cohort.id"
        class="pretty-hover"
      >
        <NavLink
          :id="`sidebar-admitted-students-cohort-${index}`"
          :aria-label="`Cohort ${cohort.name} has ${pluralize('admit', cohort.totalStudentCount)}`"
          class="align-center d-flex font-weight-medium justify-space-between pr-1 text-secondary w-100"
          :path="`/cohort/${cohort.id}`"
          :title="cohort.name"
        >
          <div :aria-hidden="true" class="truncate-with-ellipsis">
            {{ cohort.name }}
          </div>
          <PillCount
            :id="`sidebar-admitted-students-cohort-${cohort.id}-total-student-count`"
            :aria-hidden="true"
            class="text-quaternary sidebar-pill"
            color="secondary"
          >
            {{ cohort.totalStudentCount }}
          </PillCount>
        </NavLink>
      </div>
    </v-list-item>
    <v-list-item
      v-if="currentUser.canAccessAdmittedStudents"
      aria-labelledby="sidebar-admitted-students-header sidebar-admit-curated-groups-header"
      class="pa-0"
      role="region"
    >
      <div
        class="align-center d-flex font-weight-bold justify-space-between pretty-hover py-1"
        :class="{'mt-2': _filter(currentUser.myCohorts, ['domain', 'admitted_students']).length}"
      >
        <div id="sidebar-admit-curated-groups-header">
          CE3 Groups
        </div>
        <NavLink
          :id="`create-${describeCuratedGroupDomain('admitted_students', false).replace(' ', '-')}-from-sidebar`"
          class="d-flex align-center"
          path="/curate"
          :query-args="{domain: 'admitted_students'}"
          :title="`Create a new CE3 ${describeCuratedGroupDomain('admitted_students', false)}`"
        >
          <v-icon color="white" :icon="mdiPlus" size="22" />
        </NavLink>
      </div>
      <div
        v-for="(group, index) in _filter(currentUser.myCuratedGroups, ['domain', 'admitted_students'])"
        :key="group.id"
        class="pretty-hover"
      >
        <NavLink
          :id="`sidebar-admitted-students-curated-${index}`"
          :aria-label="`${capitalize(describeCuratedGroupDomain('admitted_students', false))} ${group.name} has ${pluralize('student', group.totalStudentCount)}`"
          class="align-center d-flex font-weight-medium justify-space-between pr-1 text-secondary w-100"
          :path="`/curated/${group.id}`"
          :title="group.name"
        >
          <div :aria-hidden="true" class="truncate-with-ellipsis">
            {{ group.name }}
          </div>
          <PillCount
            :id="`sidebar-admitted-students-curated-${index}-count`"
            :aria-hidden="true"
            class="text-quaternary sidebar-pill"
            color="secondary"
          >
            {{ group.totalStudentCount }}
          </PillCount>
        </NavLink>
      </div>
    </v-list-item>
    <hr class="sidebar-section-divider" />
    <v-list-item class="pa-0">
      <div class="font-weight-medium pretty-hover">
        <NavLink id="cohorts-all" path="/cohorts/all">
          Everyone's Cohorts
        </NavLink>
      </div>
      <div class="font-weight-medium mt-1 pretty-hover">
        <NavLink id="groups-all" path="/groups/all">
          Everyone's Groups
        </NavLink>
      </div>
    </v-list-item>
    <v-list-item v-if="!$vuetify.display.mdAndUp" class="px-0 pt-4">
      <SidebarFooter />
    </v-list-item>
  </v-list>
</template>

<script lang="ts" setup>
import NavLink from '@/components/util/NavLink.vue'
import PillCount from '@/components/util/PillCount.vue'
import SidebarFooter from '@/components/sidebar/SidebarFooter.vue'
import {capitalize, filter as _filter} from 'lodash'
import {reactive} from 'vue'
import {describeCuratedGroupDomain} from '@/berkeley'
import {mdiPlus} from '@mdi/js'
import {pluralize} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const currentUser = reactive(useContextStore().currentUser)
</script>

<style>
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
  -moz-outline-style: none;
  outline-style: none;
  text-decoration: none;
}
.pretty-hover:hover .sidebar-pill,
.pretty-hover:focus .sidebar-pill,
.pretty-hover:focus-within .sidebar-pill,
.pretty-hover:active .sidebar-pill {
  background-color: rgb(var(--v-theme-warning)) !important;
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.pretty-hover a:link,
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.pretty-hover a:visited {
  text-decoration: none;
  border: 0;
  color: inherit;
  outline-style: none;
}
.sidebar-section-divider {
  background-color: rgb(var(--v-theme-primary));
  border: none;
  color: rgb(var(--v-theme-primary));
  height: 1px;
  margin: 12px;
}
</style>
