<template>
  <v-container pa-1 fluid>
    <v-layout class="sidebar-row-link">
      <v-flex grow class="sidebar-row-link-label sidebar-header">
        <span class="sidebar-row-link-label-text">Cohorts</span>
      </v-flex>
      <v-flex shrink align-self-end class="sidebar-header sidebar-icon-plus">
        <router-link id="sidebar-filtered-cohort-create"
                     aria-label="Create cohort"
                     to="/cohort_create"><i class="fas fa-plus"></i></router-link>
      </v-flex>
    </v-layout>
    <v-layout class="sidebar-row-link"
              v-for="(cohort, index) in cohorts"
              v-bind:key="cohort.id">
      <v-flex class="sidebar-row-link-label">
        <router-link :id="'sidebar-filtered-cohort-' + index"
                     :aria-label="'Cohort ' + cohort.name + ' has ' + cohort.totalStudentCount + ' students'"
                     class="sidebar-row-link-label-text"
                     :to="'/cohort_' + cohort.id">{{ cohort.name }}</router-link>
      </v-flex>
      <v-spacer></v-spacer>
      <v-flex>
        <span :id="'sidebar-filtered-cohort-' + index + '-count'"
              class="sidebar-pill">{{cohort.totalStudentCount}}<span class="sr-only">{{ 'student' | pluralize(cohort.totalStudentCount)}}</span>
        </span>
      </v-flex>
    </v-layout>
  </v-container>
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
