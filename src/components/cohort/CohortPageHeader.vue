<template>
  <div class="d-flex justify-content-between">
    <div v-if="!cohortId && totalStudentCount === undefined">
      <h1 class="page-section-header mt-0"
          tabindex="0">Create a Filtered Cohort</h1>
      <div>
        Find a set of users, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
    </div>
    <div v-if="!renameMode">
      <h1 id="cohort-name"
          class="page-section-header mt-0"
          tabindex="0"
          v-if="cohortName">
        {{ cohortName }}
        <span class="faint-text"
              v-if="editMode !== 'apply' && totalStudentCount !== undefined">{{ 'student' | pluralize(totalStudentCount) }}</span>
      </h1>
      <h1 tabindex="0"
          v-if="!cohortName && totalStudentCount !== undefined">
        {{ 'Result' | pluralize(totalStudentCount) }}
      </h1>
    </div>
    <div class="w-100 mr-3" v-if="renameMode">
      <div class="">
        <form class="pt-0" name="renameCohortForm" @submit.prevent="submitRename()">
          <input id="rename-cohort-input"
                 name="name"
                 class="rename-input"
                 aria-label="Input cohort name, 255 characters or fewer"
                 aria-required="true"
                 :aria-invalid="!!name"
                 v-model="name"
                 v-focus
                 maxlength="255"
                 required
                 type="text"/>
        </form>
      </div>
      <div class="has-error pl-2" v-if="renameError">{{ renameError }}</div>
      <div class="faint-text pl-2" v-if="!renameError">255 character limit <span v-if="name.length">({{255 - name.length}} left)</span></div>
      <div class="sr-only" aria-live="polite">{{ renameError }}</div>
      <div class="sr-only"
           aria-live="polite"
           v-if="name.length === 255">Cohort name cannot exceed 255 characters.</div>
    </div>
    <div class="d-flex align-self-baseline m-1 mr-4" v-if="renameMode">
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
             variant="link"
             size="sm"
             @click="cancelRename()">
        Cancel
      </b-btn>
    </div>
    <div class="d-flex align-self-baseline m-1 mr-4" v-if="!renameMode">
      <div>
        <b-btn id="show-hide-details-button"
               class="no-wrap pr-2 pt-0"
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
                 body-class="pl-0 pr-0"
                 hide-footer
                 hide-header>
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
.rename-input {
  box-sizing: border-box;
  border: 2px solid #ccc;
  border-radius: 4px;
  color: #333;
  padding: 10px;
  width: 100%;
}
</style>
