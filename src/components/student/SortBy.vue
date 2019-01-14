<template>
  <div class="cohort-sort-column">
    <label class="cohort-sort-label" for="students-sort-by">Sort by</label>
    <select id="students-sort-by"
            class="form-control"
            v-model="selected">
      <option v-for="o in options"
              :key="o.value"
              :value="o.value">{{ o.name }}</option>
    </select>
  </div>
</template>

<script>
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'SortBy',
  mixins: [UserMetadata, Util],
  data() {
    return {
      selected: undefined,
      options: []
    };
  },
  created() {
    this.selected = this.preferences.sortBy;
    let options = [
      { name: 'First Name', value: 'first_name', available: true },
      { name: 'Last Name', value: 'last_name', available: true },
      { name: 'GPA', value: 'gpa', available: true },
      { name: 'Level', value: 'level', available: true },
      { name: 'Major', value: 'major', available: true },
      {
        name: 'Team',
        value: 'group_name',
        available: this.canViewAsc
      },
      { name: 'Units Completed', value: 'units', available: true }
    ];
    this.options = this.filterList(options, 'available');
  },
  watch: {
    selected(value) {
      this.setUserPreference({
        key: 'sortBy',
        value
      });
    }
  }
};
</script>
