<template>
  <div class="d-flex justify-content-between">
    <div class="sr-only" aria-live="polite">{{ cohortUpdateStatus }}</div>
    <div v-if="!cohortId && totalStudentCount === undefined">
      <h1 id="create-cohort-h1"
          class="page-section-header mt-0"
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
        <form class="pt-0" @submit.prevent="submitRename()">
          <input id="rename-cohort-input"
                 name="name"
                 class="rename-input"
                 aria-label="Input cohort name, 255 characters or fewer"
                 aria-required="true"
                 :aria-invalid="!!name"
                 v-model="name"
                 @keyup.esc="cancelRename()"
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
      <b-btn id="rename-confirm"
             class="cohort-manage-btn btn-primary-color-override"
             variant="primary"
             aria-label="Save changes to cohort name"
             size="sm"
             @click.prevent="submitRename()"
             :disabled="!name">
        <span :class="{'disabled-link': !name}">Rename</span>
      </b-btn>
      <b-btn id="rename-cancel"
             class="cohort-manage-btn"
             variant="link"
             aria-label="Cancel rename cohort"
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
               :aria-label="`isCompactView ? 'Show cohort filters' : 'Hide cohort filters'`"
               @click="toggleShowHideDetails()"
               v-if="cohortId">
          {{isCompactView ? 'Show' : 'Hide'}} Filters
        </b-btn>
      </div>
      <div class="faint-text" v-if="cohortId && isOwnedByCurrentUser">|</div>
      <div v-if="cohortId && isOwnedByCurrentUser">
        <b-btn id="rename-button"
               class="pl-2 pr-2 pt-0"
               variant="link"
               aria-label="Rename this cohort"
               @click="beginRename()">
          Rename
        </b-btn>
      </div>
      <div v-if="cohortId && isOwnedByCurrentUser" class="faint-text">|</div>
      <div v-if="cohortId && isOwnedByCurrentUser">
        <b-btn id="delete-button"
               class="pl-2 pr-0 pt-0"
               variant="link"
               v-b-modal="'confirm-delete-modal'"
               aria-label="Delete this cohort">
          Delete
        </b-btn>
        <b-modal id="confirm-delete-modal"
                 @shown="focusModalById('delete-confirm')"
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
import Util from '@/mixins/Util';
import Validator from '@/mixins/Validator';
import { deleteCohort } from '@/api/cohort';

export default {
  name: 'CohortPageHeader',
  components: { DeleteCohortModal },
  mixins: [CohortEditSession, Util, Validator],
  data: () => ({
    cohortUpdateStatus: undefined,
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
      this.cohortUpdateStatus = `Renaming ${this.name} cohort`;
    },
    cancelDeleteModal() {
      this.showDeleteModal = false;
      this.cohortUpdateStatus = `Cancel deletion of ${this.name} cohort`;
    },
    cancelRename() {
      this.name = this.cohortName;
      this.setEditMode(null);
      this.cohortUpdateStatus = `Cancel renaming of ${this.name} cohort`;
    },
    cohortDelete() {
      this.cohortUpdateStatus = `Deleting ${this.name} cohort`;
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
        this.renameCohort(this.name).then(() => {
          this.cohortUpdateStatus = `Saved new cohort name: ${this.name}`;
          this.putFocusNextTick('cohort-name');
        });
        this.setEditMode(null);
      }
    },
    toggleShowHideDetails() {
      this.toggleCompactView();
      this.cohortUpdateStatus = this.isCompactView
        ? 'Filters are hidden'
        : 'Filter are visible';
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
