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
        <b-btn id="save-filtered-cohort"
               :class="{'btn-filter-draft-saved': acknowledgeSave, 'btn-primary btn-filter-draft-save': !acknowledgeSave}"
               aria-label="Save cohort"
               variant="primary"
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
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession';
import CreateCohortModal from '@/components/cohort/CreateCohortModal';

export default {
  name: 'ApplyAndSaveButtons',
  mixins: [CohortEditSession],
  components: { CreateCohortModal },
  data: () => ({
    acknowledgeSave: null,
    showCreateModal: false
  }),
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
