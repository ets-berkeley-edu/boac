<template>
  <div v-if="cohorts">
    <div class="d-flex justify-space-between align-center mb-1 pl-1 pr-2 sidebar-row-link">
      <div class="sidebar-header">Cohorts</div>
      <NavLink
        id="cohort-create"
        aria-label="Create cohort"
        class="sidebar-create-link"
        path="/cohort/new"
      >
        <v-icon color="white" :icon="mdiPlus" size="24" />
      </NavLink>
    </div>
    <div
      v-for="cohort in props.cohorts"
      :key="cohort.id"
      class="d-flex justify-space-between align-center pl-2 sidebar-row-link"
    >
      <NavLink
        :id="`sidebar-cohort-${cohort.id}`"
        :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} students`"
        class="truncate-with-ellipsis"
        :path="`/cohort/${cohort.id}`"
      >
        {{ cohort.name }}
      </NavLink>
      <div class="pl-1 pr-3">
        <span
          :id="`sidebar-cohort-${cohort.id}-total-student-count`"
          class="sidebar-pill"
        >{{ cohort.totalStudentCount }}<span class="sr-only"> {{ pluralize('student', cohort.totalStudentCount) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import NavLink from '@/components/util/NavLink'
import {mdiPlus} from '@mdi/js'
import {pluralize} from '@/lib/utils'

const props = defineProps({
  cohorts: {
    type: Array,
    required: true
  }
})
</script>
