<template>
  <div class="cohort-header-container">
    <div v-if="!cohortId && totalStudentCount === null">
      <h1 class="page-section-header" focus-on="!isLoading" tabindex="0">Create a Filtered Cohort</h1>
      <div>
        Find a set of users, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
    </div>
    <div v-if="!renameMode">
      <h1 class="page-section-header" v-if="cohortName" focus-on="!isLoading" tabindex="0">
        {{ cohortName }}
        <span class="faint-text"
              v-if="totalStudentCount != null">{{ 'student' | pluralize(totalStudentCount) }}</span>
      </h1>
      <h1 v-if="!cohortName && totalStudentCount !== null" focus-on="!isLoading" tabindex="0">
        {{ 'Result' | pluralize(totalStudentCount) }}
      </h1>
    </div>
    <div>
      <div class="cohort-rename-container" v-if="renameMode">
        <div>
          <form name="renameCohortForm" @submit.prevent="rename()">
            <input aria-required="true"
                   aria-label="Input cohort name, 255 characters or fewer"
                   :aria-invalid="!!name"
                   class="form-control"
                   @change="error = null"
                   v-model="name"
                   id="rename-cohort-input"
                   maxlength="255"
                   name="name"
                   required
                   type="text"/>
          </form>
        </div>
        <div class="has-error" v-if="error">{{ error }}</div>
        <div class="faint-text">255 character limit <span v-if="name.length">({{255 - name.length}} left)</span></div>
      </div>
    </div>
    <div class="cohort-header-buttons no-wrap" v-if="renameMode">
      <b-btn id="filtered-cohort-rename"
             size="sm"
             :aria-disabled="!name"
             aria-label="Save changes to cohort name"
             class="cohort-manage-btn"
             @click.prevent="rename()"
             :disabled="!name">
        <span :class="{'disabled-link': !name}">Rename</span>
      </b-btn>
      <b-btn variant="outline-success"
             size="sm"
             aria-label="Cancel rename cohort"
             id="filtered-cohort-rename-cancel"
             class="cohort-manage-btn"
             @click="readyForSave()">
        Cancel
      </b-btn>
    </div>
    <div class="cohort-header-button-links no-wrap" v-if="!renameMode">
      <span v-if="cohortId">
        <b-btn variant="link"
               type="button"
               id="show-hide-details-button"
               class="cohort-manage-btn-link"
               :disabled="disableButtons"
               :aria-disabled="disableButtons"
               @click="toggleCompactView()">
          <span :class="{'disabled-link': disableButtons}">{{isCompactView ? 'Show' : 'Hide'}} Filters</span>
        </b-btn>
      </span>
      <span>
        <span class="faint-text" :class="{'disabled-link': disableButtons}">|</span>
        <b-btn variant="link"
               id="rename-cohort-button"
               aria-label="Rename this cohort"
               class="cohort-manage-btn-link"
               :disabled="disableButtons"
               :aria-disabled="disableButtons"
               @click="beginRename()">
          <span :class="{'disabled-link': disableButtons}">Rename</span>
        </b-btn>
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
          <span class="faint-text">|</span>
          <b-modal id="delete-cohort-modal"
                   v-model="showDeleteModal"
                   hide-footer
                   hide-header-close
                   title="Delete">
            <DeleteCohortModal />
          </b-modal>
          -->
        </span>
      </span>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession';
import DeleteCohortModal from '@/components/cohort/DeleteCohortModal';

export default {
  name: 'CohortPageHeader',
  components: { DeleteCohortModal },
  mixins: [CohortEditSession],
  data: () => ({
    error: undefined,
    name: undefined
  }),
  created() {
    this.name = this.cohortName;
  },
  computed: {
    renameMode() {
      return this.pageMode === 'rename';
    },
    disableButtons() {
      return !this.isOwnedByCurrentUser;
    }
  },
  methods: {
    beginRename() {
      this.name = this.cohortName;
      this.setPageMode('rename');
    },
    rename() {
      this.readyForSave();
    }
  }
};
</script>
