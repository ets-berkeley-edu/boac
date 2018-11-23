<template>
  <div>
    <div class="sidebar-row-link sidebar-section-header">
      <div class="sidebar-header sidebar-row-link-label">
        <span class="sidebar-row-link-label-text">Cohorts</span>
      </div>
      <div>
        <span class="sidebar-header sidebar-row-link-label">
          <SmartRef id="sidebar-filtered-cohort-create"
                    aria-label="Create cohort"
                    class="sidebar-create-link"
                    path="/cohort/filtered"><i class="fas fa-plus"></i></SmartRef>
        </span>
      </div>
    </div>
    <div class="sidebar-row-link"
         v-for="(cohort, index) in cohorts"
         v-bind:key="cohort.id">
      <div class="sidebar-row-link-label">
        <SmartRef :id="'sidebar-filtered-cohort-' + index"
                  :aria-label="'Cohort ' + cohort.name + ' has ' + cohort.totalStudentCount + ' students'"
                  class="sidebar-row-link-label-text"
                  path="/cohort/filtered"
                  :args="{id: cohort.id}">{{ cohort.name }}</SmartRef>
      </div>
      <div>
        <span :id="'sidebar-filtered-cohort-' + index + '-count'"
              class="sidebar-pill">{{cohort.totalStudentCount}}<span class="sr-only">{{ 'student' | pluralize(cohort.totalStudentCount)}}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import store from '@/store';
import SmartRef from '@/components/SmartRef.vue';

export default {
  name: 'Cohorts',
  components: { SmartRef },
  computed: {
    cohorts() {
      return _.get(store.getters.user, 'myFilteredCohorts');
    }
  }
};
</script>

<style scoped>
.sidebar-create-link {
  display: inline-block;
  text-align: center;
  vertical-align: middle;
  width: 20px;
}
</style>
