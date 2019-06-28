<template>
  <div>
    <div class="sr-only" aria-live="polite">{{ screenReaderAlert }}</div>
    <b-btn
      v-if="showApplyButton"
      id="unsaved-filter-apply"
      class="btn-filter-draft btn-primary-color-override"
      variant="primary"
      aria-label="Search for students"
      :disabled="!!editMode"
      @click="apply()">
      Apply
    </b-btn>
    <b-btn
      v-if="showApplyButton"
      id="unsaved-filter-reset"
      class="btn-filter-draft"
      aria-label="Reset filters"
      :disabled="!!editMode"
      @click="resetToLastApply()">
      Reset
    </b-btn>
    <div v-if="showSaveButton && isPerforming !== 'search'">
      <b-btn
        id="save-button"
        class="btn-filter-draft save-button-width mt-3"
        :class="{
          'btn-primary-color-override': isPerforming !== 'acknowledgeSave'
        }"
        :variant="saveButtonVariant"
        :aria-label="cohortId ? 'Save cohort' : 'Create cohort'"
        :disabled="!!editMode || showCreateModal || !!isPerforming"
        @click="save()">
        <span v-if="isPerforming === 'acknowledgeSave'">Saved</span>
        <span v-if="isPerforming === 'save'"><font-awesome icon="spinner" spin /> Saving</span>
        <span v-if="!isPerforming && cohortId">Save Cohort</span>
        <span v-if="!isPerforming && !cohortId">Save</span>
      </b-btn>
      <b-btn
        v-if="!isPerforming && cohortId"
        id="unsaved-filter-reset"
        class="btn-filter-draft"
        aria-label="Reset filters"
        :disabled="!!editMode"
        @click="resetToSaved()">
        Reset
      </b-btn>
      <b-modal
        id="create-cohort"
        v-model="showCreateModal"
        body-class="pl-0 pr-0"
        hide-footer
        hide-header-close
        title="Name Your Saved Cohort"
        @shown="focusModalById('create-input')">
        <CreateCohortModal
          :cancel="cancelCreateModal"
          :create="create" />
      </b-modal>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession';
import CreateCohortModal from '@/components/cohort/CreateCohortModal';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'ApplyAndSaveButtons',
  components: { CreateCohortModal },
  mixins: [CohortEditSession, UserMetadata, Util],
  data: () => ({
    isPerforming: undefined,
    screenReaderAlert: undefined,
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
      this.screenReaderAlert = `Searching for students`;
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
      this.screenReaderAlert = `Cancel creation of new cohort`;
      this.showCreateModal = false;
    },
    create(name) {
      this.screenReaderAlert = `Creating new cohort with name ${name}`;
      this.showCreateModal = false;
      this.isPerforming = 'save';
      this.createCohort(name).then(() => {
        this.savedCohortCallback(`Cohort ${name} created`);
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
      this.screenReaderAlert = 'Resetting filters';
      this.resetFiltersToLastApply();
    },
    resetToSaved() {
      this.screenReaderAlert = 'Resetting filters';
      this.isPerforming = 'search';
      this.resetFiltersToSaved(this.cohortId).then(() => {
        this.screenReaderAlert = 'Filters reset';
        this.isPerforming = null;
      });
    },
    save() {
      if (this.cohortId) {
        this.screenReaderAlert = `Saving changes to cohort ${this.cohortName}`;
        this.isPerforming = 'save';
        this.saveExistingCohort().then(() => {
          this.gaCohortEvent({
            id: this.cohortId,
            name: this.cohortName,
            action: 'save'
          });
          this.savedCohortCallback(`Cohort ${this.cohortName} saved`);
        });
      } else {
        this.screenReaderAlert = `Opening popup to create new cohort`;
        this.showCreateModal = true;
      }
    },
    savedCohortCallback(updateStatus) {
      this.screenReaderAlert = updateStatus;
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
