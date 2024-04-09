<template xmln="http://www.w3.org/1999/html">
  <v-navigation-drawer class="bg-tertiary pt-1" permanent>
    <v-list density="compact">
      <v-list-item class="pa-0">
        <div class="align-center d-flex font-size-18 font-weight-bold justify-space-between pretty-hover">
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
          class="align-center d-flex justify-space-between pretty-hover"
        >
          <NavLink
            :id="`sidebar-cohort-${cohort.id}`"
            :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} students`"
            class="font-weight-medium text-secondary truncate-with-ellipsis"
            :path="`/cohort/${cohort.id}`"
            :title="cohort.name"
          >
            {{ cohort.name }}
          </NavLink>
          <div class="px-1">
            <span :id="`sidebar-cohort-${cohort.id}-total-student-count`" class="sidebar-pill">
              {{ cohort.totalStudentCount }}<span class="sr-only"> {{ pluralize('student', cohort.totalStudentCount) }}</span>
            </span>
          </div>
        </div>
      </v-list-item>
      <hr class="sidebar-section-divider" />
      <v-list-item class="pa-0">
        <div class="align-center d-flex font-weight-bold justify-space-between pretty-hover">
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
          class="align-center d-flex justify-space-between pretty-hover"
        >
          <NavLink
            :id="`sidebar-${describeCuratedGroupDomain('default', false).replace(' ', '-')}-${index}`"
            :aria-label="`${capitalize(describeCuratedGroupDomain('default', false))} ${group.name} has ${group.totalStudentCount} students.`"
            class="font-weight-medium text-secondary truncate-with-ellipsis"
            :path="`/curated/${group.id}`"
          >
            {{ group.name }}
          </NavLink>
          <div
            :id="`sidebar-curated-${index}-count`"
            class="px-1 sidebar-pill"
          >
            {{ group.totalStudentCount }}<span class="sr-only"> {{ pluralize('student', group.totalStudentCount) }}</span>
          </div>
        </div>
      </v-list-item>
      <v-list-item v-if="currentUser.canAccessAdmittedStudents" class="mt-2 pa-0">
        <hr class="sidebar-section-divider" />
        <div class="font-size-18 font-weight-bold pl-3">
          Admitted Students
        </div>
        <div class="align-center d-flex font-weight-bold justify-space-between pretty-hover pt-1">
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
          class="align-center d-flex justify-space-between pretty-hover"
        >
          <NavLink
            :id="`sidebar-admitted-students-cohort-${index}`"
            :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} admits`"
            class="font-weight-medium text-secondary truncate-with-ellipsis"
            :path="`/cohort/${cohort.id}`"
          >
            {{ cohort.name }}
          </NavLink>
          <div
            :id="`sidebar-admitted-students-cohort-${cohort.id}-total-student-count`"
            class="px-1 sidebar-pill"
          >
            {{ cohort.totalStudentCount }}<span class="sr-only"> {{ pluralize('admits', cohort.totalStudentCount) }}</span>
          </div>
        </div>
      </v-list-item>
      <v-list-item v-if="currentUser.canAccessAdmittedStudents" class="mt-3 pa-0">
        <div class="align-center d-flex font-weight-bold justify-space-between pretty-hover">
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
          class="align-center d-flex justify-space-between pretty-hover"
        >
          <NavLink
            :id="`sidebar-admitted-students-curated-${index}`"
            :aria-label="`${capitalize(describeCuratedGroupDomain('admitted_students', false))} ${group.name} has ${group.totalStudentCount} students.`"
            class="font-weight-medium text-secondary truncate-with-ellipsis"
            :path="`/curated/${group.id}`"
          >
            {{ group.name }}
          </NavLink>
          <div
            :id="`sidebar-admitted-students-curated-${index}-count`"
            class="mr-1 px-1 sidebar-pill"
          >
            {{ group.totalStudentCount }}<span class="sr-only"> {{ pluralize('student', group.totalStudentCount) }}</span>
          </div>
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
      <v-list-item
        v-if="currentUser.canAccessAdvisingData"
        class="batch-note-button fixed-bottom-sidebar px-3 py-0 w-100"
        :class="{'z-index-0': !loading}"
      >
        <LinkToDraftNotes :class="{'mb-4': currentUser.isAdmin}" />
        <v-btn
          v-if="!currentUser.isAdmin"
          id="batch-note-button"
          class="mb-5 mt-3 w-100"
          color="primary"
          :disabled="!!useNoteStore().mode"
          variant="flat"
          @click="isCreateNoteModalOpen = true"
        >
          <v-icon class="mr-1" :icon="mdiFileDocument" />
          New Note
        </v-btn>
        <EditBatchNoteModal
          initial-mode="createBatch"
          :is-open="isCreateNoteModalOpen"
          :on-close="() => {
            isCreateNoteModalOpen = false
            putFocusNextTick('batch-note-button')
          }"
          :toggle-show="show => isCreateNoteModalOpen = show"
        />
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal.vue'
import LinkToDraftNotes from '@/components/sidebar/LinkToDraftNotes.vue'
import NavLink from '@/components/util/NavLink'
import {capitalize} from 'lodash'
import {describeCuratedGroupDomain} from '@/berkeley'
import {mdiFileDocument, mdiPlus} from '@mdi/js'
import {pluralize} from '@/lib/utils'
import {putFocusNextTick} from '@/lib/utils'
</script>

<script lang="ts">
import {computed, ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'
import {filter} from 'lodash'

const extract = (domain: string, objects: any[]) => filter(objects, ['domain', domain])
const currentUser = useContextStore().currentUser
const loading = computed(() => useContextStore().loading)
const myAdmitCohorts = computed(() => extract('admitted_students', currentUser.myCohorts))
const myAdmitCuratedGroups = computed(() => extract('admitted_students', currentUser.myCuratedGroups))
const myCohorts = computed(() => extract('default', currentUser.myCohorts))
const myCuratedGroups = computed(() => extract('default', currentUser.myCuratedGroups))
const isCreateNoteModalOpen = ref(false)
</script>

<style scoped>
.batch-note-button {
  background-color: rgb(18, 80, 116);
  padding-top: 10px;
  width: 16.6%;
}
.fixed-bottom-sidebar {
  bottom: 0;
  position: fixed;
  z-index: 2;
}
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
