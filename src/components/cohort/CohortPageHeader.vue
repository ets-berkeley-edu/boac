<template>
  <div>
    <div v-if="!cohortId && totalStudentCount === undefined" class="mb-2">
      <h1
        id="create-cohort-h1"
        class="page-section-header"
        tabindex="0">
        Create a Cohort
      </h1>
      <div>
        Find a set of users, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
    </div>
    <div v-if="!renameMode" class="d-flex flex-wrap justify-content-between">
      <div>
        <h1
          id="cohort-name"
          v-if="cohortName"
          class="page-section-header"
          tabindex="0">
          {{ cohortName }}
          <span
            v-if="editMode !== 'apply' && totalStudentCount !== undefined"
            class="faint-text">{{ 'student' | pluralize(totalStudentCount) }}</span>
        </h1>
        <h1
          id="cohort-results-header"
          v-if="!cohortName && totalStudentCount !== undefined"
          tabindex="0">
          {{ 'Result' | pluralize(totalStudentCount) }}
        </h1>
      </div>
      <div class="d-flex align-self-baseline mr-4">
        <div v-if="cohortId && size(filters)">
          <b-btn
            id="show-hide-details-button"
            :aria-label="isCompactView ? 'Show cohort filters' : 'Hide cohort filters'"
            @click="toggleShowHideDetails()"
            class="no-wrap pr-2 p-0"
            variant="link">
            {{ isCompactView ? 'Show' : 'Hide' }} Filters
          </b-btn>
        </div>
        <div v-if="cohortId && isOwnedByCurrentUser && size(filters)" class="faint-text">|</div>
        <div v-if="cohortId && isOwnedByCurrentUser">
          <b-btn
            id="rename-button"
            @click="beginRename()"
            class="pl-2 pr-2 pt-0"
            variant="link"
            aria-label="Rename this cohort">
            Rename
          </b-btn>
        </div>
        <div v-if="cohortId && isOwnedByCurrentUser" class="faint-text">|</div>
        <div v-if="cohortId && isOwnedByCurrentUser">
          <b-btn
            id="delete-button"
            v-b-modal="'confirm-delete-modal'"
            class="pl-2 pr-2 pt-0"
            variant="link"
            aria-label="Delete this cohort">
            Delete
          </b-btn>
          <b-modal
            id="confirm-delete-modal"
            v-model="showDeleteModal"
            @shown="focusModalById('delete-confirm')"
            body-class="pl-0 pr-0"
            hide-footer
            hide-header>
            <DeleteCohortModal
              :cohort-name="cohortName"
              :cancel-delete-modal="cancelDeleteModal"
              :delete-cohort="cohortDelete" />
          </b-modal>
        </div>
        <div v-if="(cohortId && isOwnedByCurrentUser) || (cohortId && size(filters))" class="faint-text">|</div>
        <div v-if="cohortId || totalStudentCount !== undefined">
          <b-btn
            id="export-student-list-button"
            :disabled="!exportEnabled || !totalStudentCount || isModifiedSinceLastSearch"
            @click.prevent="exportCohort()"
            class="no-wrap pl-2 pr-0 pt-0"
            variant="link"
            aria-label="Download CSV file containing all students">
            Export List
          </b-btn>
        </div>
      </div>
    </div>
    <div v-if="renameMode" class="d-flex flex-wrap justify-content-between">
      <div class="flex-grow-1 mr-4">
        <div>
          <form @submit.prevent="submitRename()">
            <input
              id="rename-cohort-input"
              v-model="name"
              :aria-invalid="!name"
              @keyup.esc="cancelRename()"
              class="rename-input text-dark p-2 w-100"
              aria-label="Input cohort name, 255 characters or fewer"
              aria-required="true"
              maxlength="255"
              required
              type="text" />
          </form>
        </div>
        <div class="pt-1">
          <span v-if="renameError" class="has-error">{{ renameError }}</span>
          <span v-if="!renameError" class="faint-text">255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></span>
        </div>
        <div class="sr-only" aria-live="polite">{{ renameError }}</div>
        <div
          v-if="name.length === 255"
          class="sr-only"
          aria-live="polite">
          Cohort name cannot exceed 255 characters.
        </div>
      </div>
      <div class="d-flex align-self-baseline">
        <b-btn
          id="rename-confirm"
          :disabled="!name"
          @click.prevent="submitRename()"
          class="cohort-manage-btn btn-primary-color-override"
          variant="primary"
          aria-label="Save changes to cohort name"
          size="sm">
          Rename
        </b-btn>
        <b-btn
          id="rename-cancel"
          @click="cancelRename()"
          class="cohort-manage-btn"
          variant="link"
          aria-label="Cancel rename cohort"
          size="sm">
          Cancel
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession';
import Context from '@/mixins/Context';
import DeleteCohortModal from '@/components/cohort/DeleteCohortModal';
import router from '@/router';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import Validator from '@/mixins/Validator';
import { deleteCohort } from '@/api/cohort';

export default {
  name: 'CohortPageHeader',
  components: { DeleteCohortModal },
  mixins: [CohortEditSession, Context, UserMetadata, Util, Validator],
  data: () => ({
    exportEnabled: true,
    name: undefined,
    renameError: undefined,
    showDeleteModal: false
  }),
  computed: {
    renameMode() {
      return this.editMode === 'rename';
    }
  },
  watch: {
    name() {
      this.renameError = undefined;
    }
  },
  created() {
    this.name = this.cohortName;
  },
  methods: {
    beginRename() {
      this.name = this.cohortName;
      this.setEditMode('rename');
      this.alertScreenReader(`Renaming ${this.name} cohort`);
      this.putFocusNextTick('rename-cohort-input');
    },
    cancelDeleteModal() {
      this.showDeleteModal = false;
      this.alertScreenReader(`Cancel deletion of ${this.name} cohort`);
    },
    cancelRename() {
      this.name = this.cohortName;
      this.setEditMode(null);
      this.alertScreenReader(`Cancel renaming of ${this.name} cohort`);
    },
    cohortDelete() {
      this.alertScreenReader(`Deleting ${this.name} cohort`);
      deleteCohort(this.cohortId).then(() => {
        this.showDeleteModal = false;
        this.gaCohortEvent({
          id: this.cohortId,
          name: this.cohortName,
          action: 'delete'
        });
        router.push({ path: '/' });
      });
    },
    exportCohort() {
      this.exportEnabled = false;
      this.downloadCsvPerFilters().then(() => {
        this.exportEnabled = true;
      });
    },
    submitRename() {
      this.renameError = this.validateCohortName({
        id: this.cohortId,
        name: this.name
      });
      if (this.renameError) {
        this.putFocusNextTick('rename-cohort-input');
      } else {
        this.renameCohort(this.name).then(() => {
          this.alertScreenReader(`Saved new cohort name: ${this.name}`);
          this.setPageTitle(this.name);
          this.putFocusNextTick('cohort-name');
          this.gaCohortEvent({
            id: this.cohortId,
            name: this.name,
            action: 'rename'
          });
        });
        this.setEditMode(null);
      }
    },
    toggleShowHideDetails() {
      this.toggleCompactView();
      this.alertScreenReader(this.isCompactView ? 'Filters are hidden' : 'Filters are visible');
    }
  }
};
</script>

<style scoped>
.rename-input {
  box-sizing: border-box;
  border: 2px solid #ccc;
  border-radius: 4px;
}
</style>
