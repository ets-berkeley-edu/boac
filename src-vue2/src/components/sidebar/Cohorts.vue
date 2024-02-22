<template>
  <div v-if="cohorts">
    <div class="d-flex justify-content-between mb-1 sidebar-row-link">
      <div class="ml-1 sidebar-header">
        Cohorts
      </div>
      <div class="ml-1 mr-2">
        <NavLink
          id="cohort-create"
          aria-label="Create cohort"
          class="sidebar-create-link"
          path="/cohort/new"
        >
          <font-awesome icon="plus" class="sidebar-header" />
        </NavLink>
      </div>
    </div>
    <div
      v-for="cohort in cohorts"
      :key="cohort.id"
      class="d-flex justify-content-between sidebar-row-link"
    >
      <div class="ml-1 truncate-with-ellipsis">
        <NavLink
          :id="`sidebar-cohort-${cohort.id}`"
          :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} students`"
          :path="`/cohort/${cohort.id}`"
        >
          {{ cohort.name }}
        </NavLink>
      </div>
      <div class="ml-1 mr-2">
        <span
          :id="`sidebar-cohort-${cohort.id}-total-student-count`"
          class="sidebar-pill"
        >{{ cohort.totalStudentCount }}<span class="sr-only"> {{ pluralize('student', cohort.totalStudentCount) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import NavLink from '@/components/util/NavLink'
import Util from '@/mixins/Util'

export default {
  name: 'Cohorts',
  components: {NavLink},
  mixins: [Util],
  props: {
    cohorts: {
      type: Array,
      required: true
    }
  }
}
</script>
