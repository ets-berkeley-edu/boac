<template>
  <div>
    <div class="sr-only" aria-live="polite">{{ screenReaderAlert }}</div>
    <b-btn
      id="unsaved-filter-apply"
      v-if="showApplyButton"
      :disabled="!!editMode"
      @click="apply()"
      class="btn-filter-draft btn-primary-color-override"
      variant="primary"
      aria-label="Search for students">
      Apply
    </b-btn>
    <b-btn
      id="unsaved-filter-reset"
      v-if="showApplyButton"
      :disabled="!!editMode"
      @click="resetToLastApply()"
      class="btn-filter-draft"
      aria-label="Reset filters">
      Reset
    </b-btn>
    <div v-if="showSaveButton && isPerforming !== 'search'">
      <b-btn
        id="save-button"
        :class="{
          'btn-primary-color-override': isPerforming !== 'acknowledgeSave'
        }"
        :variant="saveButtonVariant"
        :aria-label="cohortId ? 'Save cohort' : 'Create cohort'"
        :disabled="!!editMode || showCreateModal || !!isPerforming"
        @click="save()"
        class="btn-filter-draft save-button-width mt-3">
        <span v-if="isPerforming === 'acknowledgeSave'">Saved</span>
        <span v-if="isPerforming === 'save'"><font-awesome icon="spinner" spin /> Saving</span>
        <span v-if="!isPerforming && cohortId">Save Cohort</span>
        <span v-if="!isPerforming && !cohortId">Save</span>
      </b-btn>
      <b-btn
        id="unsaved-filter-reset"
        v-if="!isPerforming && cohortId"
        :disabled="!!editMode"
        @click="resetToSaved()"
        class="btn-filter-draft"
        aria-label="Reset filters">
        Reset
      </b-btn>
      <b-modal
        id="create-cohort"
        v-model="showCreateModal"
        @shown="focusModalById('create-input')"
        title="Name Your Saved Cohort"
        body-class="pl-0 pr-0"
        hide-footer
        hide-header-close>
        <CreateCohortModal
          :cancel="cancelCreateModal"
          :create="create" />
      </b-modal>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession';
import Context from '@/mixins/Context';
import CreateCohortModal from '@/components/cohort/CreateCohortModal';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'ApplyAndSaveButtons',
  components: { CreateCohortModal },
  mixins: [CohortEditSession, Context, UserMetadata, Util],
  data: () => ({
    isPerforming: undefined,
    showCreateModal: false
  }),
  computed: {
    saveButtonVariant() {
      return this.isPerforming === 'acknowledgeSave' ? 'success' : 'primary';
    }
  },
  methods: {
    apply() {
      this.$eventHub.$emit('cohort-apply-filters');
      this.isPerforming = 'search';
      this.applyFilters(this.preferences.sortBy).then(() => {
        this.putFocusNextTick('cohort-results-header');
        this.gaCohortEvent({
          id: this.cohortId,
          name: this.cohortName || '',
          action: 'search'
        });
        this.isPerforming = null;
      });
    },
    cancelCreateModal() {
      this.alertScreenReader(`Canceled`);
      this.showCreateModal = false;
    },
    create(name) {
      this.showCreateModal = false;
      this.isPerforming = 'save';
      this.createCohort(name).then(() => {
        this.savedCohortCallback(`Cohort "${name}" created`);
        this.setPageTitle(this.cohortName);
        this.gaCohortEvent({
          id: this.cohortId,
          name, action: 'create'
        });
        history.pushState({}, null, `/cohort/${this.cohortId}`);
        this.isPerforming = null;
      });
    },
    resetToLastApply() {
      this.alertScreenReader('Resetting filters');
      this.resetFiltersToLastApply();
    },
    resetToSaved() {
      this.isPerforming = 'search';
      this.resetFiltersToSaved(this.cohortId).then(() => {
        this.alertScreenReader('Filters reset');
        this.isPerforming = null;
      });
    },
    save() {
      if (this.cohortId) {
        this.alertScreenReader(`Saving changes to cohort ${this.cohortName}`);
        this.isPerforming = 'save';
        this.saveExistingCohort().then(() => {
          this.gaCohortEvent({
            id: this.cohortId,
            name: this.cohortName,
            action: 'save'
          });
          this.savedCohortCallback(`Cohort "${this.cohortName}" saved`);
        });
      } else {
        this.showCreateModal = true;
        this.alertScreenReader('Create cohort form is open');
      }
    },
    savedCohortCallback(updateStatus) {
      this.alertScreenReader(updateStatus);
      this.isPerforming = 'acknowledgeSave';
      setTimeout(() => (this.isPerforming = null), 2000);
    }
  }
};
</script>

<style scoped>
.btn-filter-draft {
  height: 40px;
  margin: 15px 8px 0 0;
  width: 80px;
}
.save-button-width {
  min-width: 120px;
  width: 120px;
}
</style>
