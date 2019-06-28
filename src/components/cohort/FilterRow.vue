<template>
  <div
    v-if="showRow"
    class="d-flex flex-wrap"
    :class="{'pt-2': !isExistingFilter}">
    <div
      v-if="isExistingFilter"
      :id="`existing-name-${index}`"
      class="existing-filter-name p-2">
      <span class="sr-only">Filter name:</span> {{ filter.name }}
    </div>
    <div
      v-if="isModifyingFilter && !isExistingFilter"
      :id="filterRowPrimaryDropdownId(filterRowIndex)"
      class="cohort-filter-draft-column-01 pr-2">
      <div class="sr-only" aria-live="polite">{{ screenReaderAlert }}</div>
      <b-dropdown
        id="new-filter-button"
        toggle-class="dd-override"
        variant="link"
        no-caret>
        <template slot="button-content">
          <div class="dropdown-width d-flex justify-content-between text-dark">
            <div v-if="filter.name"><span class="sr-only">Filter:</span> {{ filter.name || 'New Filter' }}</div>
            <div v-if="!filter.name"><span class="sr-only">Select a </span>New Filter</div>
            <div>
              <font-awesome :icon="isMenuOpen ? 'angle-up' : 'angle-down'" class="menu-caret" />
            </div>
          </div>
        </template>
        <div
          v-for="(category, mIndex) in menu"
          :key="mIndex"
          role="group"
          :aria-labelledby="'filter-option-group-header-' + mIndex">
          <b-dropdown-header :id="'filter-option-group-header-' + mIndex" class="sr-only">
            Filter option group {{ mIndex + 1 }} of {{ menu.length }}
          </b-dropdown-header>
          <b-dropdown-item
            v-for="subCategory in category"
            :id="`dropdown-primary-menuitem-${subCategory.key}-${filterRowIndex}`"
            :key="subCategory.key"
            class="dropdown-item"
            :aria-disabled="subCategory.disabled"
            :disabled="subCategory.disabled"
            @click="setFilterCategory(subCategory)"
            @mouseover.prevent.stop>
            <span
              class="font-size-16"
              :class="{
                'font-weight-light pointer-default text-muted': subCategory.disabled,
                'font-weight-normal text-dark': !subCategory.disabled
              }">{{ subCategory.name }}</span>
          </b-dropdown-item>
          <b-dropdown-divider v-if="mIndex !== (menu.length - 1)"></b-dropdown-divider>
        </div>
      </b-dropdown>
    </div>
    <div v-if="!isModifyingFilter">
      <span class="sr-only">Selected filter value: </span>{{ valueLabel }}
    </div>
    <div
      v-if="isModifyingFilter"
      class="cohort-filter-draft-column-02">
      <div
        v-if="filter.type === 'array'"
        :id="`filter-row-dropdown-secondary-${filterRowIndex}`">
        <b-dropdown
          toggle-class="dd-override"
          variant="link"
          no-caret>
          <template slot="button-content">
            <div class="dropdown-width d-flex justify-content-between text-secondary">
              <div v-if="valueLabel"><span class="sr-only">Selected value is </span>{{ valueLabel }}</div>
              <div v-if="!valueLabel">Choose...<span class="sr-only"> a filter value option</span></div>
              <div>
                <font-awesome :icon="isMenuOpen ? 'angle-up' : 'angle-down'" class="menu-caret" />
              </div>
            </div>
          </template>
          <b-dropdown-item
            v-for="option in filter.options"
            :id="`${filter.name}-${option.value}`"
            :key="option.key"
            class="dropdown-item"
            :aria-disabled="option.disabled"
            :disabled="option.disabled"
            @click="typeArrayUpdateValue(option)"
            @mouseover.prevent.stop>
            <span
              class="font-size-16"
              :class="{
                'font-weight-light pointer-default text-muted': option.disabled,
                'font-weight-normal text-dark': !option.disabled
              }">{{ option.name }}</span>
          </b-dropdown-item>
        </b-dropdown>
      </div>
      <div v-if="filter.type === 'range'" class="filter-range-container">
        <div class="filter-range-label-start">
          {{ filter.subcategoryHeader[0] }}
        </div>
        <div>
          <span
            :id="isExistingFilter ? `filter-${index}-range-start-label` : 'filter-range-start-label'"
            class="sr-only">beginning of range</span>
          <input
            :id="filterRangeStartInputId"
            v-model="range.start"
            class="filter-range-input"
            :aria-labelledby="isExistingFilter ? `filter-${index}-range-start-label` : 'filter-range-start-label'"
            maxlength="1" />
        </div>
        <div class="filter-range-label-stop">
          {{ filter.subcategoryHeader[1] }}
        </div>
        <div>
          <span
            :id="isExistingFilter ? `filter-${index}-range-stop-label` : 'filter-range-stop-label'"
            class="sr-only">end of range</span>
          <input
            v-model="range.stop"
            class="filter-range-input"
            :aria-labelledby="isExistingFilter ? `filter-${index}-range-stop-label` : 'filter-range-stop-label'"
            maxlength="1">
        </div>
        <div class="sr-only" aria-live="polite">{{ range.error }}</div>
        <b-popover
          v-if="size(range.error)"
          :show="true"
          :target="isExistingFilter ? `filter-${index}-range-start` : 'filter-range-start'"
          placement="top">
          <span class="has-error">{{ range.error }}</span>
        </b-popover>
      </div>
    </div>
    <div v-if="!isExistingFilter" class="cohort-filter-draft-column-03 pl-0">
      <b-btn
        v-if="showAdd"
        id="unsaved-filter-add"
        class="btn-primary-color-override ml-2"
        variant="primary"
        aria-label="Add this new filter to the search criteria"
        @click="addNewFilter()">
        Add
      </b-btn>
    </div>
    <div
      v-if="isModifyingFilter && filter.type && !isExistingFilter"
      class="cohort-filter-draft-column-04">
      <b-btn
        id="unsaved-filter-reset"
        class="p-0"
        variant="link"
        aria-label="Cancel this filter selection"
        @click="reset()">
        Cancel
      </b-btn>
    </div>
    <div v-if="isOwnedByCurrentUser && isExistingFilter" class="ml-auto p-2">
      <div v-if="!isModifyingFilter" class="d-flex flex-row">
        <span v-if="filter.type !== 'boolean'">
          <b-btn
            :id="`edit-added-filter-${index}`"
            class="btn-cohort-added-filter pr-1"
            variant="link"
            :aria-label="`Edit this ${filter.name} filter`"
            size="sm"
            @click="editExistingFilter()">
            Edit
          </b-btn> |
        </span>
        <b-btn
          :id="`remove-added-filter-${index}`"
          class="btn-cohort-added-filter pl-2 pr-0"
          variant="link"
          :aria-label="`Remove this ${filter.name} filter`"
          size="sm"
          @click="remove()">
          Remove
        </b-btn>
      </div>
      <div v-if="isModifyingFilter" class="d-flex flex-row">
        <b-btn
          :id="`update-added-filter-${index}`"
          class="btn-primary-color-override"
          variant="primary"
          :aria-label="`Update this ${filter.name} filter`"
          size="sm"
          @click="updateButtonClick()">
          Update
        </b-btn>
        <b-btn
          :id="`cancel-edit-added-filter-${index}`"
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
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'FilterRow',
  mixins: [CohortEditSession, UserMetadata, Util],
  props: {
    index: Number
  },
  data: () => ({
    filter: undefined,
    isExistingFilter: undefined,
    isMenuOpen: false,
    isModifyingFilter: undefined,
    // TODO: Can we get rid of 'range' object and bind form input to filter.value[0] and filter.value[1]?
    range: {
      start: undefined,
      stop: undefined,
      error: undefined
    },
    screenReaderAlert: undefined,
    showAdd: false,
    showRow: true,
    subcategoryError: undefined,
    valueLabel: undefined,
    valueOriginal: undefined
  }),
  computed: {
    filterRangeStartInputId() {
      return this.isExistingFilter
        ? `filter-${this.index}-range-start`
        : 'filter-range-start';
    },
    filterRowIndex() {
      return this.isExistingFilter ? this.index : 'new';
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
        if (this.showAdd) {
          this.putFocusNextTick('unsaved-filter-add');
        }
      },
      deep: true
    }
  },
  created() {
    this.reset();
    this.valueOriginal = this.filter && this.filter.value;
  },
  methods: {
    addNewFilter() {
      switch (this.filter.type) {
        case 'array':
          this.screenReaderAlert = `Added ${
            this.filter.name
          } filter with value ${this.valueLabel}`;
          break;
        case 'boolean':
          this.screenReaderAlert = `Added ${this.filter.name} filter`;
          this.filter.value = true;
          break;
        case 'range':
          this.screenReaderAlert = `Added ${this.filter.name} filter: ${
            this.range.start
          } to ${this.range.stop}`;
          this.filter.value = [this.range.start, this.range.stop];
          break;
      }
      this.addFilter(this.filter);
      this.reset();
      this.putFocusNewFilterDropdown();
      this.gaCohortEvent({
        id: this.cohortId,
        name: this.cohortName || '',
        action: this.screenReaderAlert
      });
    },
    cancelEditExisting() {
      this.screenReaderAlert = 'Cancelled';
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
        case 'range':
          this.range.start = this.filter.value[0];
          this.range.stop = this.filter.value[1];
          break;
      }
      this.isModifyingFilter = true;
      this.setEditMode(`edit-${this.index}`);
      this.putFocusSecondaryDropdown();
      this.screenReaderAlert = `Begin edit of ${this.filter.name} filter`;
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
      this.screenReaderAlert = `${this.filter.name} filter removed`;
      this.removeFilter(this.index);
      this.setEditMode(null);
      this.putFocusNewFilterDropdown();
      this.gaCohortEvent({
        id: this.cohortId,
        name: this.cohortName || '',
        action: this.screenReaderAlert
      });
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
      this.putFocusNewFilterDropdown();
    },
    setFilterCategory(menuItem) {
      this.valueLabel = undefined;
      this.filter = this.cloneDeep(menuItem);
      this.showAdd = menuItem.type === 'boolean';
      switch (menuItem.type) {
        case 'array':
          this.putFocusSecondaryDropdown();
          break;
        case 'boolean':
          this.putFocusNextTick('unsaved-filter-add');
          break;
        case 'range':
          this.putFocusNextTick(this.filterRangeStartInputId);
          break;
      }
    },
    typeArrayUpdateValue(option) {
      if (option) {
        this.filter.value = option.value;
        this.valueLabel = this.getFilterValueLabel();
        this.showAdd = true;
        this.putFocusNextTick('unsaved-filter-add');
      }
    },
    updateButtonClick() {
      if (this.filter.type === 'range') {
        this.filter.value = [this.range.start, this.range.stop];
      }
      this.valueOriginal = this.filter.value;
      this.updateExistingFilter({
        index: this.index,
        updatedFilter: this.filter
      });
      this.screenReaderAlert = `${this.filter.name} filter updated`;
      this.gaCohortEvent({
        id: this.cohortId,
        name: this.cohortName,
        action: this.screenReaderAlert
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
  }
};
</script>

<style scoped>
.btn-cohort-added-filter {
  text-transform: uppercase;
  font-size: 0.8em;
  padding: 4px 1px 5px 5px;
}
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
.cohort-filter-draft-column-01 {
  border-left: 6px solid #3b7ea5;
  flex: 0 0 240px;
}
.cohort-filter-draft-column-01 .dropdown-item {
  width: 260px;
}
.cohort-filter-draft-column-01 .dropdown-width {
  width: 240px;
}
.cohort-filter-draft-column-02 {
  flex: 0;
}
.cohort-filter-draft-column-02 .dropdown-item {
  width: 340px;
}
.cohort-filter-draft-column-02 .dropdown-width {
  width: 320px;
}
.cohort-filter-draft-column-03 {
  flex-basis: auto;
}
.cohort-filter-draft-column-03 button {
  height: 40px;
  margin-left: 10px;
  width: 80px;
}
.cohort-filter-draft-column-04 {
  flex: 1;
  vertical-align: middle;
}
.cohort-filter-draft-column-04 button {
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
.filter-range-label-start {
  padding: 10px 8px 0 0;
}
.filter-range-label-stop {
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
  width: 50px;
}
.menu-caret {
  font-size: 22px;
}
.pointer-default {
  cursor: default;
}
</style>
