<template>
  <div>
    <div class="sr-only" aria-live="polite">{{ filterUpdateStatus }}</div>
    <div>
      <div>
        <div class="cohort-filter-draft-row">
          <div class="cohort-filter-draft-column-01">
            <b-form-select id="draft-filter"
                           class="btn-filter"
                           :disabled="disable"
                           v-model="selected">
              <template slot="first">
                <option :value="null" disabled>New Filter</option>
                <optgroup role="group"
                          v-for="(category, index) in menu"
                          :key="index">
                  <option v-for="subCategory in category"
                          :disabled="subCategory.disabled"
                          :key="subCategory.key"
                          :value="subCategory">{{ subCategory.name }}</option>
                </optgroup>
              </template>
            </b-form-select>
          </div>
          <div class="cohort-filter-draft-column-02" v-if="selected">
            <b-form-select id="filter-subcategory"
                           class="btn-filter btn-filter-subcategory"
                           v-model="selectedArrayOption">
              <template slot="first">
                <option :value="null" disabled>Choose...</option>
                <option v-for="option in selected.options"
                        :disabled="option.disabled"
                        :key="option.key"
                        :value="option">{{ option.name }}</option>
              </template>
            </b-form-select>
            <!--
              Subcategory type: 'range'
            -->
            <div class="filter-range-container" v-if="selected.type === 'range'">
              <div class="filter-range-label-start">
                {{ selected.subcategoryHeader[0] }}
              </div>
              <div>
                <input class="filter-range-input"
                       focus-on="filter.isEditMode"
                       :aria-labelledby="`filter-${selected.key}-subcategory-range-start-label`"
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
          <div class="cohort-filter-draft-column-03">
            <b-btn type="button"
                   id="unsaved-filter-add"
                   aria-label="Add filter to search criteria"
                   @click="add()"
                   v-if="showAdd">
              Add
            </b-btn>
          </div>
          <div class="cohort-filter-draft-column-04" v-if="selected">
            <button type="button"
                    id="unsaved-filter-reset"
                    aria-label="Cancel new filter selection"
                    class="btn-link cohort-manage-btn-link"
                    @click="reset()">
              Cancel
            </button>
          </div>
        </div>
        <div class="filter-subcategory-error has-error" v-if="subcategoryError">
          <span data-ng-bind="subcategoryError"></span>
        </div>
      </div>
      <div>
        <b-btn id="unsaved-filter-apply"
               aria-label="Search for students"
               class="btn-filter-draft-apply"
               @click="apply()"
               v-if="showApply">
          Apply
        </b-btn>
        <div v-if="showSave">
          <b-btn id="save-filtered-cohort"
                 aria-label="Save cohort"
                 :class="{'btn-filter-draft-saved': acknowledgeSave, 'btn-primary btn-filter-draft-save': !acknowledgeSave}"
                 @click="save(openCreateCohortModal)">
            <span v-if="acknowledgeSave">Saved</span>
            <span v-if="!acknowledgeSave && cohort">Save Cohort</span>
            <span v-if="!acknowledgeSave && !cohort">Save</span>
          </b-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import CohortEditSession from '@/mixins/CohortEditSession';

export default {
  name: 'AddCohortFilterMenu',
  mixins: [CohortEditSession],
  data: () => ({
    selected: null,
    selectedArrayOption: null,
    range: {
      start: null
    },
    acknowledgeSave: null,
    filterUpdateStatus: null,
    openCreateCohortModal: null,
    showAdd: false,
    showApply: false,
    showSave: false,
    subcategoryError: null
  }),
  computed: {
    disable() {
      return _.includes(['edit', 'rename'], this.pageMode);
    }
  },
  methods: {
    save: _.noop,
    apply: _.noop,
    add() {
      switch (this.selected.type) {
        case 'array':
          this.selected['value'] = this.selectedArrayOption['value'];
          break;
        case 'range':
          this.selected['value'] = 'TODO';
          break;
      }
      this.addFilter(this.selected);
      this.reset();
    },
    reset() {
      this.selected = this.selectedArrayOption = null;
      this.showAdd = false;
      this.showApply = false;
    }
  },
  watch: {
    selected(value) {
      if (value) {
        this.showApply = false;
        this.showAdd = value.type === 'boolean';
        this.selected = value;
        this.setPageMode('add');
      } else {
        this.readyForSave();
      }
    },
    selectedArrayOption(value) {
      if (value) {
        if (this.selected.type === 'array') {
          value['selected'] = true;
        }
        this.showAdd = true;
      }
    }
  }
};
</script>
