<template>
  <div v-if="isReady" class="align-items-center d-flex pb-1">
    <div>
      <label id="sort-by" class="font-size-16 mb-0 pr-2 text-nowrap text-secondary" for="students-sort-by">
        Sort<span class="sr-only"> students</span> by
      </label>
    </div>
    <div class="dropdown">
      <b-dropdown
        id="students-sort-by"
        aria-labelledby="sort-by"
        block
        no-caret
        right
        toggle-class="dd-override"
        variant="link"
        @hidden="$announcer.polite('Sort-by menu closed')"
        @shown="$announcer.polite('Sort-by menu opened')"
      >
        <template slot="button-content">
          <div class="d-flex dropdown-width justify-content-between text-dark">
            <div v-if="dropdownLabel">
              <span class="sr-only">Students sorted by </span>{{ dropdownLabel }}<span class="sr-only">. Hit enter to open menu</span>
            </div>
            <div v-if="!dropdownLabel">Select...</div>
            <div class="ml-2">
              <font-awesome icon="angle-down" class="menu-caret" />
            </div>
          </div>
        </template>
        <b-dropdown-group
          v-for="(group, gIndex) in optionGroups"
          :id="`sort-by-option-group-${group.label}`"
          :key="`group-${gIndex}`"
          :header="group.label"
        >
          <b-dropdown-item-button
            v-for="(option, index) in group.options"
            :id="`sort-by-option-${option.value}`"
            :key="`group-option-${index}`"
            class="pl-3"
            @click="onSelect(option.value)"
          >
            &nbsp;&nbsp;{{ option.label }}
          </b-dropdown-item-button>
        </b-dropdown-group>
      </b-dropdown>
    </div>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'SortBy',
  mixins: [Berkeley, Context, Util],
  props: {
    domain: {
      type: String,
      required: false
    }
  },
  data: () => ({
    dropdownLabel: undefined,
    isReady: false,
    optionGroups: undefined,
    sortBy: undefined,
    sortByKey: undefined
  }),
  created() {
    this.optionGroups = this.getSortByOptionGroups(this.domain)
    this.sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
    this.$eventHub.on(`${this.sortByKey}-user-preference-change`, v => this.sortBy = v)
    this.sortBy = this.$_.get(this.$currentUser.preferences, this.sortByKey)
    this.dropdownLabel = this.getSortByOptionLabel(this.optionGroups, this.sortBy)
    this.isReady = true
  },
  methods: {
    getSortByOptionGroups(domain) {
      const optionGroups = []
      if (domain === 'admitted_students') {
        optionGroups.push({
          label: 'Profile',
          options: [
            {label: 'First Name', value: 'first_name'},
            {label: 'Last Name', value: 'last_name'},
            {label: 'CS ID', value: 'cs_empl_id'}
          ]
        })
      } else {
        const previousTermId = this.previousSisTermId(this.$config.currentEnrollmentTermId)
        const previousPreviousTermId = this.previousSisTermId(previousTermId)
        optionGroups.push({
          label: 'Profile',
          options: [
            {label: 'First Name', value: 'first_name'},
            {label: 'Last Name', value: 'last_name'},
            {label: 'Level', value: 'level'},
            {label: 'Major', value: 'major'}
          ]
        })
        if (this.$currentUser.isAdmin || this.$_.includes(this.myDeptCodes(['advisor', 'director']), 'UWASC')) {
          optionGroups[0].options.push({label: 'Team', value: 'group_name'})
        }
        optionGroups.push({
          label: 'Terms',
          options: [
            {label: 'Entering Term', value: 'entering_term'},
            {label: 'Terms in Attendance, ascending', value: 'terms_in_attendance'},
            {label: 'Terms in Attendance, descending', value: 'terms_in_attendance desc'}
          ]
        })
        optionGroups.push({
          label: 'GPA',
          options: [
            {label: `${this.termNameForSisId(previousPreviousTermId)}, ascending`, value: `term_gpa_${previousPreviousTermId}`},
            {label: `${this.termNameForSisId(previousPreviousTermId)}, descending`, value: `term_gpa_${previousPreviousTermId} desc`},
            {label: `${this.termNameForSisId(previousTermId)}, ascending`, value: `term_gpa_${previousTermId}`},
            {label: `${this.termNameForSisId(previousTermId)}, descending`, value: `term_gpa_${previousTermId} desc`},
            {label: 'Cumulative, ascending', value: 'gpa'},
            {label: 'Cumulative, descending', value: 'gpa desc'}
          ]
        })
        optionGroups.push({
          label: 'Units',
          options: [
            {label: 'In Progress, ascending', value: 'enrolled_units'},
            {label: 'In Progress, descending', value: 'enrolled_units desc'},
            {label: 'Completed, ascending', value: 'units'},
            {label: 'Completed, descending', value: 'units desc'}
          ]
        })
      }
      return optionGroups
    },
    getSortByOptionLabel(optionGroups, value) {
      let label = undefined
      if (this.optionGroups) {
        this.$_.each(optionGroups, group => {
          this.$_.each(group.options, option => {
            if (value === option.value) {
              label = option.label
            }
            return !label
          })
          return !label
        })
      }
      return label
    },
    onSelect(value) {
      if (value !== this.$_.get(this.$currentUser.preferences, this.sortByKey)) {
        this.sortBy = value
        this.dropdownLabel = this.getSortByOptionLabel(this.optionGroups, this.sortBy)
        this.$announcer.polite(`${this.dropdownLabel} selected`)
        this.$currentUser.preferences.sortByKey = this.sortBy
      }
    }
  }
}
</script>

<style scoped>
.dropdown {
  background-color: #fefefe;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: #000;
  height: 42px;
  text-align: left;
  vertical-align: middle;
  white-space: nowrap;
  width: 280px;
}
</style>