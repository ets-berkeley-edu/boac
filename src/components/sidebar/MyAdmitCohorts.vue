<template>
  <div v-if="cohorts">
    <div class="d-flex justify-content-between my-1 sidebar-row-link">
      <div class="ml-1 sidebar-sub-header">
        <NavLink
          id="admitted-students-all"
          class="sidebar-create-link"
          aria-label="View CE3 Admissions"
          path="/admit/students"
        >
          CE3 Cohorts
        </NavLink>
      </div>
      <div class="ml-1 mr-2">
        <NavLink
          id="admitted-students-cohort-create"
          class="sidebar-create-link"
          aria-label="Create a CE3 Admissions cohort"
          path="/cohort/new"
          :query-args="{domain: 'admitted_students'}"
        >
          <font-awesome icon="plus" class="sidebar-sub-header" />
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
          :id="`sidebar-admitted-students-cohort-${cohort.id}`"
          :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} admits`"
          :path="`/cohort/${cohort.id}`"
        >
          {{ cohort.name }}
        </NavLink>
      </div>
      <div class="ml-1 mr-2">
        <span
          :id="`sidebar-admitted-students-cohort-${cohort.id}-total-student-count`"
          class="sidebar-pill"
        >{{ cohort.totalStudentCount }}<span class="sr-only"> {{ pluralize('admits', cohort.totalStudentCount) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import NavLink from '@/components/util/NavLink'
import Util from '@/mixins/Util'

export default {
  name: 'MyAdmitCohorts',
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
