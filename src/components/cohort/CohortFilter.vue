<template>
  <div>
    <div class="cohort-added-filter-name">
      {{ filter.name }}
    </div>
    <div class="cohort-added-subcategory-name">
      <span v-if="!isEditMode">{{ summary }}</span>
      <!--
      <filter-criteria-edit-subcategory filter="row"
                                        on-option-click="filter.onOptionClick"
                                        watch="row"
                                        v-if="isEditMode"></filter-criteria-edit-subcategory>
                                        -->
    </div>
    <div class="cohort-added-filter-controls">
      <div class="cohort-added-filter-buttons"
           :class="{'disabled-link': disableButtons}"
           v-if="allowEdits">
        <div v-if="!isEditMode">
          <b-btn variant="link"
                 :id="`edit-added-filter-${index}`"
                 aria-label="Edit filter"
                 class="btn-link btn-cohort-added-filter"
                 :disabled="disableButtons"
                 @click="edit()">
            <span :class="{'disabled-link': disableButtons}">Edit</span>
          </b-btn> |
        </div>
        <div v-if="!isEditMode">
          <b-btn variant="link"
                 :id="`remove-added-filter-${index}`"
                 aria-label="Remove filter"
                 class="btn-link btn-cohort-added-filter"
                 :disabled="disableButtons"
                 @click="removeFilter(index)">
            <span :class="{'disabled-link': disableButtons}">Remove</span>
          </b-btn>
        </div>
        <div v-if="isEditMode">
          <b-btn :id="`update-added-filter-${index}`"
                 aria-label="Update filter"
                 class="btn btn-primary"
                 uib-popover-html="filter.error.popoverHtml"
                 popover-class="has-error"
                 popover-is-open="filter.error.isPopoverOpen"
                 popover-placement="top-left"
                 @click="update()">
            Update
          </b-btn> |
        </div>
        <div v-if="isEditMode">
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
import _ from 'lodash';
import CohortEditSession from '@/mixins/CohortEditSession';

// -----
// TODO: When a new filter row is added, send the set of selected filters to the server
//       in order to get up to date menu options, with proper disabling of
//       certain options (primary and secondary)
// -----

export default {
  name: 'CohortFilter',
  mixins: [CohortEditSession],
  props: {
    filter: Object,
    index: Number
  },
  data: () => ({
    isEditMode: false,
    summary: undefined
  }),
  created() {
    let value = _.get(this.filter, 'value');
    let h = this.filter.subcategoryHeader;
    switch (this.filter.type) {
      case 'range':
        this.summary = h[0] + ' ' + value[0] + ' ' + h[1] + ' ' + value[1];
        break;
      case 'array':
        this.summary = value;
        break;
      default:
        this.summary = null;
        break;
    }
  },
  computed: {
    allowEdits() {
      let isOwnedByCurrentUser = _.get(this.cohort, 'isOwnedByCurrentUser');
      return _.isNil(isOwnedByCurrentUser) || isOwnedByCurrentUser;
    },
    disableButtons() {
      return !_.includes(['readyForApply', 'readyForSave'], this.pageMode);
    }
  },
  methods: {
    cancel() {
      this.isEditMode = false;
      this.readyForSave();
    },
    edit() {
      this.isEditMode = true;
      this.setPageMode('edit');
    },
    update() {
      this.isEditMode = false;
      this.readyForSave();
    }
  }
};
</script>
