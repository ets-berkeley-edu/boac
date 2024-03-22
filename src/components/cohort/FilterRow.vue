<template>
  <div
    v-if="showRow"
    :class="{'pt-2': !isExistingFilter}"
    class="d-flex flex-wrap"
  >
    <div
      v-if="isExistingFilter"
      :id="`existing-filter-${position}`"
      class="existing-filter-name px-2"
    >
      {{ filter.label.primary }}<span class="sr-only"> is filter number {{ position }}</span>
    </div>
    <div
      v-if="isModifyingFilter && !isExistingFilter"
      class="filter-row-column-01 mt-1 pr-2"
    >
      <FilterSelect
        :filter-row-index="position"
        :labelledby="`new-filter-${position}-label`"
        :on-select-change="onSelectFilter"
        :options="prepareFilterOptionGroups()"
        :set-model-object="value => (selectedFilter = value)"
        type="primary"
        :v-model-object="selectedFilter"
      />
    </div>
    <div v-if="!isModifyingFilter">
      <span class="sr-only">Selected filter value is </span>
      <span v-if="isUX('dropdown')">{{ getDropdownSelectedLabel() }}</span>
      <span v-if="isUX('range')">{{ rangeMinLabel() }} {{ rangeMaxLabel() }}</span>
    </div>
    <div v-if="isModifyingFilter" class="filter-row-column-02 mt-1">
      <div v-if="isUX('dropdown')">
        <span :id="`filter-secondary-${position}-label`" class="sr-only">{{ filter.label }} options</span>
        <FilterSelect
          :filter-row-index="position"
          :labelledby="`filter-secondary-${position}-label`"
          :on-select-change="onSelectFilterOption"
          :options="filter.options"
          :set-model-object="value => (selectedOption = value)"
          type="secondary"
          :v-model-object="selectedOption"
        />
      </div>
      <div v-if="isUX('range') && filter.validation === 'date'" :id="`filter-range-date-picker-${position}`" class="d-flex pr-1">
        <v-date-picker
          ref="datePicker"
          v-model="range"
          :attributes="[{key: 'today', dot: true, dates: new Date()}]"
          is-range
          :model-config="{type: 'string', mask: 'YYYY-MM-DD'}"
          @popover-did-show="onPopoverShown"
        >
          <template #default="{ inputValue, inputEvents }">
            <div class="d-flex pr-1">
              <label
                :for="`filter-range-min-${position}`"
                class="pb-2"
                :class="rangeMinLabel() ? 'filter-range-label-min' : ''"
              >
                {{ rangeMinLabel() }}
              </label>
              <div>
                <input
                  :id="`filter-range-min-${position}`"
                  :value="inputValue.start"
                  aria-label="beginning of range"
                  :aria-describedby="`filter-range-min-placeholder-${position}`"
                  class="filter-range-input"
                  maxlength="10"
                  :placeholder="placeholder()"
                  size="12"
                  v-on="inputEvents.start"
                  @focus="appendPopover"
                  @mouseover="appendPopover"
                />
                <div class="filter-range-popover-container" />
                <span :id="`filter-range-min-placeholder-${position}`" class="sr-only">MM/DD/YYYY</span>
              </div>
              <label
                :for="`filter-range-max-${position}`"
                class="filter-range-label-max pb-2"
              >
                {{ rangeMaxLabel() }}
              </label>
              <div>
                <input
                  :id="`filter-range-max-${position}`"
                  :value="inputValue.end"
                  aria-label="end of range"
                  :aria-describedby="`filter-range-max-placeholder-${position}`"
                  class="filter-range-input"
                  maxlength="10"
                  :placeholder="placeholder()"
                  size="12"
                  v-on="inputEvents.end"
                  @focus="appendPopover"
                  @mouseover="appendPopover"
                />
                <div class="filter-range-popover-container" />
                <span :id="`filter-range-max-placeholder-${position}`" class="sr-only">MM/DD/YYYY</span>
              </div>
              <div
                v-if="_size(errorPerRangeInput)"
                class="sr-only"
                aria-live="polite"
              >
                Error: {{ errorPerRangeInput }}
              </div>
              <b-popover
                v-if="_size(errorPerRangeInput)"
                :show="true"
                :target="`filter-range-max-${position}`"
                placement="top"
              >
                <span class="has-error">{{ errorPerRangeInput }}</span>
              </b-popover>
            </div>
          </template>
        </v-date-picker>
      </div>
      <div v-if="isUX('range') && filter.validation !== 'date'" class="d-flex pr-1">
        <label
          :for="`filter-range-min-${position}`"
          class="pb-2"
          :class="rangeMinLabel() ? 'filter-range-label-min' : ''"
        >
          {{ rangeMinLabel() }}<span class="sr-only"> beginning of range</span>
        </label>
        <div>
          <input
            :id="`filter-range-min-${position}`"
            v-model="range.min"
            :maxlength="rangeInputSize()"
            :size="rangeInputSize()"
            :placeholder="placeholder()"
            class="filter-range-input"
          />
        </div>
        <label
          :for="`filter-range-max-${position}`"
          class="filter-range-label-max pb-2"
        >
          {{ rangeMaxLabel() }}<span class="sr-only"> (end of range)</span>
        </label>
        <div>
          <input
            :id="`filter-range-max-${position}`"
            v-model="range.max"
            :maxlength="rangeInputSize()"
            :size="rangeInputSize()"
            :placeholder="placeholder()"
            class="filter-range-input"
          />
        </div>
        <div
          v-if="_size(errorPerRangeInput)"
          class="sr-only"
          aria-live="polite"
        >
          Error: {{ errorPerRangeInput }}
        </div>
        <b-popover
          v-if="_size(errorPerRangeInput)"
          :show="true"
          :target="`filter-range-max-${position}`"
          placement="top"
        >
          <span class="has-error">{{ errorPerRangeInput }}</span>
        </b-popover>
      </div>
    </div>
    <div v-if="!isExistingFilter" class="filter-row-column-03 mt-1 pl-0">
      <v-btn
        v-if="showAdd"
        id="unsaved-filter-add"
        class="btn-primary-color-override ml-2"
        variant="primary"
        @click="onClickAddButton"
      >
        Add
      </v-btn>
    </div>
    <div
      v-if="isModifyingFilter && _get(filter, 'type.ux') && !isExistingFilter"
      class="filter-row-column-04"
    >
      <v-btn
        id="unsaved-filter-reset"
        class="p-0"
        variant="plain"
        @click="reset"
      >
        Cancel
      </v-btn>
    </div>
    <div v-if="isOwnedByCurrentUser && isExistingFilter" class="ml-auto p-2">
      <div v-if="!isModifyingFilter" class="d-flex flex-row">
        <span v-if="!isUX('boolean')">
          <v-btn
            :id="`edit-added-filter-${position}`"
            class="btn-cohort-added-filter pr-1"
            variant="plain"
            size="sm"
            @click="onClickEditButton"
          >
            Edit
          </v-btn> |
        </span>
        <v-btn
          :id="`remove-added-filter-${position}`"
          class="btn-cohort-added-filter pl-2 pr-0"
          variant="plain"
          size="sm"
          @click="remove"
        >
          Remove
        </v-btn>
      </div>
      <div v-if="isModifyingFilter" class="d-flex flex-row">
        <v-btn
          :id="`update-added-filter-${position}`"
          :disabled="disableUpdateButton"
          class="btn-primary-color-override"
          variant="primary"
          size="sm"
          @click="onClickUpdateButton"
        >
          Update
        </v-btn>
        <v-btn
          :id="`cancel-edit-added-filter-${position}`"
          class="btn-cohort-added-filter"
          variant="plain"
          size="sm"
          @click="onClickCancelEdit"
        >
          Cancel
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession'
import Context from '@/mixins/Context'
import FilterSelect from '@/components/cohort/FilterSelect'
import Util from '@/mixins/Util'
import {updateFilterOptions} from '@/stores/cohort-edit-session/utils'
import {DateTime} from 'luxon'


export default {
  name: 'FilterRow',
  components: {FilterSelect},
  mixins: [CohortEditSession, Context, Util],
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
    isModifyingFilter: undefined,
    range: {
      min: undefined,
      max: undefined,
      start: undefined,
      end: undefined
    },
    selectedFilter: undefined,
    selectedOption: undefined,
    showAdd: false,
    showRow: true,
    valueOriginal: undefined
  }),
  watch: {
    editMode(newEditMode) {
      // Reset the current filter-row if an edit session is initiated elsewhere.
      if (this._isNil(newEditMode)) {
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
    range: {
      handler(rangeObject) {
        this.disableUpdateButton = false
        this.errorPerRangeInput = undefined
        const trimToNil = v => this._isUndefined(v) ? v : this._trim(v) || undefined
        // Convert v-calendar's non-customizable attribute names
        if (!rangeObject.min && rangeObject.start) {
          rangeObject.min = rangeObject.start
        }
        if (!rangeObject.max && rangeObject.end) {
          rangeObject.max = rangeObject.end
        }
        let min = trimToNil(rangeObject.min)
        let max = trimToNil(rangeObject.max)
        const isNilOrNan = v => this._isNil(v) || this._isNaN(v)
        if (this.filter.validation === 'dependents') {
          const isInt = v => /^\d+$/.test(v)
          const isDefinedAndInvalid = v => (isInt(v) && parseInt(v, 10) < 0) || !isInt(v) || this._isNaN(v)
          if (isDefinedAndInvalid(min) || isDefinedAndInvalid(max)) {
            this.errorPerRangeInput = 'Dependents must be an integer greater than or equal to 0.'
          } else if (parseInt(min, 10) > parseInt(max, 10)) {
            this.errorPerRangeInput = 'Dependents inputs must be in ascending order.'
          }
          this.disableUpdateButton = !!this.errorPerRangeInput || isNilOrNan(min) || isNilOrNan(max) || min > max
        } else if (this.filter.validation === 'gpa') {
          min = min && parseFloat(min)
          max = max && parseFloat(max)
          const isDefinedAndInvalid = v => (this._isNumber(v) && v < 0 || v > 4) || this._isNaN(v)
          if (isDefinedAndInvalid(min) || isDefinedAndInvalid(max)) {
            this.errorPerRangeInput = 'GPA must be a number in the range 0 to 4.'
          } else if (this._isNumber(min) && this._isNumber(max) && min > max) {
            this.errorPerRangeInput = 'GPA inputs must be in ascending order.'
          }
          this.disableUpdateButton = !!this.errorPerRangeInput || isNilOrNan(min) || isNilOrNan(max) || min > max
        } else if (this.filter.validation === 'char[2]') {
          const isValid = s => /^[a-zA-Z][a-zA-Z]?$/.test(s)
          const isBadData = (min && !isValid(min)) || (max && !isValid(max))
          if (isBadData || (min && max && min.toUpperCase() > max.toUpperCase())) {
            // Invalid data or values are descending.
            this.errorPerRangeInput = 'Requires letters in ascending order.'
          }
          this.disableUpdateButton = !!this.errorPerRangeInput || isNilOrNan(min) || isNilOrNan(max) || min > max
        } else if (this.filter.validation === 'date') {
          const startDate = DateTime.fromJSDate(min)
          const endDate = DateTime.fromJSDate(max)
          if (!(startDate && endDate && startDate.isSameOrBefore(endDate, 'day'))) {
            // Invalid data or values are descending.
            this.errorPerRangeInput = 'Requires end date after start date.'
          }
          this.disableUpdateButton = !!this.errorPerRangeInput || isNilOrNan(min) || isNilOrNan(max)
        } else if (this.filter.validation) {
          this.disableUpdateButton = true
          this.errorPerRangeInput = `Unrecognized range type: ${this.filter.validation}`
        }
        this.showAdd = !this.errorPerRangeInput && !isNilOrNan(min) && !isNilOrNan(max)
      },
      deep: true
    }
  },
  created() {
    this.reset()
    this.valueOriginal = this.filter && this._cloneDeep(this.filter.value)
  },
  methods: {
    appendPopover(e) {
      // Place v-calendar date picker popover where it belongs in the tab order
      const el = document.getElementById(`filter-range-date-picker-${this.position}`)
      const container = e.target.parentElement.querySelector('.filter-range-popover-container')
      this.nextTick(() => {
        const popover = el ? el.querySelector('.vc-popover-content-wrapper') : null
        if (container && popover) {
          container.replaceChildren(popover)
        }
      })
    },
    formatGPA(value) {
      // Prepend zero in case input is, for example, '.2'. No harm done if input has a leading zero.
      const gpa = '0' + this._trim(value)
      return parseFloat(gpa).toFixed(3)
    },
    getDropdownSelectedLabel() {
      if (Array.isArray(this.filter.options)) {
        const option = this._find(this.filter.options, ['value', this.filter.value])
        return this._get(option, 'name')
      } else {
        let label = ''
        this._each(this.filter.options, (options, group) => {
          const option = this._find(options, ['value', this.filter.value])
          label = option && `${this._get(option, 'name')} (${group})`
          return !option
        })
        return label
      }
    },
    isUX(type) {
      return this._get(this.filter, 'type.ux') === type
    },
    onClickAddButton() {
      switch (this._get(this.filter, 'type.ux')) {
      case 'dropdown':
        this.alertScreenReader(`Added ${this.filter.label.primary} filter with value ${this.getDropdownSelectedLabel()}`)
        break
      case 'boolean':
        this.alertScreenReader(`Added ${this.filter.label.primary}`)
        this.filter.value = true
        break
      case 'range':
        this.alertScreenReader(`Added ${this.filter.label.primary} filter, ${this.range.min} to ${this.range.max}`)
        this.updateRangeFilter()
        this.range.min = this.range.max = undefined
        break
      }
      this._unset(this.filter, 'value.start')
      this._unset(this.filter, 'value.end')
      this.addFilter(this.filter)
      this.setModifiedSinceLastSearch(true)
      this.reset()
    },
    onClickCancelEdit() {
      this.alertScreenReader('Canceled')
      this.isModifyingFilter = false
      this.setEditMode(null)
      this.putFocusNewFilterDropdown()
    },
    onClickEditButton() {
      this.disableUpdateButton = false
      if (this.isUX('dropdown')) {
        // Populate select options, with selected option based on current filter.value.
        const flatten = optGroup => this._flatten(this._values(optGroup))
        const find = (options, value) => this._find(options, ['value', value])
        const options = this._find(flatten(this.filterOptionGroups), ['key', this.filter.key]).options
        this.filter.options = options
        this.selectedOption = Array.isArray(options) ? find(options, this.filter.value) : find(flatten(options), this.filter.value)
        this.putFocusSecondaryDropdown()
      } else if (this.isUX('range')) {
        this.range.min = this.range.start = this.filter.value.min
        this.range.max = this.range.end = this.filter.value.max
        this.putFocusRange()
      }
      this.isModifyingFilter = true
      this.setEditMode(`edit-${this.position}`)
      this.alertScreenReader(`Begin edit of ${this.filter.label.primary} filter`)
    },
    onClickUpdateButton() {
      if (this.isUX('range')) {
        this.updateRangeFilter()
      }
      this.updateExistingFilter({index: this.position, updatedFilter: this.filter})
      this.setModifiedSinceLastSearch(true)
      updateFilterOptions(this.domain, this.cohortOwner(), this.filters).then(() => {
        this.isModifyingFilter = false
        this.setEditMode(null)
        this.alertScreenReader(`${this.filter.label.primary} filter updated`)
      })
    },
    onSelectFilter() {
      this.selectedOption = undefined
      this.filter = this._cloneDeep(this.selectedFilter)
      this.showAdd = this._get(this.filter, 'type.ux') === 'boolean'
      if (this.filter) {
        this.alertScreenReader(`${this.filter.label.primary} selected`)
        switch (this.filter.type.ux) {
        case 'dropdown':
          this.putFocusSecondaryDropdown()
          break
        case 'boolean':
          this.putFocusNextTick('unsaved-filter-add')
          break
        case 'range':
          this.putFocusNextTick(`filter-range-min-${this.position}`)
          break
        }
      }
    },
    onSelectFilterOption() {
      this.filter.value = this._get(this.selectedOption, 'value')
      this.showAdd = !!this.selectedOption
      if (this.selectedOption) {
        this.putFocusNextTick('unsaved-filter-add')
        this.alertScreenReader(`${this.selectedOption.name} selected`)
      }
    },
    onPopoverShown(popoverContent) {
      // Fill accessibility gaps in v-calendar date picker popover
      const helpContainer = popoverContent.querySelector('[data-helptext]')
      const nextMonthBtn = popoverContent.querySelector('.is-right')
      const prevMonthBtn = popoverContent.querySelector('.is-left')
      const title = popoverContent.querySelector('.vc-title')
      const weeks = popoverContent.querySelector('.vc-weeks')
      const weekdayLabels = popoverContent.querySelectorAll('.vc-weekday')
      const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
      popoverContent.ariaLabel = 'choose date'
      popoverContent.ariaModal = true
      popoverContent.role = 'dialog'
      if (helpContainer) {
        const helpText = helpContainer.getAttribute('data-helptext')
        const helpEl = document.createElement('span')
        helpEl.className = 'sr-only'
        helpEl.ariaLive = 'polite'
        helpContainer.prepend(helpEl)
        setTimeout(() => {
          helpEl.innerText = helpText
        }, 200)
      }
      if (nextMonthBtn) {
        nextMonthBtn.ariaLabel = 'previous month'
      }
      if (prevMonthBtn) {
        prevMonthBtn.ariaLabel = 'previous month'
      }
      if (title) {
        title.ariaLive = 'polite'
        title.id = `filter-range-popover-title-${this.position}`
      }
      if (weeks) {
        weeks.setAttribute('aria-labelledby', `filter-range-popover-title-${this.position}`)
        weeks.role = 'grid'
      }
      this._each(weekdayLabels, (label, index) => {
        label.abbr = weekdays[index]
      })
    },
    placeholder() {
      if (this.filter.validation === 'date') {
        return 'MM/DD/YYYY'
      } else {
        return ''
      }
    },
    prepareFilterOptionGroups() {
      // If we have only one option-group then flatten the object to an array of options.
      const flatten = this._size(this.filterOptionGroups) === 1
      return flatten ? this._values(this.filterOptionGroups)[0] : this.filterOptionGroups
    },
    putFocusNewFilterDropdown() {
      this.putFocusNextTick('filter-select-primary-new')
    },
    putFocusRange() {
      this.putFocusNextTick(`filter-range-min-${this.position}`)
    },
    putFocusSecondaryDropdown() {
      this.putFocusNextTick(`filter-select-secondary-${this.position}`)
    },
    rangeInputSize() {
      let maxLength = undefined
      if (this.filter.validation === 'char[2]') {
        maxLength = 2
      } else if (this.filter.validation === 'gpa' || this.filter.validation === 'dependents') {
        maxLength = 5
      }
      return maxLength
    },
    rangeMaxLabel() {
      let snippet = undefined
      if (this.isModifyingFilter) {
        snippet = this.filter.label.range[1]
      } else {
        let max = this._get(this.filter, 'value.max')
        if (max && this.filter.validation === 'date') {
          max = DateTime.fromJSDate(max).toFormat('MMM DD, YYYY')
        }
        const labels = this._get(this.filter.label, 'range')
        snippet = this.rangeMinEqualsMax(this.filter) ? '' : `${labels[1]} ${max}`
      }
      return snippet
    },
    rangeMinEqualsMax(filter) {
      const normalize = key => {
        let value = this._get(filter, key)
        return this._isString(value) ? value.toUpperCase() : value
      }
      return normalize('value.min') === normalize('value.max')
    },
    rangeMinLabel() {
      let snippet = undefined
      if (this.isModifyingFilter) {
        snippet = this.filter.label.range[0]
      } else {
        let min = this._get(this.filter, 'value.min')
        if (min && this.filter.validation === 'date') {
          min = DateTime.fromJSDate(min).toFormat('MMM DD, YYYY')
        }
        const labels = this._get(this.filter.label, 'range')
        snippet = this.rangeMinEqualsMax(this.filter) ? this._get(this.filter.label, 'rangeMinEqualsMax') + ' ' + min : `${labels[0]} ${min}`
      }
      return snippet
    },
    remove() {
      this.removeFilter(this.position)
      updateFilterOptions(this.domain, this.cohortOwner(), this.filters).then(this._noop)
      this.setEditMode(null)
      this.putFocusNewFilterDropdown()
      this.alertScreenReader(`${this.filter.label.primary} filter removed`)
    },
    reset() {
      this.selectedFilter = this.selectedOption = undefined
      this.disableUpdateButton = false
      this.showAdd = false
      this.range = this._mapValues(this.range, () => undefined)
      this.isExistingFilter = this.position !== 'new'
      this.filter = this.isExistingFilter ? this._cloneDeep(this.filters[this.position]) : {}
      this.isModifyingFilter = !this.isExistingFilter
      this.putFocusNewFilterDropdown()
    },
    updateRangeFilter() {
      this.filter.value = {
        min: this.range.min,
        max: this.range.max
      }
      if (this.filter.validation === 'gpa') {
        this.filter.value.min = this.formatGPA(this.filter.value.min)
        this.filter.value.max = this.formatGPA(this.filter.value.max)
      }
    }
  }
}
</script>

<style>
.vc-day-content:focus {
  background-color: rgba(110, 110, 110, 0.4) !important;
}
</style>

<style scoped>
.btn-cohort-added-filter {
  text-transform: uppercase;
  font-size: 0.8em;
  padding: 4px 1px 5px 5px;
}
.filter-row-column-01 .custom-select,
.filter-row-column-02 .custom-select {
  background-color: #f3f3f3;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: #000;
  height: 42px;
  text-align: left;
  vertical-align: middle;
  white-space: nowrap;
}
.filter-row-column-01 {
  border-left: 6px solid #3b7ea5;
  flex: 0 0 240px;
}
.filter-row-column-02 {
  flex: 0;
}
.filter-row-column-03 {
  flex-basis: auto;
}
.filter-row-column-03 button {
  height: 40px;
  margin-left: 12px;
  width: 80px;
}
.filter-row-column-04 {
  flex: 1;
  vertical-align: middle;
}
.filter-row-column-04 button {
  margin: 12px 0 0 12px;
}
.existing-filter-name {
  width: 260px;
}
.filter-range-label-min {
  padding: 10px 8px 0 0;
}
.filter-range-label-max {
  padding: 10px 8px 0 10px;
}
.filter-range-input {
  border: 2px solid #ccc;
  border-radius: 8px;
  box-sizing: border-box;
  color: #333;
  font-size: 18px;
  height: 40px;
  padding: 6px 12px 6px 12px;
}
</style>
