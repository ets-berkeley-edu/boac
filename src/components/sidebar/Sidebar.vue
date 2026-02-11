<template>
  <v-list
    class="pa-0 sidebar-list"
    tag="ul"
    density="compact"
    role="list"
    lines="one"
  >
    <v-list-item
      class="pa-0 min-height-unset zero-height"
      role="listitem"
      tag="li"
    >
      <a id="skip-nav-link" class="sr-only" href="#content">skip navigation</a>
      <h2 id="nav-header" class="scroll-margins sr-only" tabindex="-1">Main Menu</h2>
    </v-list-item>
    <v-list-item aria-labelledby="sidebar-cohorts-header" class="pa-0" role="listitem">
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
      <v-list
        tag="ul"
        density="compact"
        lines="one"
        class="py-0 sidebar-list"
        aria-labelledby="sidebar-cohorts-header"
      >
        <v-list-item
          v-for="cohort in myCohorts"
          :key="cohort.id"
          tag="li"
          role="listitem"
          class="py-0 pl-1 pr-2 pretty-hover sub-item"
        >
          <NavLink
            :id="`sidebar-cohort-${cohort.id}`"
            :aria-label="`Cohort ${cohort.name} has ${pluralize('student', cohort.totalStudentCount)}`"
            class="align-center d-flex font-weight-medium justify-space-between text-secondary w-100"
            :path="`/cohort/${cohort.id}`"
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
              <span class="font-size-14">{{ toInt(cohort.totalStudentCount, 0).toLocaleString() }}</span>
            </PillCount>
          </NavLink>
        </v-list-item>
      </v-list>
    </v-list-item>
    <v-list-item
      aria-labelledby="sidebar-curated-groups-header"
      class="pa-0 sidebar-list-divided-section"
      role="listitem"
      tag="li"
    >
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
      <v-list
        tag="ul"
        density="compact"
        class="py-0 sidebar-list"
        lines="one"
        aria-labelledby="sidebar-curated-groups-header"
      >
        <v-list-item
          v-for="(group, index) in myCuratedGroups"
          :key="group.id"
          tag="li"
          role="listitem"
          class="pl-1 pr-2 pretty-hover sub-item"
        >
          <NavLink
            :id="`sidebar-${describeCuratedGroupDomain('default', false).replace(' ', '-')}-${index}`"
            :aria-label="`${capitalize(describeCuratedGroupDomain('default', false))} ${group.name} has ${pluralize('student', group.totalStudentCount)}`"
            class="align-center d-flex font-weight-medium justify-space-between pr-1 text-secondary w-100"
            :path="`/curated/${group.id}`"
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
              <span class="font-size-14">{{ toInt(group.totalStudentCount, 0).toLocaleString() }}</span>
            </PillCount>
          </NavLink>
        </v-list-item>
      </v-list>
    </v-list-item>
    <v-list-item
      v-if="contextStore.currentUser.canAccessAdmittedStudents"
      aria-labelledby="sidebar-admitted-students-header admitted-students-all"
      class="pa-0 sidebar-list-divided-section"
      role="listitem"
      tag="li"
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
      <v-list
        v-if="myCohortsCE3.length"
        tag="ul"
        density="compact"
        class="py-0 sidebar-list"
        lines="one"
        aria-labelledby="sidebar-admitted-students-header admitted-students-all"
      >
        <v-list-item
          v-for="(cohort, index) in myCohortsCE3"
          :key="cohort.id"
          tag="li"
          role="listitem"
          class="py-0 pl-1 pr-2 pretty-hover sub-item"
        >
          <NavLink
            :id="`sidebar-admitted-students-cohort-${index}`"
            :aria-label="`Cohort ${cohort.name} has ${pluralize('admit', cohort.totalStudentCount)}`"
            class="align-center d-flex font-weight-medium justify-space-between pr-1 text-secondary w-100"
            :path="`/cohort/${cohort.id}`"
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
              <span class="font-size-14">{{ toInt(cohort.totalStudentCount, 0).toLocaleString() }}</span>
            </PillCount>
          </NavLink>
        </v-list-item>
      </v-list>
    </v-list-item>
    <v-list-item
      v-if="contextStore.currentUser.canAccessAdmittedStudents"
      aria-labelledby="sidebar-admitted-students-header sidebar-admit-curated-groups-header"
      class="pa-0"
      role="listitem"
      tag="li"
    >
      <div
        class="align-center d-flex font-weight-bold justify-space-between pretty-hover py-1"
        :class="{'mt-2': myCohortsCE3.length}"
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
      <v-list
        v-if="myCuratedGroupsCE3.length"
        tag="ul"
        density="compact"
        class="py-0 sidebar-list"
        lines="one"
        role="list"
        aria-labelledby="sidebar-admit-curated-groups-header"
      >
        <v-list-item
          v-for="(group, index) in myCuratedGroupsCE3"
          :key="group.id"
          tag="li"
          role="listitem"
          class="py-0 pl-1 pr-2 pretty-hover sub-item"
        >
          <NavLink
            :id="`sidebar-admitted-students-curated-${index}`"
            :aria-label="`${capitalize(describeCuratedGroupDomain('admitted_students', false))} ${group.name} has ${pluralize('student', group.totalStudentCount)}`"
            class="align-center d-flex font-weight-medium justify-space-between pr-1 text-secondary w-100"
            :path="`/curated/${group.id}`"
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
              <span class="font-size-14">{{ toInt(group.totalStudentCount, 0).toLocaleString() }}</span>
            </PillCount>
          </NavLink>
        </v-list-item>
      </v-list>
    </v-list-item>
    <v-list-item class="pa-0 sidebar-list-divided-section" role="listitem" tag="li">
      <div class="font-weight-medium mt-1 pretty-hover sub-item">
        <NavLink id="cohorts-all" path="/all/cohorts">
          Everyone's Cohorts
        </NavLink>
      </div>
    </v-list-item>
    <v-list-item class="pa-0" role="listitem" tag="li">
      <div class="font-weight-medium mt-1 pretty-hover sub-item">
        <NavLink id="groups-all" path="/all/curated_groups">
          Everyone's Groups
        </NavLink>
      </div>
    </v-list-item>
    <v-list-item
      v-if="!mdAndUp"
      class="px-0 pt-4"
      role="listitem"
      tag="li"
    >
      <SidebarFooter />
    </v-list-item>
  </v-list>
</template>

<script setup lang="ts">
import {computed} from 'vue'
import {filter as _filter, capitalize} from 'lodash'
import {mdiPlus} from '@mdi/js'
import {useDisplay} from 'vuetify'
import type {Cohort} from '@/lib/types-cohorts'
import type {CuratedGroup} from '@/lib/types'
import NavLink from '@/components/util/NavLink.vue'
import PillCount from '@/components/util/PillCount.vue'
import SidebarFooter from '@/components/sidebar/SidebarFooter.vue'
import {describeCuratedGroupDomain} from '@/lib/berkeley-utils'
import {pluralize, toInt} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const myCohorts = computed<Cohort[]>(() => _filter(contextStore.currentUser.myCohorts, ['domain', 'default']))
const myCohortsCE3 = computed<Cohort[]>(() => _filter(contextStore.currentUser.myCohorts, ['domain', 'admitted_students']))
const myCuratedGroups = computed<CuratedGroup[]>(() => _filter(contextStore.currentUser.myCuratedGroups, ['domain', 'default']))
const myCuratedGroupsCE3 = computed<CuratedGroup[]>(() => _filter(contextStore.currentUser.myCuratedGroups, ['domain', 'admitted_students']))
const {mdAndUp} = useDisplay()
</script>

<style scoped>
.sidebar-list {
  background-color: var(--v-theme-primary);
}
.sidebar-list :deep(.v-list-item) {
  min-height: 24px !important;
}
/* override when zero-height is present */
.sidebar-list :deep(.v-list-item.zero-height) {
  min-height: 6px !important;
}
:deep(.sidebar-list .v-list-item__content) {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}
.sidebar-list-divided-section {
  border-top: solid 1px rgb(var(--v-theme-primary));
  padding-top: 12px !important;
  margin-top: 12px !important;
}
.pretty-hover {
  border-left: 6px solid transparent;
  padding: 2px 8px 2px 6px !important;
}
.pretty-hover:hover,
.pretty-hover:focus-within,
.pretty-hover:active {
  background-color: rgb(var(--v-theme-quaternary));
  border: 0;
  border-left: 6px solid rgb(var(--v-theme-warning)) !important;
  color: rgb(var(--v-theme-warning));
  text-decoration: none;
}
.pretty-hover:focus-within a {
  box-shadow: none;
}
.pretty-hover.sub-item:focus-within {
  outline-color: rgba(var(--v-theme-warning));
  outline-offset: -0.1rem;
  outline-style: solid;
  a {
    box-shadow: none;
      outline: none;
  }
}
.pretty-hover:hover .sidebar-pill,
.pretty-hover:focus-within .sidebar-pill,
.pretty-hover:active .sidebar-pill {
  background-color: rgb(var(--v-theme-warning)) !important;
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.pretty-hover a:link, .pretty-hover a:visited {
  text-decoration: none;
  border: 0;
  color: inherit;
}
</style>
