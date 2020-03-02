<template>
  <div>
    <div v-if="!cohortId && totalStudentCount === undefined" class="mb-2">
      <h1
        id="create-cohort-h1"
        class="page-section-header"
        tabindex="0">
        Create {{ domain === 'default' ? 'a Cohort' : 'an admissions cohort' }}
      </h1>
      <div v-if="domain === 'default'">
        Find a set of users, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
      <div v-if="domain === 'admitted_students'">
        Find a set of users using the filters below.
      </div>
    </div>
    <div v-if="!renameMode" class="d-flex flex-wrap justify-content-between">
      <div>
        <h1
          v-if="cohortName"
          id="cohort-name"
          class="page-section-header"
          tabindex="0">
          {{ cohortName }}
          <span
            v-if="editMode !== 'apply' && totalStudentCount !== undefined"
            class="faint-text">{{ 'student' | pluralize(totalStudentCount) }}</span>
        </h1>
        <h1
          v-if="!cohortName && totalStudentCount !== undefined"
          id="cohort-results-header"
          tabindex="0">
          {{ 'Result' | pluralize(totalStudentCount) }}
        </h1>
      </div>
      <div v-if="!showHistory" class="d-flex align-self-baseline mr-4">
        <div v-if="cohortId && size(filters)">
          <b-btn
            id="show-hide-details-button"
            :aria-label="isCompactView ? 'Show cohort filters' : 'Hide cohort filters'"
            class="no-wrap pr-2 p-0"
            variant="link"
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
            class="pl-2 pr-2 pt-0"
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
        <div v-if="(cohortId && isOwnedByCurrentUser) || (cohortId && size(filters))" class="faint-text">|</div>
        <div v-if="cohortId || totalStudentCount !== undefined">
          <b-btn
            v-if="domain === 'default'"
            id="export-student-list-button"
            v-b-modal="'export-list-modal'"
            :disabled="!exportEnabled || !totalStudentCount || isModifiedSinceLastSearch"
            class="no-wrap pl-2 pr-2 pt-0"
            variant="link"
            aria-label="Download CSV file containing all students">
            Export List
          </b-btn>
          <b-btn
            v-if="domain !== 'default'"
            id="export-student-list-button"
            :disabled="!exportEnabled || !totalStudentCount || isModifiedSinceLastSearch"
            class="no-wrap pl-2 pr-2 pt-0"
            variant="link"
            aria-label="Download CSV file containing all students"
            @click.prevent="exportCohort(getCsvExportColumnsSelected())">
            Export List
          </b-btn>
          <b-modal
            id="export-list-modal"
            v-model="showExportListModal"
            body-class="pl-0 pr-0"
            hide-footer
            hide-header
            @shown="focusModalById('export-list-confirm')">
            <ExportListModal
              :cancel-export-list-modal="cancelExportCohortModal"
              :csv-columns-selected="getCsvExportColumnsSelected()"
              :csv-columns="getCsvExportColumns()"
              :export-list="exportCohort" />
          </b-modal>
        </div>
        <div v-if="isHistorySupported" class="faint-text">|</div>
        <div v-if="isHistorySupported">
          <b-btn
            id="show-cohort-history-button"
            :disabled="isModifiedSinceLastSearch"
            class="no-wrap pl-2 pr-0 pt-0"
            variant="link"
            aria-label="Show cohort history"
            @click="toggleShowHistory(true)">
            History
          </b-btn>
        </div>
      </div>
      <div v-if="showHistory" class="d-flex align-self-baseline mr-4">
        <b-btn
          id="show-cohort-history-button"
          class="no-wrap pl-2 pr-0 pt-0"
          variant="link"
          aria-label="Hide cohort history"
          @click="toggleShowHistory(false)">
          Back to Cohort
        </b-btn>
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
              class="rename-input text-dark p-2 w-100"
              aria-label="Input cohort name, 255 characters or fewer"
              aria-required="true"
              maxlength="255"
              required
              type="text"
              @keyup.esc="cancelRename()" />
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
          class="cohort-manage-btn btn-primary-color-override"
          variant="primary"
          aria-label="Save changes to cohort name"
          size="sm"
          @click.prevent="submitRename()">
          Rename
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
    </div>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley';
import CohortEditSession from '@/mixins/CohortEditSession';
import Context from '@/mixins/Context';
import DeleteCohortModal from '@/components/cohort/DeleteCohortModal';
import ExportListModal from '@/components/util/ExportListModal';
import router from '@/router';
import Util from '@/mixins/Util';
import Validator from '@/mixins/Validator';
import { deleteCohort } from '@/api/cohort';

export default {
  name: 'CohortPageHeader',
  components: { DeleteCohortModal, ExportListModal },
  mixins: [Berkeley, CohortEditSession, Context, Util, Validator],
  props: {
    showHistory: {
      type: Boolean,
      required: true
    },
    toggleShowHistory: {
      type: Function,
      required: true
    }
  },
  data: () => ({
    exportEnabled: true,
    isHistorySupported: true,
    name: undefined,
    renameError: undefined,
    showDeleteModal: false,
    showExportListModal: false
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
    this.isHistorySupported = this.cohortId && this.domain === 'default';
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
    cancelExportCohortModal() {
      this.showExportListModal = false;
      this.alertScreenReader(`Cancel export of ${this.name} cohort`);
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
        this.$ga.cohortEvent(this.cohortId, this.cohortName, 'delete');
        router.push({ path: '/' });
      });
    },
    exportCohort(csvColumnsSelected) {
      this.showExportListModal = false;
      this.exportEnabled = false;
      this.alertScreenReader(`Exporting ${this.name} cohort`);
      this.downloadCsvPerFilters(csvColumnsSelected).then(() => {
        this.exportEnabled = true;
      });
    },
    getCsvExportColumns() {
      let columns;
      if (this.domain === 'default') {
        columns = this.getCohortCsvExportColumns();
      } else {
        columns = [
          {text: 'First name', value: 'first_name'},
          {text: 'Middle name', value: 'middle_name'},
          {text: 'Last name', value: 'last_name'},
          {text: 'CS ID', value: 'cs_empl_id'},
          {text: 'ApplyUC CPID', value: 'applyuc_cpid'},
          {text: 'UID', value: 'uid'},
          {text: 'Birthdate', value: 'birthdate'},
          {text: 'Freshman or Transfer', value: 'freshman_or_transfer'},
          {text: 'Admit Status', value: 'admit_status'},
          {text: 'SIR', value: 'current_sir'},
          {text: 'College', value: 'college'},
          {text: 'Admit Term', value: 'admit_term'},
          {text: 'Email', value: 'email'},
          {text: 'Campus Email', value: 'campus_email_1'},
          {text: 'Street 1', value: 'permanent_street_1'},
          {text: 'Street 2', value: 'permanent_street_2'},
          {text: 'City', value: 'permanent_city'},
          {text: 'Region', value: 'permanent_region'},
          {text: 'Postal Code', value: 'permanent_postal'},
          {text: 'Country', value: 'permanent_country'},
          {text: 'Sex', value: 'sex'},
          {text: 'Gender Identity', value: 'gender_identity'},
          {text: 'XEthnic', value: 'xethnic'},
          {text: 'Hispanic', value: 'hispanic'},
          {text: 'UREM', value: 'urem'},
          {text: 'Residency Category', value: 'residency_category'},
          {text: 'US Citizenship Status', value: 'us_citizenship_status'},
          {text: 'US Non Citizen Status', value: 'us_non_citizen_status'},
          {text: 'Citizenship Country', value: 'citizenship_country'},
          {text: 'Permanent Residence Country', value: 'permanent_residence_country'},
          {text: 'Non Immigrant Visa Current', value: 'non_immigrant_visa_current'},
          {text: 'Non Immigrant Visa Planned', value: 'non_immigrant_visa_planned'},
          {text: 'First Generation Student', value: 'first_generation_student'},
          {text: 'First Generation College', value: 'first_generation_college'},
          {text: 'Parent 1 Education', value: 'parent_1_education_level'},
          {text: 'Parent 2 Education', value: 'parent_2_education_level'},
          {text: 'Highest Parent Education', value: 'highest_parent_education_level'},
          {text: 'HS Unweighted GPA', value: 'hs_unweighted_gpa'},
          {text: 'HS Weighted GPA', value: 'hs_weighted_gpa'},
          {text: 'Transfer GPA', value: 'transfer_gpa'},
          {text: 'ACT Composite', value: 'act_composite'},
          {text: 'ACT Math', value: 'act_math'},
          {text: 'ACT English', value: 'act_english'},
          {text: 'ACT Reading', value: 'act_reading'},
          {text: 'ACT Writing', value: 'act_writing'},
          {text: 'SAT Total', value: 'sat_total'},
          {text: 'SAT Evidence-Based Reading and Writing', value: 'sat_r_evidence_based_rw_section'},
          {text: 'SAT Math', value: 'sat_r_math_section'},
          {text: 'SAT Essay Reading', value: 'sat_r_essay_reading'},
          {text: 'SAT Essay Analysis', value: 'sat_r_essay_analysis'},
          {text: 'SAT Essay Writing', value: 'sat_r_essay_writing'},
          {text: 'Waiver', value: 'application_fee_waiver_flag'},
          {text: 'Foster Care', value: 'foster_care_flag'},
          {text: 'Family Is Single Parent', value: 'family_is_single_parent'},
          {text: 'Student Is Single Parent', value: 'student_is_single_parent'},
          {text: 'Family Dependents', value: 'family_dependents_num'},
          {text: 'Student Dependents', value: 'student_dependents_num'},
          {text: 'Family Income', value: 'family_income'},
          {text: 'Student Income', value: 'student_income'},
          {text: 'Military Dependent', value: 'is_military_dependent'},
          {text: 'Military', value: 'military_status'},
          {text: 'Re-entry', value: 'reentry_status'},
          {text: 'Athlete', value: 'athlete_status'},
          {text: 'Summer Bridge', value: 'summer_bridge_status'},
          {text: 'Last School LCFF+', value: 'last_school_lcff_plus_flag'},
          {text: 'CEP', value: 'special_program_cep'}
        ]
      }
      return columns;
    },
    getCsvExportColumnsSelected() {
      return this.domain === 'default' ?
        ['first_name', 'last_name', 'sid', 'email', 'phone'] :
        this.map(this.getCsvExportColumns(), 'value');
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
          this.$ga.cohortEvent(this.cohortId, this.name, 'rename');
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
