<template>
  <div>
    <div class="sidebar-row-link sidebar-section-header">
      <div class="sidebar-header sidebar-row-link-label">
        <span class="sidebar-row-link-label-text">Cohorts</span>
      </div>
      <div>
        <span class="sidebar-header sidebar-row-link-label">
          <router-link id="sidebar-filtered-cohort-create"
                       class="sidebar-create-link"
                       aria-label="Create cohort"
                       to="/cohort/create"><i class="fas fa-plus"></i></router-link>
        </span>
      </div>
    </div>
    <div class="sidebar-row-link"
         v-for="(cohort, index) in cohorts"
         v-bind:key="cohort.id">
      <div class="sidebar-row-link-label">
        <router-link :id="'sidebar-filtered-cohort-' + index"
                     :aria-label="'Cohort ' + cohort.name + ' has ' + cohort.totalStudentCount + ' students'"
                     class="sidebar-row-link-label-text"
                     :to="'/cohort/' + cohort.id">{{ cohort.name }}</router-link>
      </div>
      <div>
        <span :id="'sidebar-filtered-cohort-' + index + '-count'"
              class="sidebar-pill">{{cohort.totalStudentCount}}<span class="sr-only">{{ 'student' | pluralize(cohort.totalStudentCount) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import store from '@/store';

export default {
  name: 'Cohorts',
  computed: {
    cohorts: () => _.get(store.getters.user, 'myFilteredCohorts')
  }
};
</script>

<style scoped>
.sidebar-icon-plus {
  float: right;
}
</style>
