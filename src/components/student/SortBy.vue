<template>
  <div class="align-items-center d-flex pb-1">
    <div>
      <label id="sort-by" class="mb-0 text-nowrap" for="students-sort-by">
        <span class="sr-only">Use space-bar to open</span> Sort<span class="sr-only"> students</span> by
      </label>
    </div>
    <div class="pl-2">
      <b-form-select
        id="students-sort-by"
        v-model="selected"
        aria-labelledby="sort-by"
        class="form-control px-3 py-1 w-auto"
        :options="optionGroups"
        text-field="name"
        @change="onChange"
      ></b-form-select>
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
    optionGroups: undefined,
    selected: undefined,
    sortByKey: undefined
  }),
  created() {
    this.sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
    this.$eventHub.$on(`${this.sortByKey}-user-preference-change`, sortBy => this.selected = sortBy)
    this.selected = this.get(this.preferences, this.sortByKey)
    if (this.domain === 'admitted_students') {
      this.options = [
        {name: 'First Name', value: 'first_name'},
        {name: 'Last Name', value: 'last_name'},
        {name: 'CS ID', value: 'cs_empl_id'}
      ]
    } else {
      const previousTermId = this.previousSisTermId(this.$config.currentEnrollmentTermId)
      const previousPreviousTermId = this.previousSisTermId(previousTermId)
      const options = [
        {name: 'First Name', value: 'first_name'},
        {name: 'Last Name', value: 'last_name'},
        {name: 'Level', value: 'level'},
        {name: 'Major', value: 'major'},
        {name: 'Entering Term', value: 'entering_term'}
      ]
      if (this.$currentUser.isAdmin || this.includes(this.myDeptCodes(['advisor', 'director']), 'UWASC')) {
        options.push({name: 'Team', value: 'group_name'})
      }
      this.optionGroups = [
        {
          label: 'Profile',
          options
        },
        {
          label: 'Terms',
          options: [
            {html: 'Terms in Attendance, ascending', value: 'terms_in_attendance'},
            {html: 'Terms in Attendance, descending', value: 'terms_in_attendance desc'}
          ]
        },
        {
          label: 'GPA',
          options: [
            {html: `${this.termNameForSisId(previousPreviousTermId)}, ascending`, value: `term_gpa_${previousPreviousTermId}`},
            {html: `${this.termNameForSisId(previousPreviousTermId)}, descending`, value: `term_gpa_${previousPreviousTermId} desc`},
            {html: `${this.termNameForSisId(previousTermId)}, ascending`, value: `term_gpa_${previousTermId}`},
            {html: `${this.termNameForSisId(previousTermId)}, descending`, value: `term_gpa_${previousTermId} desc`},
            {html: 'Cumulative, ascending', value: 'gpa'},
            {html: 'Cumulative, descending', value: 'gpa desc'}
          ]
        },
        {
          label: 'Units',
          options: [
            {html: 'In Progress, ascending', value: 'enrolled_units'},
            {html: 'In Progress, descending', value: 'enrolled_units desc'},
            {html: 'Completed, ascending', value: 'units'},
            {html: 'Completed, descending', value: 'units desc'}
          ]
        }
      ]
    }
  },
  methods: {
    onChange() {
      if (this.selected !== this.get(this.preferences, this.sortByKey)) {
        this.alertScreenReader(`Sorting by ${this.selected}`)
        store.commit('currentUserExtras/setUserPreference', {
          key: this.sortByKey,
          value: this.selected
        })
      }
    }
  }
}
</script>
