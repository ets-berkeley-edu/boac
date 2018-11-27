<template>
  <v-container pa-1 fluid v-if="curatedGroups.length">
    <v-layout column>
      <v-flex class="sidebar-row-link-label sidebar-header sidebar-header-scoped">
        Curated Groups
      </v-flex>
      <v-layout class="sidebar-row-link"
                v-for="(group, index) in curatedGroups"
                v-bind:key="group.id">
        <v-flex class="sidebar-row-link-label">
          <SmartRef :id="'sidebar-curated-cohort-' + index"
                    :aria-label="'Curated group ' + group.name + ' has ' + group.studentCount + ' students'"
                    class="sidebar-row-link-label-text"
                    :path="'/curated_group/' + group.id"
                    :objectId="group.id">{{ group.name }}</SmartRef>
        </v-flex>
        <v-spacer></v-spacer>
        <v-flex>
          <span :id="'sidebar-curated-cohort-' + index + '-count'"
                class="sidebar-pill">{{group.studentCount}}<span class="sr-only">{{ 'student' | pluralize(group.totalStudentCount)}}</span></span>
        </v-flex>
      </v-layout>
    </v-layout>
    <hr class="section-divider"/>
  </v-container>
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

<style scoped>
.sidebar-header-scoped {
  margin-left: 5px;
}
</style>
