<template>
  <div class="cohort-sort-column pr-3">
    <label class="cohort-sort-label" for="students-sort-by">Sort by</label>
    <select
      id="sort-students-by"
      v-model="selected"
      class="form-control">
      <option
        v-for="o in options"
        :key="o.value"
        :value="o.value">
        {{ o.name }}
      </option>
    </select>
  </div>
</template>

<script>
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'SortBy',
  mixins: [UserMetadata, Util],
  data: () => ({
    selected: undefined,
    options: []
  }),
  watch: {
    selected(value) {
      if (value && value !== this.preferences.sortBy) {
        this.setUserPreference({
          key: 'sortBy',
          value
        });
        this.$eventHub.$emit('sort-by-changed-by-user', value);
      }
    }
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
  }
};
</script>

<style scoped>
.cohort-sort-column {
  display: flex;
  white-space: nowrap;
}
.cohort-sort-label {
  padding: 8px 10px 0 0;
}
</style>
