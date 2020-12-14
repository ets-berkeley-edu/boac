<template>
  <div
    v-if="showRow"
    :class="{'pt-2': !isExistingFilter}"
    class="d-flex flex-wrap">
    <div
      v-if="isExistingFilter"
      :id="`existing-filter-${index}`"
      class="existing-filter-name px-2">
      {{ filter.label.primary }}<span class="sr-only"> is filter number {{ index }}</span>
    </div>
    <div
      v-if="isModifyingFilter && !isExistingFilter"
      :id="filterRowPrimaryDropdownId(filterRowIndex)"
      class="filter-row-column-01 mt-1 pr-2">
      <b-dropdown
        id="new-filter-button"
        :aria-labelledby="`new-filter-${index}-label`"
        class="h-100"
        menu-class="min-width-100"
        no-caret
        toggle-class="dd-override"
        variant="link"
      >
        <template slot="button-content">
          <div class="d-flex dropdown-width justify-content-between text-dark">
            <div v-if="$_.get(filter.label, 'primary')">{{ filter.label.primary }}<span class="sr-only">is selected</span></div>
            <div v-if="!$_.get(filter.label, 'primary')"><span class="sr-only">Select </span>New Filter</div>
            <div class="ml-2">
              <font-awesome :icon="isMenuOpen ? 'angle-up' : 'angle-down'" class="menu-caret" />
            </div>
          </div>
        </template>
        <b-dropdown-group
          v-for="(category, mIndex) in menu"
          :id="`primary-filter-group-${filterRowIndex}-${mIndex}`"
          :key="mIndex"
        >
          <div v-for="(subCategory, sIndex) in category" :key="subCategory.key">
            <b-dropdown-item-button v-if="subCategory.disabled" :aria-disabled="true" class="sr-only sr-only-focusable">
              '{{ subCategory.label.primary }}' is disabled.
            </b-dropdown-item-button>
            <b-dropdown-item-button
              :id="`dropdown-primary-menuitem-${subCategory.key}-${filterRowIndex}`"
              :aria-disabled="subCategory.disabled"
              :aria-hidden="subCategory.disabled"
              class="font-size-16 h-100"
              :class="{
                'pb-1': mIndex === menu.length - 1 && sIndex === category.length - 1,
                'pt-1': !mIndex && !sIndex
              }"
              :disabled="subCategory.disabled"
              @click="onSelectFilter(subCategory)"
              @focusin.prevent.stop
              @mouseover.prevent.stop
            >
              <span
                :class="{
                  'font-weight-light pointer-default text-muted': subCategory.disabled,
                  'font-weight-normal text-dark': !subCategory.disabled
                }"
                class="font-size-16"
              >
                {{ subCategory.label.primary }}
              </span>
            </b-dropdown-item-button>
          </div>
          <b-dropdown-divider v-if="mIndex !== (menu.length - 1)" />
        </b-dropdown-group>
      </b-dropdown>
    </div>
    <div v-if="!isModifyingFilter">
      <span class="sr-only">Selected filter value is </span>
      <span v-if="isUX('dropdown')">{{ getDropdownSelectedLabel() }}</span>
      <span v-if="isUX('range')">{{ rangeMinLabel() }} {{ rangeMaxLabel() }}</span>
    </div>
    <div v-if="isModifyingFilter" class="filter-row-column-02 mt-1">
      <span :id="`filter-secondary-${filterRowIndex}-label`" class="sr-only">{{ filter.label }} options</span>
      <div v-if="isUX('dropdown')">
        <b-dropdown
          :id="`filter-row-dropdown-secondary-${filterRowIndex}`"
          :aria-labelledby="`filter-secondary-${filterRowIndex}-label`"
          no-caret
          toggle-class="dd-override"
          variant="link"
          @hidden="isSubMenuOpen = false"
          @shown="isSubMenuOpen = true"
        >
          <template slot="button-content">
            <div class="d-flex dropdown-width justify-content-between text-dark">
              <div v-if="filter.value" class="option-truncate text-left">
                <span class="sr-only">Filter value is </span>
                <span v-if="isUX('dropdown')">{{ getDropdownSelectedLabel() }}</span>
                <span v-if="isUX('range')">{{ rangeMinLabel() }} {{ rangeMaxLabel() }}</span>
              </div>
              <div v-if="!filter.value">Choose...<span class="sr-only"> filter value</span></div>
              <div class="ml-2">
                <font-awesome :icon="isSubMenuOpen ? 'angle-up' : 'angle-down'" class="menu-caret" />
              </div>
            </div>
          </template>
          <div v-if="isGrouped(filter.options)">
            <div v-for="(options, name, gIndex) in groupObjectsBy(filter.options, 'group')" :key="name">
              <b-dropdown-group :id="`${filter.label.primary}-dropdown-group-${name}`" :header="name">
                <div v-for="(option, oIndex) in options" :key="option.key">
                  <b-dropdown-item-button v-if="option.disabled" :aria-disabled="true" class="sr-only sr-only-focusable">
                    '{{ option.name }}' is disabled.
                  </b-dropdown-item-button>
                  <b-dropdown-item-button
                    v-if="option.value !== 'divider'"
                    :id="`${filter.label.primary}-${option.value}`"
                    :aria-disabled="option.disabled"
                    class="h-100"
                    :class="{
                      'pb-1': gIndex === filter.options.length - 1 && oIndex === options.length - 1,
                      'pt-1': !gIndex && !oIndex
                    }"
                    :disabled="option.disabled"
                    @click="updateDropdownValue(option)"
                    @focusin.prevent.stop
                    @mouseover.prevent.stop>
                    <div
                      :class="{
                        'font-weight-light pointer-default text-muted': option.disabled,
                        'font-weight-normal text-dark': !option.disabled
                      }"
                      class="font-size-16 option-truncate">
                      {{ option.name }}
                    </div>
                  </b-dropdown-item-button>
                </div>
              </b-dropdown-group>
            </div>
          </div>
          <div v-if="!isGrouped(filter.options)">
            <div v-for="(option, fIndex) in filter.options" :key="option.key">
              <b-dropdown-item-button v-if="option.disabled" :aria-disabled="true" class="sr-only sr-only-focusable">
                '{{ option.name }}' is disabled.
              </b-dropdown-item-button>
              <b-dropdown-item-button
                v-if="option.value !== 'divider'"
                :id="`${filter.label.primary}-${option.value}`"
                :aria-disabled="option.disabled"
                class="h-100"
                :class="{
                  'pb-1': fIndex === filter.options.length - 1,
                  'pt-1': !fIndex
                }"
                :disabled="option.disabled"
                @click="updateDropdownValue(option)"
                @focusin.prevent.stop
                @mouseover.prevent.stop>
                <div
                  :class="{
                    'font-weight-light pointer-default text-muted': option.disabled,
                    'font-weight-normal text-dark': !option.disabled
                  }"
                  class="font-size-16 option-truncate">
                  {{ option.name }}
                </div>
              </b-dropdown-item-button>
              <b-dropdown-divider v-if="option.value === 'divider'" />
            </div>
          </div>
        </b-dropdown>
      </div>
      <div v-if="isUX('range')" class="filter-range-container">
        <div class="filter-range-label-min">
          {{ rangeMinLabel() }}
        </div>
        <div>
          <span
            :id="isExistingFilter ? `filter-range-min-${index}-label` : 'filter-range-min-label'"
            class="sr-only">beginning of range</span>
          <input
            :id="idRangeMin"
            v-model="range.min"
            :aria-labelledby="isExistingFilter ? `filter-range-min-${index}-label` : 'filter-range-min-label'"
            :maxlength="rangeInputSize()"
            :size="rangeInputSize()"
            class="filter-range-input" />
        </div>
        <div class="filter-range-label-max">
          {{ rangeMaxLabel() }}
        </div>
        <div>
          <span
            :id="isExistingFilter ? `filter-range-max-${index}-label` : 'filter-range-max-label'"
            class="sr-only">end of range</span>
          <input
            :id="idRangeMax"
            v-model="range.max"
            :aria-labelledby="isExistingFilter ? `filter-range-max-${index}-label` : 'filter-range-max-label'"
            :maxlength="rangeInputSize()"
            :size="rangeInputSize()"
            class="filter-range-input" />
        </div>
        <div
          v-if="$_.size(errorPerRangeInput)"
          class="sr-only"
          aria-live="polite"
          tabindex="0"
        >
          Error: {{ errorPerRangeInput }}
        </div>
        <b-popover
          v-if="$_.size(errorPerRangeInput)"
          :show="true"
          :target="isExistingFilter ? `filter-range-max-${index}` : 'filter-range-max'"
          placement="top">
          <span class="has-error">{{ errorPerRangeInput }}</span>
        </b-popover>
      </div>
    </div>
    <div v-if="!isExistingFilter" class="filter-row-column-03 mt-1 pl-0">
      <b-btn
        v-if="showAdd"
        id="unsaved-filter-add"
        class="btn-primary-color-override ml-2"
        variant="primary"
        aria-label="Add this new filter to the search criteria"
        @click="onClickAddButton">
        Add
      </b-btn>
    </div>
    <div
      v-if="isModifyingFilter && $_.get(filter, 'type.ux') && !isExistingFilter"
      class="filter-row-column-04">
      <b-btn
        id="unsaved-filter-reset"
        class="p-0"
        variant="link"
        aria-label="Cancel this filter selection"
        @click="reset">
        Cancel
      </b-btn>
    </div>
    <div v-if="isOwnedByCurrentUser && isExistingFilter" class="ml-auto p-2">
      <div v-if="!isModifyingFilter" class="d-flex flex-row">
        <span v-if="!isUX('boolean')">
          <b-btn
            :id="`edit-added-filter-${index}`"
            :aria-label="`Edit ${filter.label.primary} filter (row ${index})`"
            class="btn-cohort-added-filter pr-1"
            variant="link"
            size="sm"
            @click="onClickEditButton">
            Edit
          </b-btn> |
        </span>
        <b-btn
          :id="`remove-added-filter-${index}`"
          :aria-label="`Remove this ${filter.label.primary} filter`"
          class="btn-cohort-added-filter pl-2 pr-0"
          variant="link"
          size="sm"
          @click="remove">
          Remove
        </b-btn>
      </div>
      <div v-if="isModifyingFilter" class="d-flex flex-row">
        <b-btn
          :id="`update-added-filter-${index}`"
          :aria-label="`Update this ${filter.label.primary} filter`"
          :disabled="disableUpdateButton"
          class="btn-primary-color-override"
          variant="primary"
          size="sm"
          @click="onClickUpdateButton">
          Update
        </b-btn>
        <b-btn
          :id="`cancel-edit-added-filter-${index}`"
          class="btn-cohort-added-filter"
          variant="link"
          aria-label="Cancel update"
          size="sm"
          @click="onClickCancelEdit">
          Cancel
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession'
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'FilterRow',
  mixins: [CohortEditSession, Context, Util],
  props: {
    index: {
      default: undefined,
      required: false,
      type: Number
    }
  },
  data: () => ({
    disableUpdateButton: false,
    errorPerRangeInput: undefined,
    filter: undefined,
    isExistingFilter: undefined,
    isMenuOpen: false,
    isModifyingFilter: undefined,
    isSubMenuOpen: false,
    range: {
      min: undefined,
      max: undefined
    },
    showAdd: false,
    showRow: true,
    valueOriginal: undefined
  }),
  computed: {
    filterRowIndex() {
      return this.isExistingFilter ? this.index : 'new'
    },
    idRangeMax() {
      return this.isExistingFilter
        ? `filter-range-max-${this.index}`
        : 'filter-range-max'
    },
    idRangeMin() {
      return this.isExistingFilter
        ? `filter-range-min-${this.index}`
        : 'filter-range-min'
    }
  },
  watch: {
    editMode(newEditMode) {
      // Reset the current filter-row if an edit session is initiated elsewhere.
      if (this.$_.isNil(newEditMode)) {
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
          if (newEditMode !== `edit-${this.index}`) {
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
        const trimToNil = v => this.$_.isUndefined(v) ? v : this.$_.trim(v) || undefined
        let min = trimToNil(this.$_.get(rangeObject, 'min'))
        let max = trimToNil(this.$_.get(rangeObject, 'max'))
        const isNilOrNan = v => this.$_.isNil(v) || this.$_.isNaN(v)
        if (this.filter.validation === 'dependents') {
          const isInt = v => /^\d+$/.test(v)
          const isDefinedAndInvalid = v => (isInt(v) && parseInt(v, 10) < 0) || !isInt(v) || this.$_.isNaN(v)
          if (isDefinedAndInvalid(min) || isDefinedAndInvalid(max)) {
            this.errorPerRangeInput = 'Dependents must be an integer greater than or equal to 0.'
          } else if (parseInt(min, 10) > parseInt(max, 10)) {
            this.errorPerRangeInput = 'Dependents inputs must be in ascending order.'
          }
          this.disableUpdateButton = !!this.errorPerRangeInput || isNilOrNan(min) || isNilOrNan(max) || min > max
        } else if (this.filter.validation === 'gpa') {
          min = min && parseFloat(min)
          max = max && parseFloat(max)
          const isDefinedAndInvalid = v => (this.$_.isNumber(v) && v < 0 || v > 4) || this.$_.isNaN(v)
          if (isDefinedAndInvalid(min) || isDefinedAndInvalid(max)) {
            this.errorPerRangeInput = 'GPA must be a number in the range 0 to 4.'
          } else if (this.$_.isNumber(min) && this.$_.isNumber(max) && min > max) {
            this.errorPerRangeInput = 'GPA inputs must be in ascending order.'
          }
          this.disableUpdateButton = !!this.errorPerRangeInput || isNilOrNan(min) || isNilOrNan(max) || min > max
        } else if (this.filter.validation === 'char') {
          const isLetter = char => /^[a-zA-Z]$/.test(char)
          const badData = () => (min && !isLetter(min)) || (max && !isLetter(max))
          const descending = () => min && max && this.$_.upperCase(min) > this.$_.upperCase(max)
          if (badData() || descending()) {
            this.errorPerRangeInput = 'Requires letters in ascending order.'
          }
          this.disableUpdateButton = !!this.errorPerRangeInput || isNilOrNan(min) || isNilOrNan(max) || min > max
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
    this.valueOriginal = this.filter && this.$_.cloneDeep(this.filter.value)
  },
  methods: {
    isGrouped: options => !!options['0'].group,
    filterRowPrimaryDropdownId: index => `filter-row-dropdown-primary-${index}`,
    filterRowSecondaryDropdownId: index => `filter-row-dropdown-secondary-${index}`,
    formatGPA(value) {
      // Prepend zero in case input is, for example, '.2'. No harm done if input has a leading zero.
      const gpa = '0' + this.$_.trim(value)
      return parseFloat(gpa).toFixed(3)
    },
    getDropdownSelectedLabel() {
      const option = this.$_.find(this.filter.options, ['value', this.filter.value])
      const label = this.$_.get(option, 'name')
      return this.isGrouped(this.filter.options) ? `${label} (${option.group})` : label
    },
    isUX(type) {
      return this.$_.get(this.filter, 'type.ux') === type
    },
    onClickAddButton() {
      const announce = alert => {
        this.alertScreenReader(alert)
        this.$ga.cohortEvent(this.cohortId, this.cohortName || '', alert)
      }
      switch (this.$_.get(this.filter, 'type.ux')) {
      case 'dropdown':
        announce(`Added ${this.filter.label.primary} filter with value ${this.getDropdownSelectedLabel()}`)
        break
      case 'boolean':
        announce(`Added ${this.filter.label.primary}`)
        this.filter.value = true
        break
      case 'range':
        announce(`Added ${this.filter.label.primary} filter, ${this.range.min} to ${this.range.max}`)
        this.filter.value = {
          min: this.filter.validation === 'gpa' ? this.formatGPA(this.range.min) : this.range.min.toUpperCase(),
          max: this.filter.validation === 'gpa' ? this.formatGPA(this.range.max) : this.range.max.toUpperCase()
        }
        this.range.min = this.range.max = undefined
        break
      }
      this.addFilter(this.filter)
      this.reset()
      this.putFocusNewFilterDropdown()
    },
    onClickCancelEdit() {
      this.alertScreenReader('Cancelled')
      this.isModifyingFilter = false
      this.setEditMode(null)
      this.putFocusNewFilterDropdown()
    },
    onClickEditButton() {
      this.disableUpdateButton = false
      if (this.isUX('dropdown')) {
        const category = this.$_.find(this.$_.flatten(this.menu), ['key', this.filter.key])
        this.filter.options = category.options
      } else if (this.isUX('range')) {
        this.range.min = this.filter.value.min
        this.range.max = this.filter.value.max
      }
      this.isModifyingFilter = true
      this.setEditMode(`edit-${this.index}`)
      this.putFocusSecondaryDropdown()
      this.alertScreenReader(`Begin edit of ${this.filter.label.primary} filter`)
    },
    onClickUpdateButton() {
      if (this.isUX('range')) {
        const isGPA = this.filter.validation === 'gpa'
        this.filter.value = {
          min: isGPA ? this.formatGPA(this.range.min) : this.range.min,
          max: isGPA ? this.formatGPA(this.range.max) : this.range.max
        }
      }
      this.updateExistingFilter({index: this.index, updatedFilter: this.filter}).then(() => {
        this.isModifyingFilter = false
        this.setEditMode(null)
        let alert = `${this.filter.label.primary} filter updated`
        this.alertScreenReader(alert)
        this.$ga.cohortEvent(this.cohortId, this.cohortName, alert)
      })
    },
    onSelectFilter(filter) {
      this.filter = this.$_.cloneDeep(filter)
      this.showAdd = filter.type.ux === 'boolean'
      this.alertScreenReader(`${filter.label.primary} selected`)
      switch (filter.type.ux) {
      case 'dropdown':
        this.putFocusSecondaryDropdown()
        break
      case 'boolean':
        this.putFocusNextTick('unsaved-filter-add')
        break
      case 'range':
        this.putFocusNextTick(this.idRangeMin)
        break
      }
    },
    putFocusNewFilterDropdown() {
      this.putFocusNextTick(this.filterRowPrimaryDropdownId('new'), 'button')
    },
    putFocusSecondaryDropdown() {
      this.putFocusNextTick(
        this.filterRowSecondaryDropdownId(this.filterRowIndex),
        'button'
      )
    },
    rangeInputSize() {
      let maxLength = undefined
      if (this.filter.validation === 'char') {
        maxLength = 1
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
        const min = this.$_.get(this.filter, 'value.min')
        const max = this.$_.get(this.filter, 'value.max')
        const minEqualsMax = !this.$_.isNil(min) && min === max
        const labels = this.$_.get(this.filter.label, 'range')
        snippet = minEqualsMax ? '' : `${labels[1]} ${max}`
      }
      return snippet
    },
    rangeMinLabel() {
      let snippet = undefined
      if (this.isModifyingFilter) {
        snippet = this.filter.label.range[0]
      } else {
        const min = this.$_.get(this.filter, 'value.min')
        const max = this.$_.get(this.filter, 'value.max')
        const minEqualsMax = !this.$_.isNil(min) && min === max
        const labels = this.$_.get(this.filter.label, 'range')
        snippet = minEqualsMax ? this.$_.get(this.filter.label, 'rangeMinEqualsMax') + ' ' + min : `${labels[0]} ${min}`
      }
      return snippet
    },
    remove() {
      this.removeFilter(this.index)
      this.setEditMode(null)
      this.putFocusNewFilterDropdown()
      let alert = `${this.filter.label.primary} filter removed`
      this.alertScreenReader(alert)
      this.$ga.cohortEvent(this.cohortId, this.cohortName || '', alert)
    },
    reset() {
      this.disableUpdateButton = false
      this.showAdd = false
      this.range = this.$_.mapValues(this.range, () => undefined)
      if (this.$_.isNil(this.index)) {
        this.filter = {}
        this.isExistingFilter = false
        this.isModifyingFilter = true
      } else {
        this.filter = this.$_.cloneDeep(this.filters[this.index])
        this.isExistingFilter = true
        this.isModifyingFilter = false
      }
      this.putFocusNewFilterDropdown()
    },
    updateDropdownValue(option) {
      if (option) {
        this.filter.value = option.value
        this.showAdd = true
        this.putFocusNextTick('unsaved-filter-add')
        this.alertScreenReader(`${option.name} selected`)
      }
    }
  }
}
</script>

<style scoped>
.btn-cohort-added-filter {
  text-transform: uppercase;
  font-size: 0.8em;
  padding: 4px 1px 5px 5px;
}
.filter-row-column-01 .b-dropdown,
.filter-row-column-02 .b-dropdown {
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
.filter-row-column-01 .option-truncate {
  width: 330px;
}
.filter-row-column-01 .dropdown-width {
  width: 260px;
}
.filter-row-column-02 {
  flex: 0;
}
.filter-row-column-02 .option-truncate {
  width: 340px;
}
.filter-row-column-02 .dropdown-width {
  width: 320px;
}
.filter-row-column-03 {
  flex-basis: auto;
}
.filter-row-column-03 button {
  height: 40px;
  margin-left: 10px;
  width: 80px;
}
.filter-row-column-04 {
  flex: 1;
  vertical-align: middle;
}
.filter-row-column-04 button {
  margin: 8px 0 0 10px;
}
.existing-filter-name {
  width: 260px;
}
.filter-range-container {
  display: flex;
  flex-direction: row;
  padding-right: 15px;
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
  padding: 8px 15px 8px 17px;
  text-transform: uppercase;
}
.menu-caret {
  font-size: 22px;
}
.pointer-default {
  cursor: default;
}
.option-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
