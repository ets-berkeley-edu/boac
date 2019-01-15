<template>
  <div>
      <b-btn id="unsaved-filter-apply"
             class="btn-filter-draft-apply"
             aria-label="Search for students"
             variant="primary"
             @click="applyFilters()"
             :disabled="!!editMode"
             v-if="showApplyButton">
        Apply
      </b-btn>
      <div v-if="showSaveButton">
        <b-btn id="save-cohort"
               class="save-button-width mt-3"
               :variant="saveButtonVariant"
               :disabled="editMode || acknowledgeSave"
               @click="save()">
          <span v-if="acknowledgeSave">Saved</span>
          <span v-if="!acknowledgeSave && cohortId">Save Cohort</span>
          <span v-if="!acknowledgeSave && !cohortId">Save</span>
        </b-btn>
        <b-modal id="createCohortModal"
                 @shown="focusModalById('cohort-create-input')"
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
    acknowledgeSave: null,
    showCreateModal: false
  }),
  computed: {
    saveButtonVariant() {
      return this.acknowledgeSave ? 'success' : 'primary';
    }
  },
  methods: {
    cancelCreateModal() {
      this.showCreateModal = false;
    },
    create(name) {
      this.showCreateModal = false;
      this.createCohort(name);
    },
    save() {
      if (this.cohortId) {
        this.acknowledgeSave = true;
        this.saveExistingCohort().then(() => {
          this.acknowledgeSave = false;
        });
      } else {
        this.showCreateModal = true;
      }
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
