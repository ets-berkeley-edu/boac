<template>
  <div>
    <div class="cohort-added-filter-name">
      {{ filter.name }}
    </div>
    <div class="cohort-added-subcategory-name">
      <span v-if="filter.subcategoryHeader && !isEditMode">{{ filter.subcategoryHeader }}</span>
      <!--
      <filter-criteria-edit-subcategory filter="row"
                                        on-option-click="filter.onOptionClick"
                                        watch="row"
                                        v-if="isEditMode"></filter-criteria-edit-subcategory>
                                        -->
    </div>
    <div class="cohort-added-filter-controls">
      <div class="cohort-added-filter-buttons">
        <div v-if="allowEdits && !isEditMode">
          <b-btn variant="link"
                 :id="`edit-added-filter-${index}`"
                 aria-label="Edit filter"
                 class="btn-link btn-cohort-added-filter"
                 @click="isEditMode = true">
            Edit
          </b-btn> |
        </div>
        <div v-if="allowEdits && !isEditMode">
          <b-btn variant="link"
                 :id="`remove-added-filter-${index}`"
                 aria-label="Remove filter"
                 class="btn-link btn-cohort-added-filter"
                 @click="removeFilter(index)">
            Remove
          </b-btn>
        </div>
        <div v-if="allowEdits && isEditMode">
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
        <div v-if="allowEdits && isEditMode">
          <b-btn variant="link"
                 :id="`cancel-edit-added-filter-${index}`"
                 aria-label="Cancel"
                 class="btn-cohort-added-filter"
                 @click="isEditMode = false">
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
    allowEdits: undefined,
    isEditMode: false
  }),
  created() {
    this.allowEdits =
      _.isNil(this.isOwnedByCurrentUser) || this.isOwnedByCurrentUser;
  },
  methods: {
    update: _.noop
  }
};
</script>
