<template>
  <div class="d-flex justify-content-between">
    <div class="sr-only" aria-live="polite">{{ screenReaderAlert }}</div>
    <div v-if="!cohortId && totalStudentCount === undefined">
      <h1
        id="create-cohort-h1"
        class="page-section-header mt-0"
        tabindex="0">
        Create a Cohort
      </h1>
      <div>
        Find a set of users, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
    </div>
    <div v-if="!renameMode">
      <h1
        v-if="cohortName"
        id="cohort-name"
        class="page-section-header mt-0"
        tabindex="0">
        {{ cohortName }}
        <span
          v-if="editMode !== 'apply' && totalStudentCount !== undefined"
          class="faint-text">{{ 'student' | pluralize(totalStudentCount) }}</span>
      </h1>
      <h1
        v-if="!cohortName && totalStudentCount !== undefined"
        tabindex="0">
        {{ 'Result' | pluralize(totalStudentCount) }}
      </h1>
    </div>
    <div v-if="renameMode" class="w-100 mr-3">
      <div class="">
        <form class="pt-0" @submit.prevent="submitRename()">
          <input
            id="rename-cohort-input"
            v-model="name"
            class="rename-input"
            :aria-invalid="!name"
            aria-label="Input cohort name, 255 characters or fewer"
            aria-required="true"
            maxlength="255"
            required
            type="text"
            @keyup.esc="cancelRename()" />
        </form>
      </div>
      <div v-if="renameError" class="has-error pl-2">{{ renameError }}</div>
      <div v-if="!renameError" class="faint-text pl-2">255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></div>
      <div class="sr-only" aria-live="polite">{{ renameError }}</div>
      <div
        v-if="name.length === 255"
        class="sr-only"
        aria-live="polite">
        Cohort name cannot exceed 255 characters.
      </div>
    </div>
    <div v-if="renameMode" class="d-flex align-self-baseline m-1 mr-4">
      <b-btn
        id="rename-confirm"
        class="cohort-manage-btn btn-primary-color-override"
        variant="primary"
        aria-label="Save changes to cohort name"
        size="sm"
        :disabled="!name"
        @click.prevent="submitRename()">
        <span :class="{'disabled-link': !name}">Rename</span>
      </b-btn>
      <b-btn
        id="rename-cancel"
        class="cohort-manage-btn"
        variant="link"
        aria-label="Cancel rename cohort"
        size="sm"
        @click="cancelRename()">
        Cancel
      </b-btn>
    </div>
    <div v-if="!renameMode" class="d-flex align-self-baseline m-1 mr-4">
      <div>
        <b-btn
          v-if="cohortId && size(filters)"
          id="show-hide-details-button"
          class="no-wrap pr-2 pt-0"
          variant="link"
          :aria-label="isCompactView ? 'Show cohort filters' : 'Hide cohort filters'"
          @click="toggleShowHideDetails()">
          {{ isCompactView ? 'Show' : 'Hide' }} Filters
        </b-btn>
      </div>
      <div v-if="cohortId && isOwnedByCurrentUser && size(filters)" class="faint-text">|</div>
      <div v-if="cohortId && isOwnedByCurrentUser">
        <b-btn
          id="rename-button"
          class="pl-2 pr-2 pt-0"
          variant="link"
          aria-label="Rename this cohort"
          @click="beginRename()">
          Rename
        </b-btn>
      </div>
      <div v-if="cohortId && isOwnedByCurrentUser" class="faint-text">|</div>
      <div v-if="cohortId && isOwnedByCurrentUser">
        <b-btn
          id="delete-button"
          v-b-modal="'confirm-delete-modal'"
          class="pl-2 pr-0 pt-0"
          variant="link"
          aria-label="Delete this cohort">
          Delete
        </b-btn>
        <b-modal
          id="confirm-delete-modal"
          v-model="showDeleteModal"
          body-class="pl-0 pr-0"
          hide-footer
          hide-header
          @shown="focusModalById('delete-confirm')">
          <DeleteCohortModal
            :cohort-name="cohortName"
            :cancel-delete-modal="cancelDeleteModal"
            :delete-cohort="cohortDelete" />
        </b-modal>
      </div>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession';
import DeleteCohortModal from '@/components/cohort/DeleteCohortModal';
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import router from '@/router';
import Util from '@/mixins/Util';
import Validator from '@/mixins/Validator';
import { deleteCohort } from '@/api/cohort';

export default {
  name: 'CohortPageHeader',
  components: { DeleteCohortModal },
  mixins: [CohortEditSession, GoogleAnalytics, Util, Validator],
  data: () => ({
    name: undefined,
    renameError: undefined,
    screenReaderAlert: undefined,
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
      this.screenReaderAlert = `Renaming ${this.name} cohort`;
      this.putFocusNextTick('rename-cohort-input');
    },
    cancelDeleteModal() {
      this.showDeleteModal = false;
      this.screenReaderAlert = `Cancel deletion of ${this.name} cohort`;
    },
    cancelRename() {
      this.name = this.cohortName;
      this.setEditMode(null);
      this.screenReaderAlert = `Cancel renaming of ${this.name} cohort`;
    },
    cohortDelete() {
      this.screenReaderAlert = `Deleting ${this.name} cohort`;
      deleteCohort(this.cohortId).then(() => {
        this.showDeleteModal = false;
        this.gaCohortEvent(this.cohortId, this.cohortName, 'delete');
        router.push({ path: '/' });
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
          this.screenReaderAlert = `Saved new cohort name: ${this.name}`;
          this.setPageTitle(this.name);
          this.putFocusNextTick('cohort-name');
          this.gaCohortEvent(this.cohortId, this.name, 'rename');
        });
        this.setEditMode(null);
      }
    },
    toggleShowHideDetails() {
      this.toggleCompactView();
      this.screenReaderAlert = this.isCompactView
        ? 'Filters are hidden'
        : 'Filters are visible';
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
