<template>
  <div
    v-if="showRow"
    :id="`filter-row-${position}`"
    class="align-center d-flex flex-wrap mt-2 w-100"
    :class="{'filter-row': isExistingFilter}"
  >
    <div
      v-if="isExistingFilter"
      :id="`existing-filter-${position}`"
      class="existing-filter-name font-weight-500 py-2 ml-4"
    >
      {{ get(filter, 'label.primary') }}<span class="sr-only"> is filter number {{ position }}</span>
    </div>
    <div v-if="isModifyingFilter && !isExistingFilter">
      <FilterSelect
        v-model="selectedFilter"
        :disabled="isUpdatingExistingFilter"
        :filter-row-index="position"
        :has-left-border-style="true"
        :has-opt-groups="cohortStore.domain === 'default'"
        :labelledby="`new-filter-${position}-label`"
        :options="primaryOptions"
        type="primary"
      />
    </div>
    <div
      v-if="!isModifyingFilter"
      class="font-weight-500 truncate-with-ellipsis py-2 w-40"
    >
      <span class="sr-only">Selected filter value is </span>
      <span v-if="isUX('dropdown')">{{ getDropdownSelectedLabel() }}</span>
      <span v-if="isUX('range')">{{ rangeMinLabel() }} {{ rangeMaxLabel() }}</span>
    </div>
    <div
      v-if="isModifyingFilter"
      class="py-1"
      :class="{'mr-4': showAdd}"
    >
      <div v-if="isUX('dropdown')">
        <span :id="`filter-secondary-${position}-label`" class="sr-only">{{ filter.name }} options</span>
        <FilterSelect
          v-model="selectedOption"
          :disabled="isUpdatingExistingFilter"
          :filter-row-index="position"
          :has-opt-groups="!!filter.options[0].header"
          :labelledby="`filter-secondary-${position}-label`"
          :options="filter.options"
          type="secondary"
        />
      </div>
      <div
        v-if="isUX('range') && filter.validation === 'date'"
        class="align-center d-flex"
      >
        <label class="font-weight-500 px-2" :for="`filter-range-min-${position}`">
          {{ rangeMinLabel() }}
        </label>
        <span :id="`filter-range-min-placeholder-${position}`" class="sr-only">
          Start of range in format MM/DD/YYYY
        </span>
        <AccessibleDateInput
          :aria-describedby="`filter-range-min-placeholder-${position}`"
          aria-label="&quot;from&quot; date"
          :container-id="`filter-row-${position}`"
          :get-value="() => DateTime.fromISO(rangeMin).toJSDate()"
          :id-prefix="`filter-range-min-${position}`"
          :max-date="rangeMax"
          required
          :set-value="d => rangeMin = DateTime.fromJSDate(d).toISODate()"
        />
        <label class="font-weight-500 px-2" :for="`filter-range-max-${position}`">
          {{ rangeMaxLabel() }}
        </label>
        <span :id="`filter-range-max-placeholder-${position}`" class="sr-only">
          End of range in format MM/DD/YYYY
        </span>
        <AccessibleDateInput
          :aria-describedby="`filter-range-max-placeholder-${position}`"
          aria-label="&quot;to&quot; date"
          :container-id="`filter-row-${position}`"
          :get-value="() => DateTime.fromISO(rangeMax).toJSDate()"
          :id-prefix="`filter-range-max-${position}`"
          :min-date="rangeMin"
          required
          :set-value="d => rangeMax = DateTime.fromJSDate(d).toISODate()"
        />
      </div>
      <div v-if="isUX('range') && filter.validation !== 'date'" class="align-center d-flex">
        <label class="font-weight-500 mx-3" :for="`filter-range-min-${position}`">
          {{ rangeMinLabel() }}<span class="sr-only"> starting at</span>
        </label>
        <div>
          <v-text-field
            :id="`filter-range-min-${position}`"
            v-model="rangeMin"
            bg-color="white"
            :error="errorPerRangeInput"
            hide-details
            :maxlength="rangeInputSize()"
            :size="rangeInputSize()"
            @keydown.enter="() => isExistingFilter ? onClickUpdateButton() : onClickAddButton()"
          />
        </div>
        <label class="font-weight-500 mx-3" :for="`filter-range-max-${position}`">
          {{ rangeMaxLabel() }}<span class="sr-only"> end of range</span>
        </label>
        <div>
          <v-text-field
            :id="`filter-range-max-${position}`"
            v-model="rangeMax"
            bg-color="white"
            :error="errorPerRangeInput"
            hide-details
            :maxlength="rangeInputSize()"
            :size="rangeInputSize()"
            @keydown.enter="() => isExistingFilter ? onClickUpdateButton() : onClickAddButton()"
          />
        </div>
      </div>
    </div>
    <div
      v-if="!isExistingFilter"
      class="align-center d-flex text-right py-1"
    >
      <div v-if="showAdd">
        <ProgressButton
          id="unsaved-filter-add"
          :action="onClickAddButton"
          :disabled="isSaving || (isUX('dropdown') && !selectedOption)"
          :in-progress="isSaving"
          text="Add"
        />
      </div>
      <div v-if="isModifyingFilter && get(filter, 'type.ux')">
        <v-btn
          id="unsaved-filter-reset"
          class="text-uppercase ml-2"
          color="primary"
          text="Cancel"
          variant="text"
          @click="reset"
        />
      </div>
    </div>
    <div v-if="cohortStore.isOwnedByCurrentUser && isExistingFilter" class="ml-auto mr-3 py-1">
      <div v-if="!isModifyingFilter" class="align-center d-flex justify-space-between">
        <div v-if="!isUX('boolean')">
          <v-btn
            :id="`edit-added-filter-${position}`"
            class="text-uppercase"
            color="primary"
            text="Edit"
            variant="text"
            @click="onClickEditButton"
          />
        </div>
        <div v-if="!isUX('boolean')" class="mb-1">|</div>
        <div>
          <v-btn
            :id="`remove-added-filter-${position}`"
            class="text-uppercase"
            color="primary"
            :disabled="!!cohortStore.editMode"
            text="Remove"
            variant="text"
            @click="remove"
          />
        </div>
      </div>
      <div v-if="isModifyingFilter" class="align-center d-flex">
        <ProgressButton
          :id="`update-added-filter-${position}`"
          :action="onClickUpdateButton"
          density="comfortable"
          :disabled="disableUpdateButton || isUpdatingExistingFilter || (isUX('dropdown') && !selectedOption)"
          :in-progress="isUpdatingExistingFilter"
          size="large"
          :text="isUpdatingExistingFilter ? 'Updating' : 'Update'"
        />
        <v-btn
          :id="`cancel-edit-added-filter-${position}`"
          class="font-size-14 text-uppercase ml-2"
          :disabled="isUpdatingExistingFilter"
          text="Cancel"
          variant="text"
          @click="onClickCancelEdit"
        />
      </div>
    </div>
  </div>
  <v-expand-transition class="mx-2 my-4">
    <v-card v-show="errorPerRangeInput" flat>
      <v-alert
        aria-live="polite"
        density="compact"
        type="error"
        :icon="false"
        variant="tonal"
      >
        <v-alert-title class="font-size-16">{{ errorPerRangeInput }}</v-alert-title>
      </v-alert>
    </v-card>
  </v-expand-transition>
</template>

<script setup>
import AccessibleDateInput from '@/components/util/AccessibleDateInput'
import FilterSelect from '@/components/cohort/FilterSelect'
import ProgressButton from '@/components/util/ProgressButton'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {
  cloneDeep,
  get,
  each,
  find,
  flatten,
  isNaN,
  isNil,
  isNumber,
  isPlainObject,
  isUndefined,
  toLower,
  noop,
  size,
  trim,
  values
} from 'lodash'
import {DateTime} from 'luxon'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {updateFilterOptions} from '@/stores/cohort-edit-session/utils'
import {computed, onMounted, ref, watch} from 'vue'

const props = defineProps({
  position: {
    default: 'new',
    required: false,
    type: [Number, String]
  }
})

const disableUpdateButton = ref(false)
const errorPerRangeInput = ref(undefined)
const filter = ref(undefined)
const isExistingFilter = ref(undefined)
const isModifyingFilter = ref(false)
const isUpdatingExistingFilter = ref(false)
const isSaving = ref(false)
const rangeMax = ref(undefined)
const rangeMin = ref(undefined)
const selectedFilter = ref(undefined)
const selectedOption = ref(undefined)
const showAdd = ref(false)
const showRow = ref(true)

const cohortStore = useCohortStore()

const primaryOptions = computed(() => {
  // If we have only one option-group then flatten the object to an array of options.
  const optionGroups = cohortStore.filterOptionGroups
  const flatten = size(optionGroups) === 1
  const preparedOptions = []
  each(optionGroups, (items, group) => {
    if (!flatten) {
      preparedOptions.push({
        header: group,
        name: group,
        key: group
      })
    }
    each(items, item => {
      if (isPlainObject(item.options)) {
        const subOptions = []
        each(item.options, (subItems, subGroup) => {
          if (!flatten) {
            subOptions.push({
              header: subGroup,
              name: subGroup,
              key: subGroup
            })
          }
          each(subItems, subItem => {
            const value = subItem.value
            subOptions.push({
              disabled: subItem.disabled,
              group: flatten ? null : subGroup,
              key: value,
              name: subItem.name,
              value
            })
          })
        })
        item.options = subOptions
      }
      preparedOptions.push({
        group: flatten ? null : group,
        name: item.label.primary,
        ...item
      })
    })
  })
  return preparedOptions
})

const onRangeUpdate = () => {
  disableUpdateButton.value = false
  errorPerRangeInput.value = undefined
  const trimToNil = v => isUndefined(v) ? v : trim(v) || undefined
  const isNilOrNan = v => isNil(v) || isNaN(v)
  const validation = get(filter.value, 'validation')
  if (validation === 'dependents') {
    const min = trimToNil(rangeMin.value)
    const max = trimToNil(rangeMax.value)
    const isInt = v => /^\d+$/.test(v)
    const isDefinedAndInvalid = v => (isInt(v) && parseInt(v, 10) < 0) || !isInt(v) || isNaN(v)
    if (isDefinedAndInvalid(min) || isDefinedAndInvalid(max)) {
      errorPerRangeInput.value = 'Dependents must be an integer greater than or equal to 0.'
    } else if (parseInt(min, 10) > parseInt(max, 10)) {
      errorPerRangeInput.value = 'Dependents inputs must be in ascending order.'
    }
    disableUpdateButton.value = !!errorPerRangeInput.value || isNilOrNan(min) || isNilOrNan(max) || min > max
  } else if (validation === 'gpa') {
    rangeMin.value = trimToNil(rangeMin.value) && parseFloat(rangeMin.value)
    rangeMax.value = trimToNil(rangeMax.value) && parseFloat(rangeMax.value)
    const isDefinedAndInvalid = v => (isNumber(v) && v < 0 || v > 4) || isNaN(v)
    if (isDefinedAndInvalid(rangeMin.value) || isDefinedAndInvalid(rangeMax.value)) {
      errorPerRangeInput.value = 'GPA must be a number in the range 0 to 4.'
    } else if (isNumber(rangeMin.value) && isNumber(rangeMax.value) && rangeMin.value > rangeMax.value) {
      errorPerRangeInput.value = 'GPA inputs must be in ascending order.'
    }
    disableUpdateButton.value = !!errorPerRangeInput.value
      || isNilOrNan(rangeMin.value)
      || isNilOrNan(rangeMax.value)
      || rangeMin.value > rangeMax.value
  } else if (validation === 'char[2]') {
    rangeMin.value = trimToNil(rangeMin.value)
    rangeMax.value = trimToNil(rangeMax.value)
    const isValid = s => /^[a-zA-Z][a-zA-Z]?$/.test(s)
    const isBadData = rangeMin.value
      && rangeMax.value
      && (!isValid(rangeMin.value) || !isValid(rangeMax.value) || rangeMin.value.toUpperCase() > rangeMax.value.toUpperCase())
    if (isBadData) {
      // Invalid data or values are descending.
      errorPerRangeInput.value = 'Letters must be in ascending order.'
    }
    disableUpdateButton.value = !!errorPerRangeInput.value
      || isNilOrNan(rangeMin.value)
      || isNilOrNan(rangeMax.value)
      || rangeMin.value > rangeMax.value
  } else if (validation === 'date') {
    if (rangeMin.value && rangeMax.value && rangeMin.value > rangeMax.value) {
      // Invalid data or values are descending.
      errorPerRangeInput.value = 'Requires end date after start date.'
    }
    disableUpdateButton.value = !!errorPerRangeInput.value || isNilOrNan(rangeMin.value) || isNilOrNan(rangeMax.value)
  } else if (validation) {
    disableUpdateButton.value = true
    errorPerRangeInput.value = `Unrecognized range type: ${validation}`
  }
  showAdd.value = !errorPerRangeInput.value && !isNilOrNan(rangeMin.value) && !isNilOrNan(rangeMax.value)
}

watch(() => cohortStore.editMode, newEditMode => {
  // Reset the current filter-row if an edit session is initiated elsewhere.
  if (isNil(newEditMode)) {
    // Nothing is being edited. Let's make sure this row is in default state.
    reset()
    showRow.value = true
  } else if (newEditMode === 'add') {
    if (isExistingFilter.value) {
      // User is adding a new filter so other rows, per existing filters, are put back in default state.
      reset()
    }
  } else if (newEditMode.match('edit-[0-9]+')) {
    if (isExistingFilter.value) {
      if (newEditMode !== `edit-${props.position}`) {
        // We do not allow two rows to be in edit mode simultaneously. In this case, some other row is entering edit
        // mode so we effectively click cancel on this row.
        reset()
      }
    } else {
      // Reset and then hide this 'New Filter' row because user has clicked to edit an existing filter.
      reset()
      showRow.value = false
    }
  } else if (newEditMode === 'rename') {
    reset()
  }
})
watch(rangeMax, onRangeUpdate)
watch(rangeMin, onRangeUpdate)
watch(selectedFilter, () => {
  selectedOption.value = undefined
  filter.value = cloneDeep(selectedFilter.value)
  if (filter.value) {
    const type = get(filter.value, 'type.ux')
    showAdd.value = type === 'boolean'
    alertScreenReader(`${filter.value.name} selected`)
    switch (type) {
    case 'dropdown':
      putFocusNextTick(`filter-select-secondary-${props.position}`)
      break
    case 'boolean':
      putFocusNextTick('unsaved-filter-add')
      break
    case 'range':
      putFocusNextTick(`filter-range-min-${props.position}`)
      break
    }
  }
})
watch(selectedOption, () => {
  const value = get(selectedOption.value, 'value')
  if (value) {
    filter.value.value = value
    showAdd.value = !!selectedOption.value
    if (selectedOption.value) {
      putFocusNextTick('unsaved-filter-add')
      alertScreenReader(`${selectedOption.value.name} selected`)
    }
  }
})

onMounted(() => {
  reset()
})

const flattenOptions = optGroup => flatten(values(optGroup))

const formatGPA = value => {
  // Prepend zero in case input is, for example, '.2'. No harm done if input has a leading zero.
  const gpa = '0' + trim(value)
  return parseFloat(gpa).toFixed(3)
}

const getDropdownSelectedLabel = () => {
  const options = find(flattenOptions(cohortStore.filterOptionGroups), ['key', filter.value.key]).options
  let label = ''
  if (Array.isArray(options) && !options[0].header) {
    const option = find(options, ['value', filter.value.value])
    label = get(option, 'name')
  } else {
    each(options, option => {
      label = option.value === filter.value.value ? `${get(option, 'name')} (${option.group})` : null
      return !label
    })
  }
  return label
}

const isUX = type => {
  return get(filter.value, 'type.ux') === type
}

const onClickAddButton = () => {
  isSaving.value = true
  switch (get(filter.value, 'type.ux')) {
  case 'dropdown':
    filter.value.value = selectedOption.value.value
    alertScreenReader(`Added ${filter.value.name} filter with value ${getDropdownSelectedLabel()}`)
    break
  case 'boolean':
    alertScreenReader(`Added ${filter.value.name}`)
    filter.value.value = true
    break
  case 'range':
    alertScreenReader(`Added ${filter.value.name} filter, ${rangeMin.value} to ${rangeMax.value}`)
    updateRangeFilter()
    rangeMin.value = rangeMax.value = undefined
    break
  }
  cohortStore.addFilter(filter.value)
  cohortStore.setModifiedSinceLastSearch(true)
  reset()
  updateFilterOptions(cohortStore.domain, cohortStore.cohortOwner, cohortStore.filters).then(() => {
    putFocusNextTick('filter-select-primary-new')
  })
}

const onClickCancelEdit = () => {
  errorPerRangeInput.value = undefined
  alertScreenReader('Canceled')
  isModifyingFilter.value = false
  cohortStore.setEditMode(null)
  putFocusNextTick('filter-select-primary-new')
}

const onClickEditButton = () => {
  disableUpdateButton.value = false
  if (isUX('dropdown')) {
    // Populate select options, with selected option based on current filter.value.
    const findOption = (options, value) => find(options, ['value', value])
    const options = find(flattenOptions(cohortStore.filterOptionGroups), ['key', filter.value.key]).options
    filter.value.options = options
    selectedOption.value = Array.isArray(options) ? findOption(options, filter.value.value) : find(flattenOptions(options), filter.value.value)
    putFocusNextTick(`filter-select-secondary-${props.position}`)
  } else if (isUX('range')) {
    rangeMin.value = filter.value.value.min
    rangeMax.value = filter.value.value.max
    putFocusNextTick(`filter-range-min-${props.position}`)
  }
  isModifyingFilter.value = true
  cohortStore.setEditMode(`edit-${props.position}`)
  alertScreenReader(`Begin edit of ${filter.value.name} filter`)
}

const onClickUpdateButton = () => {
  if (!disableUpdateButton.value && !isUpdatingExistingFilter.value) {
    isUpdatingExistingFilter.value = true
    if (isUX('range')) {
      updateRangeFilter()
    }
    cohortStore.updateExistingFilter({index: props.position, updatedFilter: filter.value})
    cohortStore.setModifiedSinceLastSearch(true)
    updateFilterOptions(cohortStore.domain, cohortStore.cohortOwner, cohortStore.filters).then(() => {
      isModifyingFilter.value = false
      cohortStore.setEditMode(null)
      alertScreenReader(`${filter.value.name} filter updated`)
      isUpdatingExistingFilter.value = false
    })
  }
}

const rangeInputSize = () => {
  let maxLength = undefined
  const validation = get(filter.value, 'validation')
  if (validation === 'char[2]') {
    maxLength = 2
  } else if (validation === 'gpa' || validation === 'dependents') {
    maxLength = 5
  }
  return maxLength
}

const rangeMaxLabel = () => {
  let snippet = undefined
  if (isModifyingFilter.value) {
    snippet = toLower(filter.value.label.range[1])
  } else {
    let max = get(filter.value, 'value.max')
    if (max && filter.value.validation === 'date') {
      max = DateTime.fromISO(max).toFormat('DD')
    }
    const labels = get(filter.value.label, 'range')
    snippet = rangeMinEqualsMax(filter.value) ? '' : `${labels[1]} ${max}`
  }
  return snippet
}

const rangeMinEqualsMax = filter => get(filter, 'value.min') === get(filter, 'value.max')

const rangeMinLabel = () => {
  let snippet = undefined
  if (isModifyingFilter.value) {
    snippet = toLower(filter.value.label.range[0])
  } else {
    let min = get(filter.value, 'value.min')
    if (min && filter.value.validation === 'date') {
      min = DateTime.fromISO(min).toFormat('DD')
    }
    const labels = get(filter.value.label, 'range')
    snippet = rangeMinEqualsMax(filter.value) ? get(filter.value.label, 'rangeMinEqualsMax') + ' ' + min : `${labels[0]} ${min}`
  }
  return snippet
}

const remove = () => {
  cohortStore.removeFilter(props.position)
  updateFilterOptions(cohortStore.domain, cohortStore.cohortOwner, cohortStore.filters).then(noop)
  cohortStore.setEditMode(null)
  putFocusNextTick('filter-select-primary-new')
  alertScreenReader(`${filter.value.label.primary} filter removed`)
}

const reset = () => {
  errorPerRangeInput.value = selectedFilter.value = selectedOption.value = undefined
  disableUpdateButton.value = false
  showAdd.value = false
  rangeMax.value = undefined
  rangeMin.value = undefined
  isExistingFilter.value = props.position !== 'new'
  filter.value = isExistingFilter.value ? cloneDeep(cohortStore.filters[props.position]) : {}
  isModifyingFilter.value = !isExistingFilter.value
  isSaving.value = false
}

const updateRangeFilter = () => {
  if (filter.value.validation === 'gpa') {
    filter.value.value = {
      min: formatGPA(rangeMin.value),
      max: formatGPA(rangeMax.value)
    }
  } else {
    filter.value.value = {
      min: rangeMin.value,
      max: rangeMax.value
    }
  }
}
</script>

<style scoped>
.existing-filter-name {
  min-width: 210px;
  width: 26%;
}
.filter-row {
  align-items: center;
  background-color: rgb(var(--v-theme-surface-light));
  border-left: 6px solid rgb(var(--v-theme-primary)) !important;
  min-height: 56px;
}
</style>
