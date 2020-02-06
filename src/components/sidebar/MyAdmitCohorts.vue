<template>
  <div v-if="myAdmitCohorts">
    <div class="d-flex justify-content-between mb-1 sidebar-row-link">
      <div class="ml-2 sidebar-header">
        CE3 Admissions
      </div>
      <div class="ml-2 mr-2">
        <NavLink
          id="admitted-students-cohort-create"
          class="sidebar-create-link"
          aria-label="Create an admitted-students cohort"
          path="/cohort/new"
          :query-args="{domain: 'admitted_students'}">
          <font-awesome icon="plus" class="sidebar-header" />
        </NavLink>
      </div>
    </div>
    <div
      v-for="cohort in myAdmitCohorts"
      :key="cohort.id"
      class="d-flex justify-content-between sidebar-row-link">
      <div class="ml-2 truncate-with-ellipsis">
        <NavLink
          :id="`sidebar-admitted-students-cohort-${cohort.id}`"
          :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} students`"
          :path="`/cohort/${cohort.id}`">
          {{ cohort.name }}
        </NavLink>
      </div>
      <div class="ml-2 mr-2">
        <span
          :id="`sidebar-admitted-students-cohort-${cohort.id}-total-student-count`"
          class="sidebar-pill">{{ cohort.totalStudentCount }}<span class="sr-only">{{ 'student' | pluralize(cohort.totalStudentCount) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import CurrentUserExtras from "@/mixins/CurrentUserExtras";
import NavLink from "@/components/util/NavLink";
import Util from "@/mixins/Util";

export default {
  name: "MyAdmitCohorts",
  components: {NavLink},
  mixins: [CurrentUserExtras, Util]
};
</script>
