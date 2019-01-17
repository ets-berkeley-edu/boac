<template>
  <div>
      <div class="sr-only" aria-live="polite">{{ cohortUpdateStatus }}</div>
      <b-btn id="unsaved-filter-apply"
             class="btn-filter-draft-apply"
             aria-label="Search for students"
             variant="primary"
             @click="apply()"
             :disabled="!!editMode"
             v-if="showApplyButton">
        Apply
      </b-btn>
      <div v-if="showSaveButton && isPerforming !== 'search'">
        <b-btn id="save-button"
               class="save-button-width mt-3"
               :aria-label="`cohortId ? 'Save cohort' : 'Create cohort'`"
               :variant="saveButtonVariant"
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
import CohortEditSession from '@/mixins/CohortEditSession';
import CreateCohortModal from '@/components/cohort/CreateCohortModal';
import Util from '@/mixins/Util';

export default {
  name: 'ApplyAndSaveButtons',
  mixins: [CohortEditSession, Util],
  components: { CreateCohortModal },
  data: () => ({
    cohortUpdateStatus: undefined,
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
      this.cohortUpdateStatus = `Searching for students`;
      this.isPerforming = 'search';
      this.applyFilters().then(() => {
        this.putFocusNextTick('save-button');
        this.cohortUpdateStatus = `Search results loaded`;
        this.isPerforming = null;
      });
    },
    cancelCreateModal() {
      this.cohortUpdateStatus = `Cancel creation of new cohort`;
      this.showCreateModal = false;
    },
    create(name) {
      this.cohortUpdateStatus = `Creating new cohort with name ${name}`;
      this.showCreateModal = false;
      this.isPerforming = 'save';
      this.createCohort(name).then(() => {
        this.savedCohortCallback(`Cohort ${name} created`);
        this.setPageTitle(this.cohortName);
        this.isPerforming = null;
      });
    },
    save() {
      if (this.cohortId) {
        this.cohortUpdateStatus = `Saving changes to cohort ${this.cohortName}`;
        this.isPerforming = 'save';
        this.saveExistingCohort().then(() => {
          this.savedCohortCallback(`Cohort ${this.cohortName} saved`);
        });
      } else {
        this.cohortUpdateStatus = `Opening popup to create new cohort`;
        this.showCreateModal = true;
      }
    },
    savedCohortCallback(updateStatus) {
      this.cohortUpdateStatus = updateStatus;
      this.isPerforming = 'acknowledgeSave';
      setTimeout(() => (this.isPerforming = null), 2000);
    }
  }
};
</script>

<style scoped>
.save-button-width {
  min-width: 120px;
  width: 120px;
}
</style>
