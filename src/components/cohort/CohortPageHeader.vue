<template>
  <div class="cohort-header-container">
    <div v-if="!id && totalStudentCount === null">
      <h1 class="page-section-header" focus-on="!isLoading" tabindex="0">Create a Filtered Cohort</h1>
      <div>
        Find a set of users, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
    </div>
    <div v-if="!renameMode.on">
      <h1 class="page-section-header" v-if="name" focus-on="!isLoading" tabindex="0">
        {{ name }}
        <span class="faint-text"
              v-if="totalStudentCount != null">{{ 'student' | pluralize(totalStudentCount) }}</span>
      </h1>
      <h1 v-if="!name && totalStudentCount !== null" focus-on="!isLoading" tabindex="0">
        {{ 'Result' | pluralize(totalStudentCount) }}
      </h1>
    </div>
    <div>
      <div class="cohort-rename-container" v-if="renameMode.on">
        <div>
          <form name="renameCohortForm" @submit.prevent="rename()">
            <input aria-required="true"
                   aria-label="Input cohort name, 255 characters or fewer"
                   :aria-invalid="!!renameMode.input"
                   class="form-control"
                   @change="renameMode.hideError = true"
                   v-model="renameMode.input"
                   id="rename-cohort-input"
                   maxlength="255"
                   name="name"
                   required
                   type="text"/>
          </form>
        </div>
        <div class="has-error"
             v-if="renameMode.error && !renameMode.hideError">{{ renameMode.error }}</div>
        <div class="faint-text">255 character limit <span v-if="renameMode.input.length">({{255 - renameMode.input.length}} left)</span></div>
      </div>
    </div>
    <div class="cohort-header-buttons no-wrap" v-if="renameMode.on">
      <button type="button"
              id="filtered-cohort-rename"
              !aria-disabled="!renameMode.input"
              aria-label="Save changes to cohort name"
              class="btn btn-sm btn-primary cohort-manage-btn"
              @click.prevent="rename()"
              :disabled="!renameMode.input">
        Rename
      </button>
      <button type="button"
              aria-label="Cancel rename cohort"
              id="filtered-cohort-rename-cancel"
              class="btn btn-sm btn-default cohort-manage-btn"
              @click="exitRenameMode()">
        Cancel
      </button>
    </div>
    <div class="cohort-header-button-links no-wrap" v-if="!renameMode.on">
      <span v-if="isSearching || id">
        <button type="button"
                id="show-hide-details-button"
                class="btn-link cohort-manage-btn-link"
                @click="makeFiltersVisible(!filtersVisible)">
          {{filtersVisible ? 'Hide' : 'Show'}} Filters
        </button>
      </span>
      <span v-if="id && isOwnedByCurrentUser">
        <span class="faint-text">|</span>
        <button type="button"
                id="rename-cohort-button"
                aria-label="Rename this cohort"
                class="btn-link cohort-manage-btn-link"
                @click="enterRenameMode(name)">
          Rename
        </button>
        <span>
          <!--
          <span class="faint-text">|</span>
          <button type="button"
                  data-ng-controller="DeleteCohortController"
                  id="delete-cohort-button"
                  aria-label="Delete this cohort"
                  class="btn-link cohort-manage-btn-link"
                  data-ng-click="openDeleteCohortModal(search.cohort, callbacks)">
            Delete
          </button>
          -->
          <span class="faint-text">|</span>
          <b-modal id="delete-cohort-modal"
                   v-model="showDeleteModal"
                   hide-footer
                   hide-header-close
                   title="Delete">
            <DeleteCohortModal />
          </b-modal>
        </span>
      </span>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import CohortEditSession from '@/mixins/CohortEditSession';
import DeleteCohortModal from '@/components/cohort/DeleteCohortModal';

export default {
  name: 'CohortPageHeader',
  components: { DeleteCohortModal },
  mixins: [CohortEditSession],
  data: () => ({
    filtersVisible: false,
    isSearching: false,
    showDeleteModal: undefined,
    renameMode: {
      on: false,
      error: undefined,
      hideError: false,
      input: undefined
    }
  }),
  methods: {
    enterRenameMode: _.noop,
    exitRenameMode: _.noop,
    rename: _.noop
  }
};
</script>
