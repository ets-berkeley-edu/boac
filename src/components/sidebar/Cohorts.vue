<template>
  <div v-if="myCohorts">
    <div class="d-flex justify-content-between mb-1 sidebar-row-link">
      <div class="ml-2 sidebar-header">
        Cohorts
      </div>
      <div class="mr-2">
        <router-link
          id="cohort-create"
          aria-label="Create cohort"
          :to="forceUniquePath('/cohort/new?')">
          <i class="fas fa-plus sidebar-header"></i>
        </router-link>
      </div>
    </div>
    <div
      v-for="cohort in myCohorts"
      :key="cohort.id"
      class="d-flex justify-content-between sidebar-row-link">
      <div class="ml-2">
        <router-link
          :id="`sidebar-cohort-${cohort.id}`"
          :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} students`"
          :to="forceUniquePath(`/cohort/${cohort.id}`)">
          {{ cohort.name }}
        </router-link>
      </div>
      <div class="mr-2">
        <span
          :id="`sidebar-cohort-${cohort.id}-total-student-count`"
          class="sidebar-pill">{{ cohort.totalStudentCount }}<span class="sr-only">{{ 'student' | pluralize(cohort.totalStudentCount) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'Cohorts',
  mixins: [UserMetadata, Util]
};
</script>
