<template>
  <div class="d-flex align-items-center">
    <div>
      <label class="text-nowrap" for="students-sort-by">Sort by</label>
    </div>
    <div class="pl-2 pb-1">
      <select
        id="students-sort-by"
        v-model="selected"
        class="form-control w-auto">
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
import Berkeley from '@/mixins/Berkeley';
import Context from '@/mixins/Context';
import CurrentUserExtras from '@/mixins/CurrentUserExtras';
import store from '@/store';
import Util from '@/mixins/Util';

export default {
  name: 'SortBy',
  mixins: [Berkeley, Context, CurrentUserExtras, Util],
  data: () => ({
    selected: undefined,
    options: []
  }),
  watch: {
    selected(value) {
      if (value && value !== this.preferences.sortBy) {
        store.commit('currentUserExtras/setUserPreference', {
          key: 'sortBy',
          value
        });
      }
    }
  },
  created() {
    this.$eventHub.$on('sortBy-user-preference-change', sortBy => this.selected = sortBy);
    this.selected = this.preferences.sortBy;
    const gpa_term_id_1 = this.previousSisTermId(this.$config.currentEnrollmentTermId);
    const gpa_term_id_2 = this.previousSisTermId(gpa_term_id_1);
    let options = [
      { name: 'First Name', value: 'first_name', available: true },
      { name: 'Last Name', value: 'last_name', available: true },
      { name: 'GPA (Cumulative)', value: 'gpa', available: true },
      { name: `GPA (${this.termNameForSisId(gpa_term_id_2)})`, value: `term_gpa_${gpa_term_id_2}`, available: true },
      { name: `GPA (${this.termNameForSisId(gpa_term_id_1)})`, value: `term_gpa_${gpa_term_id_1}`, available: true },
      { name: 'Level', value: 'level', available: true },
      { name: 'Major', value: 'major', available: true },
      { name: 'Entering Term', value: 'entering_term', available: true },
      {
        name: 'Team',
        value: 'group_name',
        available: this.$currentUser.isAdmin || this.includes(this.myDeptCodes(['isAdvisor', 'isDirector']), 'UWASC')
      },
      { name: 'Units (In Progress)', value: 'enrolled_units', available: true },
      { name: 'Units (Completed)', value: 'units', available: true },
    ];
    this.options = this.filterList(options, 'available');
  }
};
</script>
