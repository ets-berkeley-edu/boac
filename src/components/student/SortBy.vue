<template>
  <div class="align-items-center d-flex pb-1">
    <div>
      <label class="mb-0 text-nowrap" for="students-sort-by">Sort by</label>
    </div>
    <div class="pl-2">
      <b-form-select
        id="students-sort-by"
        v-model="selected"
        :options="options"
        class="form-control pb-1 pt-1 pr-4 w-auto"
        text-field="name">
      </b-form-select>
    </div>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import store from '@/store'
import Util from '@/mixins/Util'

export default {
  name: 'SortBy',
  mixins: [Berkeley, Context, CurrentUserExtras, Util],
  props: {
    domain: {
      type: String,
      required: false
    }
  },
  data: () => ({
    selected: undefined,
    options: [],
    separator: '&#x2500;'.repeat(14)
  }),
  computed: {
    sortByKey() {
      return this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
    }
  },
  watch: {
    selected(value) {
      if (value && value !== this.get(this.preferences, this.sortByKey)) {
        store.commit('currentUserExtras/setUserPreference', {
          key: this.sortByKey,
          value
        })
      }
    }
  },
  created() {
    let options = [
      { name: 'First Name', value: 'first_name', available: true },
      { name: 'Last Name', value: 'last_name', available: true }
    ]
    this.$eventHub.$on(`${this.sortByKey}-user-preference-change`, sortBy => this.selected = sortBy)
    this.selected = this.get(this.preferences, this.sortByKey)
    if (this.domain === 'admitted_students') {
      options = options.concat([
        { name: 'CS ID', value: 'cs_empl_id', available: true }
      ])
    } else {
      const gpa_term_id_1 = this.previousSisTermId(this.$config.currentEnrollmentTermId)
      const gpa_term_id_2 = this.previousSisTermId(gpa_term_id_1)
      options = options.concat([
        { name: 'Level', value: 'level', available: true },
        { name: 'Major', value: 'major', available: true },
        { name: 'Entering Term', value: 'entering_term', available: true },
        {
          name: 'Team',
          value: 'group_name',
          available: this.$currentUser.isAdmin || this.includes(this.myDeptCodes(['advisor', 'director']), 'UWASC')
        },
        { html: this.separator, value: null, disabled: true, available: true },
        { name: 'Terms in Attendance (High/Low)', value: 'terms_in_attendance desc', available: true },
        { name: 'Terms in Attendance (Low/High)', value: 'terms_in_attendance', available: true },
        { html: this.separator, value: null, disabled: true, available: true },
        { name: `GPA (${this.termNameForSisId(gpa_term_id_2)} - High/Low)`, value: `term_gpa_${gpa_term_id_2} desc`, available: true },
        { name: `GPA (${this.termNameForSisId(gpa_term_id_2)} - Low/High)`, value: `term_gpa_${gpa_term_id_2}`, available: true },
        { name: `GPA (${this.termNameForSisId(gpa_term_id_1)} - High/Low)`, value: `term_gpa_${gpa_term_id_1} desc`, available: true },
        { name: `GPA (${this.termNameForSisId(gpa_term_id_1)} - Low/High)`, value: `term_gpa_${gpa_term_id_1}`, available: true },
        { name: 'GPA (Cumulative - High/Low)', value: 'gpa desc', available: true },
        { name: 'GPA (Cumulative - Low/High)', value: 'gpa', available: true },
        { html: this.separator, value: null, disabled: true, available: true },
        { name: 'Units (In Progress - High/Low)', value: 'enrolled_units desc', available: true },
        { name: 'Units (In Progress - Low/High)', value: 'enrolled_units', available: true },
        { name: 'Units (Completed - High/Low)', value: 'units desc', available: true },
        { name: 'Units (Completed - Low/High)', value: 'units', available: true },
      ])
    }
    this.options = this.filterList(options, 'available')
  }
}
</script>
