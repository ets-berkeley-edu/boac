<template>
  <div v-if="isReady" class="align-center d-flex pb-2 pr-3">
    <label id="sort-by" class="font-size-16 pr-2 text-no-wrap text-medium-emphasis" for="students-sort-by">
      Sort<span class="sr-only"> students</span> by
    </label>
    <v-select
      id="students-sort-by"
      class="students-sort-by"
      density="compact"
      eager
      hide-details
      item-title="label"
      :items="options"
      :model-value="selectedOption"
      single-line
      variant="outlined"
      @update:menu="onToggleMenu"
      @update:model-value="onSelect"
    >
      <template #selection="{item}">
        <div class="text-no-wrap">
          <template v-if="item">
            <span class="sr-only">Students sorted by </span>{{ item.title }}<span class="sr-only"></span>
          </template>
          <template v-else>Select...</template>
        </div>
      </template>
      <template #item="{props, item}">
        <v-list-subheader
          v-if="item.raw.header"
          :id="`sort-by-option-group-${item.raw.header}`"
        >
          {{ item.title }}
        </v-list-subheader>
        <v-list-item
          v-else
          :id="`sort-by-option-${item.value}`"
          v-bind="props"
          :aria-describedby="item.raw.group ? `sort-by-option-group-${item.raw.group}` : false"
          class="min-height-unset py-1 pl-8"
          density="compact"
          role="option"
          :title="item.title"
        ></v-list-item>
      </template>
    </v-select>
  </div>
</template>

<script setup>
import {find, get, includes} from 'lodash'
import {useContextStore} from '@/stores/context'
</script>

<script>
import {myDeptCodes, previousSisTermId, termNameForSisId} from '@/berkeley'
import {nextTick} from 'vue'

export default {
  name: 'SortBy',
  props: {
    domain: {
      default: undefined,
      required: false,
      type: String
    }
  },
  data: () => ({
    isReady: false,
    options: []
  }),
  computed: {
    selectedOptionLabel() {
      const option = find(this.options, {value: this.selectedOption})
      return get(option, 'label')
    },
    selectedOption() {
      const sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
      return get(useContextStore().currentUser.preferences, sortByKey)
    }
  },
  created() {
    this.options = this.getSortByOptions(this.domain)
    this.isReady = true
  },
  methods: {
    getSortByOptions(domain) {
      const options = [
        {header: 'Profile', label: 'Profile'},
        {group: 'Profile', label: 'First Name', value: 'first_name'},
        {group: 'Profile', label: 'Last Name', value: 'last_name'}
      ]
      if (domain === 'admitted_students') {
        options.push({group: 'Profile', label: 'CS ID', value: 'cs_empl_id'})
      } else {
        const previousTermId = previousSisTermId(useContextStore().config.currentEnrollmentTermId)
        const previousPreviousTermId = previousSisTermId(previousTermId)
        options.push({group: 'Profile', label: 'Level', value: 'level'})
        options.push({group: 'Profile', label: 'Major', value: 'major'})
        if (get(useContextStore().currentUser, 'isAdmin') || includes(myDeptCodes(['advisor', 'director']), 'UWASC')) {
          options[0].options.push({group: 'Profile', label: 'Team', value: 'group_name'})
        }
        options.push({header: 'Terms', label: 'Terms'})
        options.push({group: 'Terms', label: 'Entering Term', value: 'entering_term'})
        options.push({group: 'Terms', label: 'Expected Graduation Term', value: 'expected_grad_term'})
        options.push({group: 'Terms', label: 'Terms in Attendance, ascending', value: 'terms_in_attendance'})
        options.push({group: 'Terms', label: 'Terms in Attendance, descending', value: 'terms_in_attendance desc'})
        options.push({header: 'GPA', label: 'GPA'})
        options.push({group: 'GPA', label: `${termNameForSisId(previousPreviousTermId)}, ascending`, value: `term_gpa_${previousPreviousTermId}`})
        options.push({group: 'GPA', label: `${termNameForSisId(previousPreviousTermId)}, descending`, value: `term_gpa_${previousPreviousTermId} esc`})
        options.push({group: 'GPA', label: `${termNameForSisId(previousTermId)}, ascending`, value: `term_gpa_${previousTermId}`})
        options.push({group: 'GPA', label: `${termNameForSisId(previousTermId)}, descending`, value: `term_gpa_${previousTermId} desc`})
        options.push({group: 'GPA', label: 'Cumulative, ascending', value: 'gpa'})
        options.push({group: 'GPA', label: 'Cumulative, descending', value: 'gpa desc'})
        options.push({header: 'Units', label: 'Units'})
        options.push({group: 'Units', label: 'In Progress, ascending', value: 'enrolled_units'})
        options.push({group: 'Units', label: 'In Progress, descending', value: 'enrolled_units desc'})
        options.push({group: 'Units', label: 'Completed, ascending', value: 'units'})
        options.push({group: 'Units', label: 'Completed, descending', value: 'units desc'})
      }
      return options
    },
    onSelect(sortBy) {
      const sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
      useContextStore().updateCurrentUserPreference(sortByKey, sortBy)
      useContextStore().broadcast(`${sortByKey}-user-preference-change`, sortBy)
      nextTick(() => {
        useContextStore().alertScreenReader(`${this.selectedOptionLabel} selected`)
      })
    },
    onToggleMenu(isOpen) {
      useContextStore().alertScreenReader(`Sort-by menu ${isOpen ? 'opened' : 'closed'}`)
    }
  }
}
</script>

<style scoped>
.students-sort-by {
  min-width: 310px;
}
</style>
