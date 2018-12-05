<template>
  <div class="cohort-column-results">
    <div class="cohort-list-header">
      <div class="cohort-list-header-column-01"></div>
      <div class="cohort-list-header-column-02">
        <div class="cohort-sort-column">
          <label class="cohort-sort-label" for="curated-cohort-sort-by">Sort by</label>
          <select id="curated-cohort-sort-by"
                  class="form-control"
                  v-model="orderBy.selected">
            <option v-for="o in this.orderBy.options"
                    :key="o.value"
                    :value="o.value">{{ o.name }}</option>
          </select>
        </div>
      </div>
    </div>
    <div v-if="!curatedGroup.students.length">
      This curated group has no students. Start adding students from their profile pages to your
      <strong>{{ curatedGroup.name }}</strong> group:
      <SearchStudents :withButton="true"/>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import SearchStudents from '@/components/sidebar/SearchStudents.vue';
import UserMetadata from '@/mixins/UserMetadata';

export default {
  name: 'CuratedGroupList',
  props: {
    curatedGroup: Object
  },
  components: {
    SearchStudents
  },
  mixins: [UserMetadata],
  data: () => ({
    orderBy: {
      selected: 'last_name',
      options: []
    }
  }),
  created() {
    let options = [
      { name: 'First Name', value: 'first_name', available: true },
      { name: 'Last Name', value: 'last_name', available: true },
      { name: 'GPA', value: 'gpa', available: true },
      { name: 'Level', value: 'level', available: true },
      { name: 'Major', value: 'major', available: true },
      { name: 'Team', value: 'group_name', available: this.canViewAsc },
      { name: 'Units Completed', value: 'units', available: true }
    ];
    this.orderBy.options = _.filter(options, 'available');
  }
};
</script>

<style scoped>
</style>
