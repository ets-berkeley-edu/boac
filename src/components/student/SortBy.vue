<template>
  <div class="d-flex align-items-center">
    <div>
      <label class="text-nowrap" for="students-sort-by">Sort by</label>
    </div>
    <div class="pl-2 pb-1">
      <select
        id="students-sort-by"
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
        this.setUserPreference({key: 'sortBy', value});
      }
    }
  },
  created() {
    this.$eventHub.$on('sortBy-user-preference-change', sortBy => this.selected = sortBy);
    this.selected = this.preferences.sortBy;
    let options = [
      { name: 'First Name', value: 'first_name', available: true },
      { name: 'Last Name', value: 'last_name', available: true },
      { name: 'GPA', value: 'gpa', available: true },
      { name: 'Level', value: 'level', available: true },
      { name: 'Major', value: 'major', available: true },
      { name: 'Entering Term', value: 'entering_term', available: true },
      {
        name: 'Team',
        value: 'group_name',
        available: this.user.isAdmin || this.includes(this.myDeptCodesWhereAdvising(), 'UWASC')
      },
      { name: 'Units Completed', value: 'units', available: true }
    ];
    this.options = this.filterList(options, 'available');
  }
};
</script>
