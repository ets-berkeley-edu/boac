<template>
  <div class="d-flex"
       :class="{'pt-2': !isExistingFilter}"
       v-if="showRow">
    <div :id="`existing-name-${index}`"
         class="existing-filter-name p-2"
         v-if="isExistingFilter">
      <span class="sr-only">Filter name:</span> {{ filter.name }}
    </div>
    <div :id="filterRowPrimaryDropdownId(filterRowIndex)"
         class="cohort-filter-draft-column-01 pr-2"
         v-if="isModifyingFilter && !isExistingFilter">
      <div class="sr-only" aria-live="polite">{{ filterUpdateStatus }}</div>
      <b-dropdown variant="link" no-caret>
        <template slot="button-content">
          <div class="dropdown-width d-flex justify-content-between text-dark">
            <div v-if="filter.name"><span class="sr-only">Filter:</span> {{ filter.name || 'New Filter' }}</div>
            <div v-if="!filter.name"><span class="sr-only">Select a </span>New Filter</div>
            <div>
              <i :class="{
                'fas fa-angle-up menu-caret': isMenuOpen,
                'fas fa-angle-down menu-caret': !isMenuOpen
              }"></i>
            </div>
          </div>
        </template>
        <div role="group"
             v-for="(category, index) in menu"
             :key="index">
          <b-dropdown-item v-for="subCategory in category"
                           class="dropdown-item"
                           :class="{
                             'pointer-default text-muted font-weight-light': subCategory.disabled,
                             'text-dark': !subCategory.disabled
                           }"
                           :key="subCategory.key"
                           @click="setFilterCategory(subCategory)"
                           :aria-disabled="subCategory.disabled"
                           :disabled="subCategory.disabled">{{ subCategory.name }}</b-dropdown-item>
          <b-dropdown-divider v-if="index !== (menu.length - 1)"></b-dropdown-divider>
        </div>
      </b-dropdown>
    </div>
    <div v-if="!isModifyingFilter">
      <span class="sr-only">Selected filter value: </span>{{ valueLabel }}
    </div>
    <div class="cohort-filter-draft-column-02"
         v-if="isModifyingFilter">
      <div :id="`filter-row-dropdown-secondary-${filterRowIndex}`"
           v-if="filter.type === 'array'">
        <b-dropdown variant="link"
                    no-caret>
          <template slot="button-content">
            <div class="dropdown-width d-flex justify-content-between text-secondary">
              <div v-if="valueLabel"><span class="sr-only">Selected value is </span>{{ valueLabel }}</div>
              <div v-if="!valueLabel">Choose...<span class="sr-only"> a filter value option</span></div>
              <div>
                <i :class="{
                  'fas fa-angle-up menu-caret': isMenuOpen,
                  'fas fa-angle-down menu-caret': !isMenuOpen
                }"></i>
              </div>
            </div>
          </template>
          <b-dropdown-item :id="`${filter.name}-${option.value}`"
                           class="dropdown-item"
                           :class="{
                             'pointer-default text-muted font-weight-light': option.disabled,
                             'text-dark': !option.disabled
                           }"
                           v-for="option in filter.options"
                           :key="option.key"
                           @click="updateFilterValue(option)"
                           :aria-disabled="option.disabled"
                           :disabled="option.disabled">{{ option.name }}</b-dropdown-item>
        </b-dropdown>
      </div>
      <div class="filter-range-container" v-if="filter.type === 'range'">
        <div class="filter-range-label-start">
          {{ filter.subcategoryHeader[0] }}
        </div>
        <div>
          <span :id="isExistingFilter ? `filter-${index}-range-start-label` : 'filter-range-start-label'"
                class="sr-only">beginning of range</span>
          <input :id="isExistingFilter ? `filter-${index}-range-start` : 'filter-range-start'"
                 class="filter-range-input"
                 v-focus
                 :aria-labelledby="isExistingFilter ? `filter-${index}-range-start-label` : 'filter-range-start-label'"
                 v-model="range.start"
                 maxlength="1"/>
        </div>
        <div class="filter-range-label-stop">
          {{ filter.subcategoryHeader[1] }}
        </div>
        <div>
          <span :id="isExistingFilter ? `filter-${index}-range-stop-label` : 'filter-range-stop-label'"
                class="sr-only">end of range</span>
          <input class="filter-range-input"
                 :aria-labelledby="isExistingFilter ? `filter-${index}-range-stop-label` : 'filter-range-stop-label'"
                 v-model="range.stop"
                 maxlength="1">
        </div>
        <div class="sr-only" aria-live="polite">{{ range.error }}</div>
        <b-popover :show="true"
                   :target="isExistingFilter ? `filter-${index}-range-start` : 'filter-range-start'"
                   placement="top"
                   v-if="size(range.error)">
          <span class="has-error">{{ range.error }}</span>
        </b-popover>
      </div>
    </div>
    <div class="cohort-filter-draft-column-03 pl-0" v-if="!isExistingFilter">
      <b-btn id="unsaved-filter-add"
             class="btn-primary-color-override ml-2"
             variant="primary"
             aria-label="Add this new filter to the search criteria"
             @click="addNewFilter()"
             v-focus
             v-if="showAdd">
        Add
      </b-btn>
    </div>
    <div class="cohort-filter-draft-column-04"
         v-if="isModifyingFilter && filter.type && !isExistingFilter">
      <b-btn id="unsaved-filter-reset"
             class="cohort-manage-btn-link p-0"
             variant="link"
             aria-label="Cancel this filter selection"
             @click="reset()">
        Cancel
      </b-btn>
    </div>
    <div class="ml-auto p-2" v-if="isOwnedByCurrentUser && isExistingFilter">
      <div class="d-flex flex-row" v-if="!isModifyingFilter">
        <span v-if="filter.type !== 'boolean'">
          <b-btn :id="`edit-added-filter-${index}`"
                 class="btn-cohort-added-filter pr-1"
                 variant="link"
                 :aria-label="`Edit this ${filter.name} filter`"
                 size="sm"
                 @click="editExistingFilter()">
            Edit
          </b-btn> |
        </span>
        <b-btn :id="`remove-added-filter-${index}`"
               class="btn-cohort-added-filter pl-2 pr-0"
               variant="link"
               :aria-label="`Remove this ${filter.name} filter`"
               size="sm"
               @click="remove()">
          Remove
        </b-btn>
      </div>
      <div class="d-flex flex-row" v-if="isModifyingFilter">
        <b-btn :id="`update-added-filter-${index}`"
               class="btn-primary-color-override"
               variant="primary"
               :aria-label="`Update this ${filter.name} filter`"
               size="sm"
               @click="updateExisting()">
          Update
        </b-btn>
        <b-btn :id="`cancel-edit-added-filter-${index}`"
               class="btn-cohort-added-filter"
               variant="link"
               aria-label="Cancel update"
               size="sm"
               @click="cancelEditExisting()">
          Cancel
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession';
import Util from '@/mixins/Util';

export default {
  name: 'FilterRow',
  mixins: [CohortEditSession, Util],
  props: {
    index: Number
  },
  data: () => ({
    filter: undefined,
    filterUpdateStatus: undefined,
    isExistingFilter: undefined,
    isMenuOpen: false,
    isModifyingFilter: undefined,
    range: {
      start: undefined,
      stop: undefined,
      error: undefined
    },
    showAdd: false,
    showRow: true,
    subcategoryError: undefined,
    valueLabel: undefined,
    valueOriginal: undefined
  }),
  created() {
    this.reset();
    this.valueOriginal = this.filter && this.filter.value;
  },
  computed: {
    filterRowIndex() {
      return this.isExistingFilter ? this.index : 'new';
    }
  },
  methods: {
    addNewFilter() {
      switch (this.filter.type) {
        case 'array':
          this.filterUpdateStatus = `Added ${
            this.filter.name
          } filter with value ${this.valueLabel}`;
          break;
        case 'boolean':
          this.filterUpdateStatus = `Added ${this.filter.name} filter`;
          this.filter.value = true;
          break;
        case 'range':
          this.filterUpdateStatus = `Added ${this.filter.name} filter: ${
            this.range.start
          } to ${this.range.stop}`;
          this.filter.value = [this.range.start, this.range.stop];
          break;
      }
      this.addFilter(this.filter);
      this.reset();
      this.putFocusNewFilterDropdown();
    },
    cancelEditExisting() {
      this.filterUpdateStatus = 'Cancelled';
      this.isModifyingFilter = false;
      this.filter.value = this.valueOriginal;
      this.valueLabel = this.getFilterValueLabel();
      this.setEditMode(null);
      this.putFocusNewFilterDropdown();
    },
    editExistingFilter() {
      let category = this.find(this.flatten(this.menu), [
        'key',
        this.filter.key
      ]);
      switch (this.filter.type) {
        case 'array':
          this.filter.options = category.options;
          break;
      }
      this.isModifyingFilter = true;
      this.setEditMode(`edit-${this.index}`);
      this.putFocusSecondaryDropdown();
      this.filterUpdateStatus = `Editing existing ${this.filter.name} filter`;
    },
    filterRowPrimaryDropdownId: index => `filter-row-dropdown-primary-${index}`,
    filterRowSecondaryDropdownId: index =>
      `filter-row-dropdown-secondary-${index}`,
    putFocusNewFilterDropdown() {
      this.putFocusNextTick(this.filterRowPrimaryDropdownId('new'), 'button');
    },
    putFocusSecondaryDropdown() {
      this.putFocusNextTick(
        this.filterRowSecondaryDropdownId(this.filterRowIndex),
        'button'
      );
    },
    remove() {
      this.removeFilter(this.index);
      this.setEditMode(null);
      this.putFocusNewFilterDropdown();
    },
    reset() {
      this.showAdd = false;
      this.range = this.mapValues(this.range, () => undefined);
      if (this.isNil(this.index)) {
        this.filter = {};
        this.isExistingFilter = false;
        this.isModifyingFilter = true;
      } else {
        this.filter = this.cloneDeep(this.filters[this.index]);
        this.isExistingFilter = true;
        this.isModifyingFilter = false;
        this.valueLabel = this.getFilterValueLabel();
      }
    },
    setFilterCategory(menuItem) {
      this.valueLabel = undefined;
      this.filter = this.cloneDeep(menuItem);
      this.showAdd = menuItem.type === 'boolean';
      if (menuItem.type === 'array') {
        this.putFocusSecondaryDropdown();
      }
    },
    updateFilterValue(option) {
      if (option) {
        this.filter.value = option.value;
        this.valueLabel = this.getFilterValueLabel();
        this.showAdd = true;
      }
    },
    updateExisting() {
      this.valueOriginal = this.filter.value;
      this.updateExistingFilter({
        index: this.index,
        updatedFilter: this.filter
      });
      this.isModifyingFilter = false;
      this.setEditMode(null);
    },
    getFilterValueLabel() {
      // Update human-readable label
      let label = undefined;
      const h = this.filter.subcategoryHeader;
      const v = this.filter.value;
      switch (this.filter.type) {
        case 'range':
          if (Array.isArray(v) && this.size(v) === 2) {
            label =
              v[0] === v[1]
                ? 'Starts with ' + v[0]
                : [h[0], v[0], h[1], v[1]].join(' ');
          }
          break;
        case 'array':
          label = this.get(
            this.find(this.filter.options, ['value', v]),
            'name'
          );
          break;
      }
      return label;
    }
  },
  watch: {
    editMode(newEditMode) {
      // Reset the current filter-row if an edit session is initiated elsewhere.
      if (this.isNil(newEditMode)) {
        // Nothing is being edited. Let's make sure this row is in default state.
        this.reset();
        this.showRow = true;
      } else if (newEditMode === 'add') {
        if (this.isExistingFilter) {
          // User is adding a new filter so other rows, per existing filters, are put back in default state.
          this.reset();
        }
      } else if (newEditMode.match('edit-[0-9]+')) {
        if (this.isExistingFilter) {
          if (newEditMode !== `edit-${this.index}`) {
            // We do not allow two rows to be in edit mode simultaneously. In this case, some other row is entering edit
            // mode so we effectively click cancel on this row.
            this.reset();
          }
        } else {
          // Reset and then hide this 'New Filter' row because user has clicked to edit an existing filter.
          this.reset();
          this.showRow = false;
        }
      } else if (newEditMode === 'rename') {
        this.reset();
      }
    },
    range: {
      handler(rangeObject) {
        const start = this.trim(this.get(rangeObject, 'start'));
        const stop = this.trim(this.get(rangeObject, 'stop'));
        this.range.error =
          start && stop && start > stop
            ? 'Values must be in ascending order.'
            : undefined;
        this.showAdd = start && stop && !this.range.error;
      },
      deep: true
    }
  }
};
</script>

<style scoped>
.cohort-filter-draft-column-01 .b-dropdown,
.cohort-filter-draft-column-02 .b-dropdown {
  background-color: #f3f3f3;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: #000;
  height: 42px;
  text-align: left;
  vertical-align: middle;
  white-space: nowrap;
}
.dropdown-item {
  font-size: 14px;
  padding-top: 3px;
}
.cohort-filter-draft-column-01 .dropdown-width {
  width: 240px;
}
.cohort-filter-draft-column-02 .dropdown-width {
  width: 320px;
}
.cohort-filter-draft-column-01 .dropdown-item {
  width: 260px;
}
.cohort-filter-draft-column-02 .dropdown-item {
  width: 340px;
}
.existing-filter-name {
  width: 260px;
}
.menu-caret {
  font-size: 22px;
}
.pointer-default {
  cursor: default;
}
</style>
