<template>
  <div>
    <div class="sr-only" aria-live="polite">{{ filterUpdateStatus }}</div>
    <div class="cohort-added-filter-name">
      <span v-if="!isModifyingFilter">{{ filter.name }}</span>
      <b-dropdown id="draft-filter"
                  class="btn-filter m-md-2"
                  :disabled="disableCategoryDropdown"
                  v-if="isModifyingFilter">
        <template slot="button-content">
          <div class="d-flex align-items-center">
            <span class="b-link-text">{{ filter.name || 'New Filter' }}</span><i class="ml-1 fas fa-caret-down b-link-text"></i>
          </div>
        </template>
        <div role="group"
             v-for="(category, index) in menu"
             :key="index">
          <b-dropdown-item v-for="subCategory in category"
                           :key="subCategory.key"
                           @click="setFilterCategory(subCategory)"
                           :disabled="subCategory.disabled">{{ subCategory.name }}</b-dropdown-item>
          <b-dropdown-divider v-if="index !== (menu.length - 1)"></b-dropdown-divider>
        </div>
      </b-dropdown>
    </div>
    <div class="cohort-added-subcategory-name">
      <span v-if="!isModifyingFilter">{{ filter.valueLabel }}</span>
      <div class="cohort-filter-draft-column-02" v-if="isModifyingFilter && filter.type === 'array'">
        <b-dropdown id="filter-subcategory"
                    class="btn-filter btn-filter-subcategory">
          <template slot="button-content">
            <div class="d-flex align-items-center">
              <div class="b-link-text">{{ filter.valueLabel || 'Choose...' }}</div><i class="ml-1 fas fa-caret-down b-link-text"></i>
            </div>
          </template>
          <b-dropdown-item v-for="option in filter.options"
                           :key="option.key"
                           :disabled="option.disabled"
                           @click="setFilterValue(option)">{{ option.name }}</b-dropdown-item>
        </b-dropdown>
        <!--
          Subcategory type: 'range'
        -->
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

    </div>
    <div class="cohort-added-filter-controls">
      <div class="cohort-filter-draft-column-03">
        <b-btn type="button"
               id="unsaved-filter-add"
               aria-label="Add filter to search criteria"
               @click="add()"
               v-if="showAdd && !isExistingFilter">
          Add
        </b-btn>
      </div>
      <div class="cohort-filter-draft-column-04"
           v-if="isModifyingFilter && !isExistingFilter && filter.type">
        <button type="button"
                id="unsaved-filter-reset"
                aria-label="Cancel new filter selection"
                class="btn-link cohort-manage-btn-link"
                @click="reset()">
          Cancel
        </button>
      </div>
      <div class="cohort-added-filter-buttons"
           :class="{'disabled-link': disableEdit}"
           v-if="isOwnedByCurrentUser">
        <div v-if="!isModifyingFilter && isExistingFilter">
          <b-btn variant="link"
                 :id="`edit-added-filter-${index}`"
                 aria-label="Edit filter"
                 class="btn-link btn-cohort-added-filter"
                 :disabled="disableEdit"
                 @click="edit()">
            <span :class="{'disabled-link': disableEdit}">Edit</span>
          </b-btn> |
        </div>
        <div v-if="!isModifyingFilter && isExistingFilter">
          <b-btn variant="link"
                 :id="`remove-added-filter-${index}`"
                 aria-label="Remove filter"
                 class="btn-link btn-cohort-added-filter"
                 :disabled="disableEdit"
                 @click="removeFilter(index)">
            <span :class="{'disabled-link': disableEdit}">Remove</span>
          </b-btn>
        </div>
        <div v-if="isModifyingFilter && isExistingFilter">
          <b-btn :id="`update-added-filter-${index}`"
                 aria-label="Update filter"
                 class="btn btn-primary"
                 uib-popover-html="filter.error.popoverHtml"
                 popover-class="has-error"
                 popover-is-open="filter.error.isPopoverOpen"
                 popover-placement="top-left"
                 @click="updateExisting()">
            Update
          </b-btn> |
        </div>
        <div v-if="isModifyingFilter && isExistingFilter">
          <b-btn variant="link"
                 :id="`cancel-edit-added-filter-${index}`"
                 aria-label="Cancel"
                 class="btn-cohort-added-filter"
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
    filter: undefined,
    filterUpdateStatus: undefined,
    isExistingFilter: undefined,
    isModifyingFilter: undefined,
    range: {
      start: undefined,
      end: undefined
    },
    showAdd: false,
    subcategoryError: undefined
  }),
  created() {
    this.reset();
  },
  computed: {
    disableCategoryDropdown() {
      return !this.isExistingFilter && this.editMode && this.editMode !== 'add';
    },
    disableEdit() {
      return this.editMode !== null;
    }
  },
  methods: {
    add() {
      this.addFilter(this.filter);
      this.reset();
    },
    cancel() {
      this.isModifyingFilter = false;
      this.setEditMode(null);
    },
    edit() {
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
      this.filter.key = menuItem.key;
      this.filter.name = menuItem.name;
      this.filter.subcategoryHeader = menuItem.subcategoryHeader;
      this.filter.options = menuItem.options;
      this.filter.type = menuItem.type;
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
  }
};
</script>
