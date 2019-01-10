<template>
  <div class="cohort-filter-draft-row" v-if="showRow">
    <div class="cohort-added-filter-name" v-if="!isModifyingFilter || isExistingFilter">
      {{ filter.name }}
    </div>
    <div class="cohort-filter-draft-column-01 pr-2" v-if="isModifyingFilter && !isExistingFilter">
      <div class="sr-only" aria-live="polite">{{ filterUpdateStatus }}</div>
      <b-dropdown id="draft-filter"
                  variant="link"
                  no-caret>
        <template slot="button-content">
          <div class="dropdown-content">
            <div>{{ filter.name || 'New Filter' }}</div>
            <div>
              <i :class="{ 'fas fa-angle-up menu-caret': isMenuOpen, 'fas fa-angle-down menu-caret': !isMenuOpen }"></i>
            </div>
          </div>
        </template>
        <div role="group"
             v-for="(category, index) in menu"
             :key="index">
          <b-dropdown-item v-for="subCategory in category"
                           class="dropdown-item"
                           :class="{ 'dropdown-item-disabled': subCategory.disabled, 'dropdown-item-text': !subCategory.disabled }"
                           :key="subCategory.key"
                           @click="setFilterCategory(subCategory)"
                           :disabled="subCategory.disabled">{{ subCategory.name }}</b-dropdown-item>
          <b-dropdown-divider v-if="index !== (menu.length - 1)"></b-dropdown-divider>
        </div>
      </b-dropdown>
    </div>
    <div class="cohort-added-subcategory-name" v-if="!isModifyingFilter">
      <span>{{ filter.valueLabel }}</span>
    </div>
    <div :class="{
            'cohort-added-subcategory-name': isExistingFilter,
            'cohort-filter-draft-column-02': !isExistingFilter && filter.type === 'boolean',
            'cohort-filter-draft-column-02 pr-2': !isExistingFilter && filter.type !== 'boolean'
          }"
         v-if="isModifyingFilter">
      <div v-if="filter.type === 'array'">
        <b-dropdown id="filter-subcategory"
                    variant="link"
                    no-caret>
          <template slot="button-content">
            <div class="dropdown-content">
              <div>{{ filter.valueLabel || 'Choose...' }}</div>
              <div>
                <i :class="{ 'fas fa-angle-up menu-caret': isMenuOpen, 'fas fa-angle-down menu-caret': !isMenuOpen }"></i>
              </div>
            </div>
          </template>
          <b-dropdown-item v-for="option in filter.options"
                           class="dropdown-item"
                           :class="{ 'dropdown-item-disabled': option.disabled, 'dropdown-item-text': !option.disabled }"
                           :key="option.key"
                           @click="setFilterValue(option)"
                           :disabled="option.disabled">{{ option.name }}</b-dropdown-item>
        </b-dropdown>
      </div>
      <div class="filter-range-container" v-if="filter.type === 'range'">
        <div class="filter-range-label-start">
          {{ filter.subcategoryHeader[0] }}
        </div>
        <div>
          <input class="filter-range-input"
                 focus-on="filter.isEditMode"
                 :aria-labelledby="`filter-${filter.key}-subcategory-range-start-label`"
                 v-model="range.start"
                 maxlength="1"/>
        </div>
        <div class="filter-range-label-stop">
          {{ filter.subcategoryHeader[1] }}
        </div>
        <div>
          <input class="filter-range-input"
                 :aria-labelledby="`filter-${filter.key}-subcategory-range-end-label`"
                 v-model="range.stop"
                 maxlength="1">
        </div>
      </div>
    </div>
    <div class="cohort-filter-draft-column-03 pl-0" v-if="!isExistingFilter">
      <b-btn id="unsaved-filter-add"
             class="ml-0"
             aria-label="Add filter to search criteria"
             @click="addNewFilter()"
             v-if="showAdd">
        Add
      </b-btn>
    </div>
    <div class="cohort-filter-draft-column-04"
         v-if="isModifyingFilter && filter.type && !isExistingFilter">
      <b-btn id="unsaved-filter-reset"
             class="cohort-manage-btn-link p-0"
             aria-label="Cancel new filter selection"
             variant="link"
             @click="reset()">
        Cancel
      </b-btn>
    </div>
    <div>
      <div class="cohort-added-filter-controls" v-if="isOwnedByCurrentUser && isExistingFilter">
        <div class="cohort-added-filter-buttons" v-if="!isModifyingFilter">
          <span v-if="filter.type !== 'boolean'">
            <b-btn :id="`edit-added-filter-${index}`"
                   class="btn-cohort-added-filter pr-1"
                   aria-label="Edit filter"
                   variant="link"
                   size="sm"
                   @click="editExistingFilter()">
              Edit
            </b-btn> |
          </span>
          <b-btn :id="`remove-added-filter-${index}`"
                 class="btn-cohort-added-filter pl-2 pr-0"
                 aria-label="Remove filter"
                 variant="link"
                 size="sm"
                 @click="removeFilter(index)">
            Remove
          </b-btn>
        </div>
        <div v-if="isModifyingFilter">
          <b-btn :id="`update-added-filter-${index}`"
                 aria-label="Update filter"
                 variant="primary"
                 size="sm"
                 @click="updateExisting()">
            Update
          </b-btn>
          <b-btn :id="`cancel-edit-added-filter-${index}`"
                 class="btn-cohort-added-filter"
                 aria-label="Cancel"
                 variant="link"
                 size="sm"
                 @click="cancel()">
            Cancel
          </b-btn>
        </div>
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
    filter: {},
    filterUpdateStatus: undefined,
    isExistingFilter: undefined,
    isMenuOpen: false,
    isModifyingFilter: undefined,
    range: {
      start: undefined,
      end: undefined
    },
    showAdd: false,
    showRow: true,
    subcategoryError: undefined
  }),
  created() {
    this.reset();
  },
  methods: {
    addNewFilter() {
      this.addFilter(this.filter);
      this.reset();
    },
    cancel() {
      this.isModifyingFilter = false;
      this.setEditMode(null);
    },
    editExistingFilter() {
      this.isModifyingFilter = true;
      this.setEditMode('edit');
    },
    reset() {
      this.showAdd = false;
      if (this.isNil(this.index)) {
        this.filter = {};
        this.isExistingFilter = false;
        this.isModifyingFilter = true;
      } else {
        this.filter = this.cloneDeep(this.filters[this.index]);
        this.isExistingFilter = true;
        this.isModifyingFilter = false;
        this.updateFilterValueLabel();
      }
    },
    setFilterCategory(menuItem) {
      this.filter = this.cloneDeep(menuItem);
      this.showAdd = menuItem.type === 'boolean';
    },
    setFilterValue(option) {
      if (option) {
        this.filter.value = option.value;
        this.updateFilterValueLabel();
        this.showAdd = true;
      }
    },
    updateExisting() {
      this.updateExistingFilter(this.index, this.filter);
      this.isModifyingFilter = false;
      this.setEditMode(null);
    },
    updateFilterValueLabel() {
      // Update human-readable label
      let h = this.filter.subcategoryHeader;
      switch (this.filter.type) {
        case 'range':
          this.filter.valueLabel = [
            h[0],
            this.filter.value[0],
            h[1],
            this.filter.value[1]
          ].join(' ');
          break;
        case 'array':
          this.filter.valueLabel = this.get(
            this.find(this.filter.options, ['value', this.filter.value]),
            'name'
          );
          break;
        default:
          this.filter.valueLabel = null;
          break;
      }
    }
  },
  watch: {
    editMode(newEditMode) {
      // Reset the current filter-row if an edit session is initiated elsewhere.
      switch (newEditMode) {
        case 'add':
          if (this.isExistingFilter) {
            this.reset();
          }
          break;
        case 'edit':
          if (!this.isExistingFilter) {
            this.showRow = false;
            this.reset();
          } else {
            this.showRow = true;
          }
          break;
        case 'rename':
          this.reset();
          this.showRow = true;
          break;
        default:
          this.showRow = true;
          break;
      }
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
.dropdown-content {
  color: #000;
  display: flex;
  font-weight: 500;
  justify-content: space-between;
  width: 240px;
}
.dropdown-item {
  font-size: 14px;
  padding-top: 3px;
  width: 260px;
}
.dropdown-item-disabled {
  color: #ccc !important;
}
.dropdown-item-text {
  color: #000 !important;
}
.menu-caret {
  font-size: 22px;
}
</style>
