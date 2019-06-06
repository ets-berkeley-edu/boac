<template>
  <div v-if="myCohorts">
    <div class="d-flex justify-content-between mb-1 sidebar-row-link">
      <div class="ml-2 sidebar-header">
        Cohorts
      </div>
      <div class="ml-2 mr-2">
        <a
          id="cohort-create"
          class="sidebar-create-link"
          aria-label="Create cohort"
          href=""
          @click.prevent="updatePath('/cohort/new?')"
        ><i class="fas fa-plus sidebar-header"></i>
        </a>
      </div>
    </div>
    <div
      v-for="cohort in myCohorts"
      :key="cohort.id"
      class="d-flex justify-content-between sidebar-row-link">
      <div class="ml-2 truncate-with-ellipsis">
        <a
          :id="`sidebar-cohort-${cohort.id}`"
          :aria-label="`Cohort ${cohort.name} has ${cohort.totalStudentCount} students`"
          href=""
          @click.prevent="updatePath(`/cohort/${cohort.id}`)">
          {{ cohort.name }}
        </a>
      </div>
      <div class="ml-2 mr-2">
        <span
          :id="`sidebar-cohort-${cohort.id}-total-student-count`"
          class="sidebar-pill">{{ cohort.totalStudentCount }}<span class="sr-only">{{ 'student' | pluralize(cohort.totalStudentCount) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import UserMetadata from "@/mixins/UserMetadata";
import Util from "@/mixins/Util";
import router from '@/router';

export default {
  name: "Cohorts",
  mixins: [UserMetadata, Util],
  methods: {
    updatePath(path) {
      router.push(this.forceUniquePath(path));
    }
  }
};
</script>
