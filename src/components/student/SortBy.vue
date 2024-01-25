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
        left
        menu-class="w-100"
        no-caret
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
import Context from '@/mixins/Context'
import store from '@/store'
import Util from '@/mixins/Util'
import {myDeptCodes, previousSisTermId, termNameForSisId} from '@/berkeley'

export default {
  name: 'SortBy',
  mixins: [Context, Util],
  props: {
    domain: {
      type: String,
      required: false
    }
  },
  data: () => ({
    dropdownLabel: undefined,
    isReady: false,
    optionGroups: undefined
  }),
  created() {
    this.optionGroups = this.getSortByOptionGroups(this.domain)
    const sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
    const sortBy = this._get(this.currentUser.preferences, sortByKey)
    this.dropdownLabel = this.getSortByOptionLabel(sortBy)
    this.isReady = true
  },
  methods: {
    getSortBy() {
      const sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
      return this._get(this.currentUser.preferences, sortByKey)
    },
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
        const previousTermId = previousSisTermId(this.config.currentEnrollmentTermId)
        const previousPreviousTermId = previousSisTermId(previousTermId)
        optionGroups.push({
          label: 'Profile',
          options: [
            {label: 'First Name', value: 'first_name'},
            {label: 'Last Name', value: 'last_name'},
            {label: 'Level', value: 'level'},
            {label: 'Major', value: 'major'}
          ]
        })
        if (this.currentUser.isAdmin || this._includes(myDeptCodes(['advisor', 'director']), 'UWASC')) {
          optionGroups[0].options.push({label: 'Team', value: 'group_name'})
        }
        optionGroups.push({
          label: 'Terms',
          options: [
            {label: 'Entering Term', value: 'entering_term'},
            {label: 'Expected Graduation Term', value: 'expected_grad_term'},
            {label: 'Terms in Attendance, ascending', value: 'terms_in_attendance'},
            {label: 'Terms in Attendance, descending', value: 'terms_in_attendance desc'}
          ]
        })
        optionGroups.push({
          label: 'GPA',
          options: [
            {label: `${termNameForSisId(previousPreviousTermId)}, ascending`, value: `term_gpa_${previousPreviousTermId}`},
            {label: `${termNameForSisId(previousPreviousTermId)}, descending`, value: `term_gpa_${previousPreviousTermId} desc`},
            {label: `${termNameForSisId(previousTermId)}, ascending`, value: `term_gpa_${previousTermId}`},
            {label: `${termNameForSisId(previousTermId)}, descending`, value: `term_gpa_${previousTermId} desc`},
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
    getSortByOptionLabel(sortBy) {
      let label = undefined
      this._each(this.optionGroups, group => {
        this._each(group.options, option => {
          if (sortBy === option.value) {
            label = option.label
          }
          return !label
        })
        return !label
      })
      return label
    },
    onSelect(sortBy) {
      const sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
      store.commit('context/updateCurrentUserPreference', {key: sortByKey, value: sortBy})
      this.broadcast(`${sortByKey}-user-preference-change`, sortBy)
      this.dropdownLabel = this.getSortByOptionLabel(sortBy)
      this.$announcer.polite(`${this.dropdownLabel} selected`)
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
