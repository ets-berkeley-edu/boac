<template>
  <div class="cohort-header-container">
    <div v-if="!cohortId && totalStudentCount === undefined">
      <h1 class="page-section-header mt-0" focus-on="!isLoading" tabindex="0">Create a Filtered Cohort</h1>
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
      <div v-if="renameMode">
        <div>
          <form class="pt-0" name="renameCohortForm" @submit.prevent="submitRename()">
            <input aria-required="true"
                   aria-label="Input cohort name, 255 characters or fewer"
                   :aria-invalid="!!name"
                   class="form-control"
                   v-model="name"
                   id="rename-cohort-input"
                   maxlength="255"
                   name="name"
                   required
                   type="text"/>
          </form>
        </div>
        <div class="has-error pl-2" v-if="renameError">{{ renameError }}</div>
        <div class="faint-text pl-2" v-if="!renameError">255 character limit <span v-if="name.length">({{255 - name.length}} left)</span></div>
      </div>
    </div>
    <div class="d-flex justify-content-end ml-2" v-if="renameMode">
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
    <div class="d-flex justify-content-end align-middle mt-0" v-if="!renameMode">
      <div>
        <b-btn id="show-hide-details-button"
               class="pr-2 pt-0"
               variant="link"
               @click="toggleCompactView()"
               v-if="cohortId">
          {{isCompactView ? 'Show' : 'Hide'}} Filters
        </b-btn>
      </div>
      <div class="faint-text" v-if="cohortId && isOwnedByCurrentUser">|</div>
      <div v-if="cohortId && isOwnedByCurrentUser">
        <b-btn id="rename-cohort-button"
               class="pl-2 pr-2 pt-0"
               aria-label="Rename this cohort"
               variant="link"
               @click="beginRename()">
          Rename
        </b-btn>
      </div>
      <div class="faint-text">|</div>
      <div v-if="cohortId && isOwnedByCurrentUser">
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
      </div>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession';
import DeleteCohortModal from '@/components/cohort/DeleteCohortModal';
import router from '@/router';
import Validator from '@/mixins/Validator';
import { deleteCohort } from '@/api/cohort';

export default {
  name: 'CohortPageHeader',
  components: { DeleteCohortModal },
  mixins: [CohortEditSession, Validator],
  data: () => ({
    name: undefined,
    renameError: undefined,
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
      this.renameError = this.validateCohortName({
        id: this.cohortId,
        name: this.name
      });
      if (!this.renameError) {
        this.renameCohort(this.name);
        this.setEditMode(null);
      }
    }
  },
  watch: {
    name() {
      this.renameError = undefined;
    }
  }
};
</script>

<style scoped>
.disabled-link {
  color: #ccc;
}
</style>
