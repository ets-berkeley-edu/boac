<template>
  <div class="align-center d-flex">
    <label
      id="sort-by"
      :class="labelClass"
      for="students-sort-by"
    >
      Sort<span class="sr-only"> students</span> by
    </label>
    <select
      id="students-sort-by"
      v-model="selected"
      class="select-menu"
      :class="selectClass"
    >
      <optgroup
        v-for="(options, label) in optGroups"
        :key="label"
        :label="label"
      >
        <option
          v-for="option in options"
          :id="`sort-by-option-${option.value}`"
          :key="option.value"
          :aria-label="option.label"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </optgroup>
    </select>
  </div>
</template>

<script setup>
import {each, find, get, includes} from 'lodash'
import {nextTick, ref, watch} from 'vue'
import {alertScreenReader} from '@/lib/utils'
import {myDeptCodes} from '@/lib/berkeley-department'
import {previousSisTermId, termNameForSisId} from '@/berkeley'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  domain: {
    default: undefined,
    required: false,
    type: String
  },
  labelClass: {
    default: 'font-size-16 pr-2 text-no-wrap text-medium-emphasis',
    required: false,
    type: String
  },
  selectClass: {
    default: 'students-sort-by',
    required: false,
    type: String
  }
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const optGroups = {
  Profile: [
    {label: 'First Name', value: 'first_name'},
    {label: 'Last Name', value: 'last_name'}
  ]
}
if (props.domain === 'admitted_students') {
  optGroups.Profile.push({label: 'CS ID', value: 'cs_empl_id'})
} else {
  Object.assign(optGroups, {
    Terms: [],
    GPA: [],
    Units: []
  })
  const previousTermId = previousSisTermId(contextStore.config.currentEnrollmentTermId)
  const previousPreviousTermId = previousSisTermId(previousTermId)
  optGroups.Profile.push({label: 'Level', value: 'level'})
  optGroups.Profile.push({label: 'Major', value: 'major'})
  if (currentUser.isAdmin || includes(myDeptCodes(['advisor', 'director']), 'UWASC')) {
    optGroups.Profile.push({label: 'Team', value: 'group_name'})
  }
  optGroups.Terms.push({label: 'Entering Term', value: 'entering_term'})
  optGroups.Terms.push({label: 'Expected Graduation Term', value: 'expected_grad_term'})
  optGroups.Terms.push({label: 'Terms in Attendance, ascending', value: 'terms_in_attendance'})
  optGroups.Terms.push({label: 'Terms in Attendance, descending', value: 'terms_in_attendance desc'})
  optGroups.GPA.push({label: `${termNameForSisId(previousPreviousTermId)}, ascending`, value: `term_gpa_${previousPreviousTermId}`})
  optGroups.GPA.push({label: `${termNameForSisId(previousPreviousTermId)}, descending`, value: `term_gpa_${previousPreviousTermId} desc`})
  optGroups.GPA.push({label: `${termNameForSisId(previousTermId)}, ascending`, value: `term_gpa_${previousTermId}`})
  optGroups.GPA.push({label: `${termNameForSisId(previousTermId)}, descending`, value: `term_gpa_${previousTermId} desc`})
  optGroups.GPA.push({label: 'Cumulative, ascending', value: 'gpa'})
  optGroups.GPA.push({label: 'Cumulative, descending', value: 'gpa desc'})
  optGroups.Units.push({label: 'In Progress, ascending', value: 'enrolled_units'})
  optGroups.Units.push({label: 'In Progress, descending', value: 'enrolled_units desc'})
  optGroups.Units.push({label: 'Completed, ascending', value: 'units'})
  optGroups.Units.push({label: 'Completed, descending', value: 'units desc'})
}
const sortByKey = props.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
const selected = ref(get(currentUser.preferences, sortByKey))

watch(selected, () => {
  contextStore.updateCurrentUserPreference(sortByKey, selected.value)
  contextStore.broadcast(`${sortByKey}-user-preference-change`, selected.value)
  nextTick(() => {
    each(optGroups, options => {
      const label = get(find(options, ['value', selected.value]), 'label')
      if (label) {
        alertScreenReader(`Sorting students by ${label}`)
      }
      return !label
    })
  })
})
</script>

<style scoped>
.students-sort-by {
  min-width: 310px;
}
</style>
