<template>
  <div v-if="curatedGroups.length">
    <div class="sidebar-row-link sidebar-section-header">
      <div class="sidebar-header sidebar-row-link-label">
        <SmartRef id="sidebar-curated-cohorts-manage"
                  aria-label="Manage your curated groups"
                  class="sidebar-row-link-label-text"
                  path="/cohort/curated/manage">Curated Groups</SmartRef>
      </div>
    </div>
    <div class="sidebar-row-link"
         v-for="(group, index) in curatedGroups"
         v-bind:key="group.id">
      <div class="sidebar-row-link-label">
        <SmartRef :id="'sidebar-curated-cohort-' + index"
                  :aria-label="'Curated group ' + group.name + ' has ' + group.studentCount + ' students'"
                  class="sidebar-row-link-label-text"
                  :path="'/cohort/curated/' + group.id">{{ group.name }}</SmartRef>
      </div>
      <div>
        <span :id="'sidebar-curated-cohort-' + index + '-count'"
              class="sidebar-pill">{{group.studentCount}}<span class="sr-only">{{ 'student' | pluralize(group.totalStudentCount)}}</span></span>
      </div>
    </div>
    <hr class="section-divider"/>
  </div>
</template>

<script>
import _ from 'lodash';
import SmartRef from '@/components/SmartRef';
import store from '@/store';

export default {
  name: 'CuratedGroups',
  components: { SmartRef },
  computed: {
    curatedGroups() {
      return _.get(store.getters.user, 'myCuratedCohorts') || [];
    }
  }
};
</script>
