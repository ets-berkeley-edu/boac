<template>
  <div class="cohort-header-container">
    <div v-if="!cohortId && totalStudentCount === undefined">
      <h1 class="page-section-header" focus-on="!isLoading" tabindex="0">Create a Filtered Cohort</h1>
      <div>
        Find a set of users, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
    </div>
    <div v-if="!renameMode">
      <h1 class="page-section-header mt-0" v-if="cohortName" focus-on="!isLoading" tabindex="0">
        {{ cohortName }}
        <span class="faint-text"
              v-if="editMode !== 'apply' && totalStudentCount !== undefined">{{ 'student' | pluralize(totalStudentCount) }}</span>
      </h1>
      <h1 v-if="!cohortName && totalStudentCount !== undefined" focus-on="!isLoading" tabindex="0">
        {{ 'Result' | pluralize(totalStudentCount) }}
      </h1>
    </div>
    <div>
      <div class="cohort-rename-container" v-if="renameMode">
        <div>
          <form name="renameCohortForm" @submit.prevent="submitRename()">
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
             class="cohort-manage-btn"
             aria-label="Save changes to cohort name"
             variant="primary"
             size="sm"
             @click.prevent="submitRename()"
             :disabled="!name">
        <span :class="{'disabled-link': !name}">Rename</span>
      </b-btn>
      <b-btn id="filtered-cohort-rename-cancel"
             class="cohort-manage-btn"
             aria-label="Cancel rename cohort"
             variant="secondary"
             size="sm"
             @click="cancelRename()">
        Cancel
      </b-btn>
    </div>
    <div class="cohort-header-button-links align-middle no-wrap mt-0" v-if="!renameMode">
      <b-btn id="show-hide-details-button"
             class="pr-2 pt-0"
             variant="link"
             @click="toggleCompactView()"
             v-if="cohortId">
        {{isCompactView ? 'Show' : 'Hide'}} Filters
      </b-btn>
      <span v-if="cohortId && isOwnedByCurrentUser">
        <span class="faint-text">|</span>
        <b-btn id="rename-cohort-button"
               class="pl-2 pr-2 pt-0"
               aria-label="Rename this cohort"
               variant="link"
               @click="beginRename()">
          Rename
        </b-btn>
        <span class="faint-text">|</span>
        <b-btn id="delete-cohort-button"
               class="pl-2 pr-0 pt-0"
               variant="link"
               v-b-modal="'confirmDeleteModal'"
               aria-label="Delete this cohort">
          Delete
        </b-btn>
        <b-modal id="confirmDeleteModal"
                 v-model="showDeleteModal"
                 hide-footer
                 hide-header-close
                 title="Delete Saved Cohort">
          <DeleteCohortModal :cohortName="cohortName"
                             :cancelDeleteModal="cancelDeleteModal"
                             :deleteCohort="cohortDelete"/>
        </b-modal>
      </span>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession';
import DeleteCohortModal from '@/components/cohort/DeleteCohortModal';
import router from '@/router';
import { deleteCohort } from '@/api/cohort';

export default {
  name: 'CohortPageHeader',
  components: { DeleteCohortModal },
  mixins: [CohortEditSession],
  data: () => ({
    error: undefined,
    name: undefined,
    showDeleteModal: false
  }),
  created() {
    this.name = this.cohortName;
  },
  computed: {
    renameMode() {
      return this.editMode === 'rename';
    }
  },
  methods: {
    beginRename() {
      this.name = this.cohortName;
      this.setEditMode('rename');
    },
    cancelDeleteModal() {
      this.showDeleteModal = false;
    },
    cancelRename() {
      this.name = this.cohortName;
      this.setEditMode(null);
    },
    cohortDelete() {
      deleteCohort(this.cohortId).then(() => {
        this.showDeleteModal = false;
        router.push({ path: '/' });
      });
    },
    submitRename() {
      this.renameCohort(this.name);
      this.setEditMode(null);
    }
  }
};
</script>

<style scoped>
.disabled-link {
  color: #ccc;
}
</style>
