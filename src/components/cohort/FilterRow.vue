<template>
  <div
    v-if="showRow"
    class="align-center d-flex flex-wrap mt-2"
    :class="{'filter-row': isExistingFilter}"
  >
    <div
      v-if="isExistingFilter"
      :id="`existing-filter-${position}`"
      class="existing-filter-name font-weight-500 ml-4"
    >
      {{ get(filter, 'label.primary') }}<span class="sr-only"> is filter number {{ position }}</span>
    </div>
    <div v-if="isModifyingFilter && !isExistingFilter" class="mr-3">
      <FilterSelect
        v-model="selectedFilter"
        :filter-row-index="position"
        :has-left-border-style="true"
        :has-opt-groups="true"
        :labelledby="`new-filter-${position}-label`"
        :options="primaryOptions"
        type="primary"
      />
    </div>
    <div v-if="!isModifyingFilter" class="font-weight-500">
      <span class="sr-only">Selected filter value is </span>
      <span v-if="isUX('dropdown')">{{ getDropdownSelectedLabel() }}</span>
      <span v-if="isUX('range')">{{ rangeMinLabel() }} {{ rangeMaxLabel() }}</span>
    </div>
    <div
      v-if="isModifyingFilter"
      :class="{'mr-4': showAdd, 'mr-2': !showAdd, 'date-range-container': isUX('range')}"
    >
      <div v-if="isUX('dropdown')">
        <span :id="`filter-secondary-${position}-label`" class="sr-only">{{ filter.name }} options</span>
        <FilterSelect
          v-model="selectedOption"
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
        <label class="font-weight-500 pl-0 pr-2" :for="`filter-range-min-${position}`">
          {{ rangeMinLabel() }}
        </label>
        <span :id="`filter-range-min-placeholder-${position}`" class="sr-only">
          Start of range in format MM/DD/YYYY
        </span>
        <v-date-input
          :id="`filter-range-min-${position}`"
          v-model.string="rangeMin"
          :aria-required="true"
          :aria-describedby="`filter-range-min-placeholder-${position}`"
          autocomplete="off"
          clearable
          density="compact"
          hide-actions
          hide-details
          :max="rangeMax && dateTimeFromISO(rangeMax)"
          placeholder="MM/DD/YYYY"
          prepend-icon=""
          variant="outlined"
        />
        <label class="font-weight-500 px-2" :for="`filter-range-max-${position}`">
          {{ rangeMaxLabel() }}
        </label>
        <span :id="`filter-range-max-placeholder-${position}`" class="sr-only">
          End of range in format MM/DD/YYYY
        </span>
        <v-date-input
          :id="`filter-range-max-${position}`"
          v-model.string="rangeMax"
          :aria-describedby="`filter-range-max-placeholder-${position}`"
          :aria-required="true"
          autocomplete="off"
          clearable
          density="compact"
          hide-actions
          hide-details
          :min-date="rangeMin && dateTimeFromISO(rangeMin)"
          placeholder="MM/DD/YYYY"
          prepend-icon=""
          variant="outlined"
        />
      </div>
      <div v-if="isUX('range') && filter.validation !== 'date'" class="align-center d-flex">
        <label class="font-weight-500 ml-2 pr-2" :for="`filter-range-min-${position}`">
          {{ rangeMinLabel() }}<span class="sr-only"> starting at</span>
        </label>
        <div>
          <v-text-field
            :id="`filter-range-min-${position}`"
            v-model="rangeMin"
            bg-color="white"
            density="compact"
            hide-details
            :maxlength="rangeInputSize()"
            :size="rangeInputSize()"
            variant="outlined"
          />
        </div>
        <label class="font-weight-500 px-2" :for="`filter-range-max-${position}`">
          {{ rangeMaxLabel() }}<span class="sr-only"> end of range</span>
        </label>
        <div>
          <v-text-field
            :id="`filter-range-max-${position}`"
            v-model="rangeMax"
            bg-color="white"
            density="compact"
            hide-details
            :maxlength="rangeInputSize()"
            :size="rangeInputSize()"
            variant="outlined"
          />
        </div>
      </div>
    </div>
    <div v-if="!isExistingFilter" class="align-center d-flex">
      <div v-if="showAdd">
        <ProgressButton
          id="unsaved-filter-add"
          :action="onClickAddButton"
          :disabled="isSaving"
          :in-progress="isSaving"
          text="Add"
        />
      </div>
      <div v-if="isModifyingFilter && get(filter, 'type.ux')">
        <v-btn
          id="unsaved-filter-reset"
          class="text-uppercase"
          color="primary"
          text="Cancel"
          variant="text"
          @click="reset"
        />
      </div>
    </div>
    <div v-if="useCohortStore().isOwnedByCurrentUser && isExistingFilter" class="ml-auto mr-3">
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
            text="Remove"
            variant="text"
            @click="remove"
          />
        </div>
      </div>
      <div v-if="isModifyingFilter" class="d-flex">
        <v-btn
          :id="`update-added-filter-${position}`"
          color="primary"
          :disabled="disableUpdateButton || isUpdatingExistingFilter"
          size="large"
          @click="onClickUpdateButton"
        >
          <div class="align-center d-flex">
            <div v-if="isUpdatingExistingFilter" class="pr-2">
              <v-progress-circular indeterminate size="16" width="2" />
            </div>
            <div>
              {{ isUpdatingExistingFilter ? 'Updating' : 'Update' }}
            </div>
          </div>
        </v-btn>
        <v-btn
          :id="`cancel-edit-added-filter-${position}`"
          class="font-size-14 text-uppercase"
          :disabled="isUpdatingExistingFilter"
          size="large"
          text="Cancel"
          variant="plain"
          @click="onClickCancelEdit"
        />
      </div>
    </div>
  </div>
  <v-expand-transition class="mx-2 my-4">
    <v-card v-show="errorPerRangeInput" flat>
      <v-alert
        aria-live="polite"
        class="bg-red-lighten-5"
        color="red"
        density="compact"
        role="alert"
        :text="errorPerRangeInput"
        type="warning"
        variant="outlined"
      />
    </v-card>
  </v-expand-transition>
</template>

<script>
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
  isString,
  isUndefined,
  toLower,
  mapValues,
  noop,
  size,
  trim,
  values
} from 'lodash'
import {DateTime} from 'luxon'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {updateFilterOptions} from '@/stores/cohort-edit-session/utils'

export default {
  name: 'FilterRow',
  components: {FilterSelect, ProgressButton},
  props: {
    position: {
      default: 'new',
      required: false,
      type: [Number, String]
    }
  },
  data: () => ({
    disableUpdateButton: false,
    errorPerRangeInput: undefined,
    filter: undefined,
    isExistingFilter: undefined,
    isMenuOpen: false,
    isModifyingFilter: false,
    isUpdatingExistingFilter: false,
    isSaving: false,
    rangeMax: undefined,
    rangeMin: undefined,
    selectedFilter: undefined,
    selectedOption: undefined,
    showAdd: false,
    showRow: true
  }),
  computed: {
    primaryOptions() {
      // If we have only one option-group then flatten the object to an array of options.
      const optionGroups = useCohortStore().filterOptionGroups
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
            let subOptions = []
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
    }
  },
  watch: {
    editMode(newEditMode) {
      // Reset the current filter-row if an edit session is initiated elsewhere.
      if (isNil(newEditMode)) {
        // Nothing is being edited. Let's make sure this row is in default state.
        this.reset()
        this.showRow = true
      } else if (newEditMode === 'add') {
        if (this.isExistingFilter) {
          // User is adding a new filter so other rows, per existing filters, are put back in default state.
          this.reset()
        }
      } else if (newEditMode.match('edit-[0-9]+')) {
        if (this.isExistingFilter) {
          if (newEditMode !== `edit-${this.position}`) {
            // We do not allow two rows to be in edit mode simultaneously. In this case, some other row is entering edit
            // mode so we effectively click cancel on this row.
            this.reset()
          }
        } else {
          // Reset and then hide this 'New Filter' row because user has clicked to edit an existing filter.
          this.reset()
          this.showRow = false
        }
      } else if (newEditMode === 'rename') {
        this.reset()
      }
    },
    rangeMax() {
      this.onRangeUpdate()
    },
    rangeMin() {
      this.onRangeUpdate()
    },
    selectedFilter() {
      this.onSelectFilter()
    },
    selectedOption() {
      this.onSelectFilterOption()
    }
  },
  created() {
    this.reset()
  },
  methods: {
    dateTimeFromISO: DateTime.fromISO,
    formatGPA(value) {
      // Prepend zero in case input is, for example, '.2'. No harm done if input has a leading zero.
      const gpa = '0' + trim(value)
      return parseFloat(gpa).toFixed(3)
    },
    get,
    getDropdownSelectedLabel() {
      if (!this.filter.options[0].header) {
        const option = find(this.filter.options, ['value', this.filter.value])
        return get(option, 'name')
      } else {
        let label = ''
        each(this.filter.options, option => {
          label = option.value === this.filter.value ? `${get(option, 'name')} (${option.group})` : null
          return !label
        })
        return label
      }
    },
    isUX(type) {
      return get(this.filter, 'type.ux') === type
    },
    onClickAddButton() {
      this.isSaving = true
      const cohortStore = useCohortStore()
      switch (get(this.filter, 'type.ux')) {
      case 'dropdown':
        this.filter.value = this.selectedOption.value
        alertScreenReader(`Added ${this.filter.name} filter with value ${this.getDropdownSelectedLabel()}`)
        break
      case 'boolean':
        alertScreenReader(`Added ${this.filter.name}`)
        this.filter.value = true
        break
      case 'range':
        alertScreenReader(`Added ${this.filter.name} filter, ${this.rangeMin} to ${this.rangeMax}`)
        this.updateRangeFilter()
        this.rangeMin = this.rangeMax = undefined
        break
      }
      cohortStore.addFilter(this.filter)
      cohortStore.setModifiedSinceLastSearch(true)
      this.reset()
      updateFilterOptions(this.domain, cohortStore.cohortOwner, cohortStore.filters).then(noop)
    },
    onClickCancelEdit() {
      this.errorPerRangeInput = undefined
      alertScreenReader('Canceled')
      this.isModifyingFilter = false
      useCohortStore().setEditMode(null)
      this.putFocusNewFilterDropdown()
    },
    onClickEditButton() {
      this.disableUpdateButton = false
      const cohortStore = useCohortStore()
      if (this.isUX('dropdown')) {
        // Populate select options, with selected option based on current filter.value.
        const flattenOptions = optGroup => flatten(values(optGroup))
        const findOption = (options, value) => find(options, ['value', value])
        const options = find(flattenOptions(cohortStore.filterOptionGroups), ['key', this.filter.key]).options
        this.filter.options = options
        this.selectedOption = Array.isArray(options) ? findOption(options, this.filter.value) : find(flattenOptions(options), this.filter.value)
        this.putFocusSecondaryDropdown()
      } else if (this.isUX('range')) {
        this.rangeMin = this.filter.value.min
        this.rangeMax = this.filter.value.max
        this.putFocusRange()
      }
      this.isModifyingFilter = true
      cohortStore.setEditMode(`edit-${this.position}`)
      alertScreenReader(`Begin edit of ${this.filter.name} filter`)
    },
    onClickUpdateButton() {
      this.isUpdatingExistingFilter = true
      if (this.isUX('range')) {
        this.updateRangeFilter()
      }
      const cohortStore = useCohortStore()
      cohortStore.updateExistingFilter({index: this.position, updatedFilter: this.filter})
      cohortStore.setModifiedSinceLastSearch(true)
      updateFilterOptions(this.domain, cohortStore.cohortOwner, cohortStore.filters).then(() => {
        this.isModifyingFilter = false
        cohortStore.setEditMode(null)
        alertScreenReader(`${this.filter.name} filter updated`)
        this.isUpdatingExistingFilter = false
      })
    },
    onRangeUpdate() {
      this.disableUpdateButton = false
      this.errorPerRangeInput = undefined
      const trimToNil = v => isUndefined(v) ? v : trim(v) || undefined
      // Convert v-calendar's non-customizable attribute names
      let min = trimToNil(this.rangeMin)
      let max = trimToNil(this.rangeMax)
      const isNilOrNan = v => isNil(v) || isNaN(v)
      const validation = get(this.filter, 'validation')
      if (validation === 'dependents') {
        const isInt = v => /^\d+$/.test(v)
        const isDefinedAndInvalid = v => (isInt(v) && parseInt(v, 10) < 0) || !isInt(v) || isNaN(v)
        if (isDefinedAndInvalid(min) || isDefinedAndInvalid(max)) {
          this.errorPerRangeInput = 'Dependents must be an integer greater than or equal to 0.'
        } else if (parseInt(min, 10) > parseInt(max, 10)) {
          this.errorPerRangeInput = 'Dependents inputs must be in ascending order.'
        }
        this.disableUpdateButton = !!this.errorPerRangeInput || isNilOrNan(min) || isNilOrNan(max) || min > max
      } else if (validation === 'gpa') {
        min = min && parseFloat(min)
        max = max && parseFloat(max)
        const isDefinedAndInvalid = v => (isNumber(v) && v < 0 || v > 4) || isNaN(v)
        if (isDefinedAndInvalid(min) || isDefinedAndInvalid(max)) {
          this.errorPerRangeInput = 'GPA must be a number in the range 0 to 4.'
        } else if (isNumber(min) && isNumber(max) && min > max) {
          this.errorPerRangeInput = 'GPA inputs must be in ascending order.'
        }
        this.disableUpdateButton = !!this.errorPerRangeInput || isNilOrNan(min) || isNilOrNan(max) || min > max
      } else if (validation === 'char[2]') {
        const isValid = s => /^[a-zA-Z][a-zA-Z]?$/.test(s)
        const isBadData = (min && !isValid(min)) || (max && !isValid(max))
        if (isBadData || (min && max && min.toUpperCase() > max.toUpperCase())) {
          // Invalid data or values are descending.
          this.errorPerRangeInput = 'Letters must be in ascending order.'
        }
        this.disableUpdateButton = !!this.errorPerRangeInput || isNilOrNan(min) || isNilOrNan(max) || min > max
      } else if (validation === 'date') {
        const startDate = DateTime.fromISO(min)
        const endDate = DateTime.fromISO(max)
        if (startDate && endDate && startDate > endDate) {
          // Invalid data or values are descending.
          this.errorPerRangeInput = 'Requires end date after start date.'
        }
        this.disableUpdateButton = !!this.errorPerRangeInput || isNilOrNan(min) || isNilOrNan(max)
      } else if (validation) {
        this.disableUpdateButton = true
        this.errorPerRangeInput = `Unrecognized range type: ${validation}`
      }
      this.showAdd = !this.errorPerRangeInput && !isNilOrNan(min) && !isNilOrNan(max)
    },
    onSelectFilter() {
      this.selectedOption = undefined
      this.filter = cloneDeep(this.selectedFilter)
      if (this.filter) {
        const type = get(this.filter, 'type.ux')
        this.showAdd = type === 'boolean'
        alertScreenReader(`${this.filter.name} selected`)
        switch (type) {
        case 'dropdown':
          this.putFocusSecondaryDropdown()
          break
        case 'boolean':
          putFocusNextTick('unsaved-filter-add')
          break
        case 'range':
          putFocusNextTick(`filter-range-min-${this.position}`)
          break
        }
      }
    },
    onSelectFilterOption() {
      this.filter.value = get(this.selectedOption, 'value')
      this.showAdd = !!this.selectedOption
      if (this.selectedOption) {
        putFocusNextTick('unsaved-filter-add')
        alertScreenReader(`${this.selectedOption.name} selected`)
      }
    },
    putFocusNewFilterDropdown() {
      putFocusNextTick('filter-select-primary-new')
    },
    putFocusRange() {
      putFocusNextTick(`filter-range-min-${this.position}`)
    },
    putFocusSecondaryDropdown() {
      putFocusNextTick(`filter-select-secondary-${this.position}`)
    },
    rangeInputSize() {
      let maxLength = undefined
      const validation = get(this.filter, 'validation')
      if (validation === 'char[2]') {
        maxLength = 2
      } else if (validation === 'gpa' || validation === 'dependents') {
        maxLength = 5
      }
      return maxLength
    },
    rangeMaxLabel() {
      let snippet = undefined
      if (this.isModifyingFilter) {
        snippet = toLower(this.filter.label.range[1])
      } else {
        let max = get(this.filter, 'value.max')
        if (max && this.filter.validation === 'date') {
          max = DateTime.fromISO(max).toFormat('DD')
        }
        const labels = get(this.filter.label, 'range')
        snippet = this.rangeMinEqualsMax(this.filter) ? '' : `${labels[1]} ${max}`
      }
      return snippet
    },
    rangeMinEqualsMax(filter) {
      const normalize = key => {
        let value = get(filter, key)
        return isString(value) ? value.toUpperCase() : value
      }
      return normalize('value.min') === normalize('value.max')
    },
    rangeMinLabel() {
      let snippet = undefined
      if (this.isModifyingFilter) {
        snippet = toLower(this.filter.label.range[0])
      } else {
        let min = get(this.filter, 'value.min')
        if (min && this.filter.validation === 'date') {
          min = DateTime.fromISO(min).toFormat('DD')
        }
        const labels = get(this.filter.label, 'range')
        snippet = this.rangeMinEqualsMax(this.filter) ? get(this.filter.label, 'rangeMinEqualsMax') + ' ' + min : `${labels[0]} ${min}`
      }
      return snippet
    },
    remove() {
      useCohortStore().removeFilter(this.position)
      updateFilterOptions(this.domain, useCohortStore().cohortOwner, useCohortStore().filters).then(noop)
      useCohortStore().setEditMode(null)
      this.putFocusNewFilterDropdown()
      alertScreenReader(`${this.filter.label.primary} filter removed`)
    },
    reset() {
      this.errorPerRangeInput = this.selectedFilter = this.selectedOption = undefined
      this.disableUpdateButton = false
      this.showAdd = false
      this.range = mapValues(this.range, () => undefined)
      this.isExistingFilter = this.position !== 'new'
      this.filter = this.isExistingFilter ? cloneDeep(useCohortStore().filters[this.position]) : {}
      this.isModifyingFilter = !this.isExistingFilter
      this.isSaving = false
      this.putFocusNewFilterDropdown()
    },
    size,
    updateRangeFilter() {
      if (this.filter.validation === 'gpa') {
        this.filter.value = {
          min: this.formatGPA(this.rangeMin),
          max: this.formatGPA(this.rangeMax)
        }
      } else if (this.filter.validation === 'date') {
        this.filter.value = {
          min: this.rangeMin.substring(0, 10),
          max: this.rangeMax.substring(0, 10)
        }
      } else {
        this.filter.value = {
          min: this.rangeMin,
          max: this.rangeMax
        }
      }
    },
    useCohortStore
  }
}
</script>

<style>
.vc-day-content:focus {
  background-color: rgba(110, 110, 110, 0.4) !important;
}
</style>

<style scoped>
.date-range-container {
  min-width: 360px;
}
.existing-filter-name {
  width: 26%;
}
.filter-row {
  align-items: center;
  background-color: #f3f3f3;
  border-left: 6px solid rgb(var(--v-theme-primary)) !important;
  min-height: 56px;
}
</style>
