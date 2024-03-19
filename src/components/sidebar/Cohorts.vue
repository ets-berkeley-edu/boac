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
        <v-icon color="white" :icon="mdiPlus" size="large" />
      </NavLink>
    </div>
    <div
      v-for="cohort in cohorts"
      :key="cohort.id"
      class="d-flex justify-space-between align-center pl-1 sidebar-row-link"
    >
      <NavLink
        :id="`sidebar-cohort-${cohort.id}`"
        :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} students`"
        class="truncate-with-ellipsis"
        :path="`/cohort/${cohort.id}`"
      >
        {{ cohort.name }}
      </NavLink>
      <div class="pl-1 pr-2">
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
import {mdiPlus} from '@mdi/js'
</script>

<script>
import NavLink from '@/components/util/NavLink'
import {pluralize} from '@/lib/utils'

export default {
  name: 'Cohorts',
  components: {NavLink},
  props: {
    cohorts: {
      type: Array,
      required: true
    }
  },
  methods: {
    pluralize
  }
}
</script>
