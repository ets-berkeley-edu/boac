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
               @click="applyFilters()"
               :disabled="!!editMode"
               v-if="showApplyButton">
          Apply
        </b-btn>
        <div v-if="showSaveButton">
          <b-btn id="save-filtered-cohort"
                 aria-label="Save cohort"
                 :class="{'btn-filter-draft-saved': acknowledgeSave, 'btn-primary btn-filter-draft-save': !acknowledgeSave}"
                 :disabled="!!editMode"
                 @click="save()">
            <span v-if="acknowledgeSave">Saved</span>
            <span v-if="!acknowledgeSave && cohortId">Save Cohort</span>
            <span v-if="!acknowledgeSave && !cohortId">Save</span>
          </b-btn>
          <b-modal id="createCohortModal"
                   v-model="showCreateModal"
                   hide-footer
                   hide-header-close
                   title="Name Your Saved Cohort">
            <CreateCohortModal :cancel="cancelCreateModal"
                               :create="create"/>
          </b-modal>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession';
import CreateCohortModal from '@/components/cohort/CreateCohortModal';

export default {
  name: 'AddCohortFilterMenu',
  mixins: [CohortEditSession],
  components: { CreateCohortModal },
  data: () => ({
    acknowledgeSave: null,
    filterUpdateStatus: null,
    range: {
      start: null
    },
    selected: null,
    selectedArrayOption: null,
    showAdd: false,
    showCreateModal: false,
    subcategoryError: null
  }),
  computed: {
    disable() {
      return this.editMode && this.editMode !== 'add';
    }
  },
  methods: {
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
    cancelCreateModal() {
      this.showCreateModal = false;
    },
    create(name) {
      this.showCreateModal = false;
      this.createCohort(name);
    },
    reset() {
      this.selected = this.selectedArrayOption = null;
      this.showAdd = false;
    },
    save() {
      if (this.cohortId) {
        this.saveCohort();
      } else {
        this.showCreateModal = true;
      }
    }
  },
  watch: {
    selected(value) {
      if (value) {
        this.showAdd = value.type === 'boolean';
        this.selected = value;
        this.setEditMode('add');
      } else {
        this.setEditMode(null);
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
