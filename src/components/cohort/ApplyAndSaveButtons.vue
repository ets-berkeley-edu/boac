<template>
  <div>
      <div class="sr-only" aria-live="polite">{{ screenReaderAlert }}</div>
      <b-btn id="unsaved-filter-apply"
             class="btn-filter-draft-apply btn-primary-color-override"
             variant="primary"
             aria-label="Search for students"
             @click="apply()"
             :disabled="!!editMode"
             v-if="showApplyButton">
        Apply
      </b-btn>
      <div v-if="showSaveButton && isPerforming !== 'search'">
        <b-btn id="save-button"
               class="save-button-width mt-3"
               :class="{
                 'btn-primary-color-override': this.isPerforming !== 'acknowledgeSave'
               }"
               :variant="saveButtonVariant"
               :aria-label="`cohortId ? 'Save cohort' : 'Create cohort'`"
               :disabled="!!editMode || showCreateModal || !!isPerforming"
               @click="save()">
          <span v-if="isPerforming === 'acknowledgeSave'">Saved</span>
          <span v-if="isPerforming === 'save'"><i class="fas fa-spinner fa-spin"></i> Saving</span>
          <span v-if="!isPerforming && cohortId">Save Cohort</span>
          <span v-if="!isPerforming && !cohortId">Save</span>
        </b-btn>
        <b-modal id="create-cohort"
                 @shown="focusModalById('create-input')"
                 body-class="pl-0 pr-0"
                 v-model="showCreateModal"
                 hide-footer
                 hide-header-close
                 title="Name Your Saved Cohort">
          <CreateCohortModal :cancel="cancelCreateModal"
                             :create="create"/>
        </b-modal>
      </div>
    </div>
</template>

<script>
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import CohortEditSession from '@/mixins/CohortEditSession';
import CreateCohortModal from '@/components/cohort/CreateCohortModal';
import Util from '@/mixins/Util';

export default {
  name: 'ApplyAndSaveButtons',
  mixins: [CohortEditSession, GoogleAnalytics, Util],
  components: { CreateCohortModal },
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
      this.screenReaderAlert = `Searching for students`;
      this.isPerforming = 'search';
      this.setCurrentPage(1);
      this.applyFilters().then(() => {
        this.putFocusNextTick('save-button');
        this.gaCohortEvent(
          this.cohortId,
          this.cohortName || 'unsaved',
          'search'
        );
        this.screenReaderAlert = `Search results loaded`;
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
        this.gaCohortEvent(this.cohortId, name, 'create');
        history.pushState({}, null, `/cohort/${this.cohortId}`);
        this.isPerforming = null;
      });
    },
    save() {
      if (this.cohortId) {
        this.screenReaderAlert = `Saving changes to cohort ${this.cohortName}`;
        this.isPerforming = 'save';
        this.saveExistingCohort().then(() => {
          this.gaCohortEvent(this.cohortId, this.cohortName, 'save');
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
.btn-filter-draft-apply {
  height: 40px;
  margin: 15px 8px 0 0;
  width: 80px;
}
.save-button-width {
  min-width: 120px;
  width: 120px;
}
</style>
