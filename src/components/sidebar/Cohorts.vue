<template>
  <div v-if="myCohorts">
    <div class="sidebar-row-link sidebar-section-header">
      <div class="sidebar-header sidebar-row-link-label">
        <span class="sidebar-row-link-label-text">Cohorts</span>
      </div>
      <div>
        <span class="sidebar-header sidebar-row-link-label">
          <router-link
            id="cohort-create"
            class="sidebar-create-link"
            aria-label="Create cohort"
            :to="forceUniquePath('/cohort/new?')"><i class="fas fa-plus"></i></router-link>
        </span>
      </div>
    </div>
    <div
      v-for="cohort in myCohorts"
      :key="cohort.id"
      class="sidebar-row-link">
      <div class="sidebar-row-link-label">
        <router-link
          :id="`sidebar-cohort-${cohort.id}`"
          :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} students`"
          class="sidebar-row-link-label-text"
          :to="forceUniquePath(`/cohort/${cohort.id}`)">
          {{ cohort.name }}
        </router-link>
      </div>
      <div>
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

<style scoped>
.sidebar-create-link {
  display: inline-block;
  text-align: center;
  vertical-align: middle;
  width: 20px;
}
.sidebar-icon-plus {
  float: right;
}
</style>
