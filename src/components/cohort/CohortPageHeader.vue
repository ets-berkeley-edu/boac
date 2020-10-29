<template>
  <div>
    <div v-if="!cohortId && totalStudentCount === undefined" class="pb-3">
      <h1
        id="create-cohort-h1"
        class="page-section-header"
        tabindex="0">
        Create {{ domain === 'default' ? 'a Cohort' : 'an admissions cohort' }}
      </h1>
      <div v-if="domain === 'default'">
        Find a set of students, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
      <div v-if="domain === 'admitted_students'">
        Find a set of admitted students using the filters below.
      </div>
    </div>
    <div v-if="!renameMode" class="d-flex flex-wrap justify-content-between">
      <div>
        <h1
          v-if="cohortName"
          id="cohort-name"
          class="page-section-header pb-0"
          tabindex="0">
          {{ cohortName }}
          <span
            v-if="editMode !== 'apply' && totalStudentCount !== undefined"
            class="faint-text">{{ pluralize('student', totalStudentCount) }}</span>
        </h1>
        <h1
          v-if="!cohortName && totalStudentCount !== undefined"
          id="cohort-results-header"
          tabindex="0">
          {{ pluralize('Result', totalStudentCount) }}
        </h1>
      </div>
      <div v-if="!showHistory" class="d-flex align-self-baseline mr-3">
        <div v-if="cohortId && $_.size(filters)">
          <b-btn
            id="show-hide-details-button"
            :aria-label="isCompactView ? 'Show cohort filters' : 'Hide cohort filters'"
            class="no-wrap pr-2 p-0"
            variant="link"
            @click="toggleShowHideDetails">
            {{ isCompactView ? 'Show' : 'Hide' }} Filters
          </b-btn>
        </div>
        <div v-if="cohortId && isOwnedByCurrentUser && $_.size(filters)" class="faint-text">|</div>
        <div v-if="cohortId && isOwnedByCurrentUser">
          <b-btn
            id="rename-button"
            class="pl-2 pr-2 pt-0"
            variant="link"
            aria-label="Rename this cohort"
            @click="beginRename">
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
        <div v-if="(cohortId && isOwnedByCurrentUser) || (cohortId && $_.size(filters))" class="faint-text">|</div>
        <div v-if="cohortId || totalStudentCount !== undefined">
          <span id="export-student-list-description" class="sr-only">Download CSV file containing all students in this cohort</span>
          <b-btn
            v-if="domain === 'default'"
            id="export-student-list-button"
            v-b-modal="'export-list-modal'"
            :disabled="!exportEnabled || !totalStudentCount || isModifiedSinceLastSearch"
            class="no-wrap pl-2 pr-2 pt-0"
            variant="link"
            aria-describedby="export-student-list-description">
            Export List
          </b-btn>
          <b-btn
            v-if="domain === 'admitted_students'"
            id="export-student-list-button"
            :disabled="!exportEnabled || !totalStudentCount || isModifiedSinceLastSearch"
            class="no-wrap pl-2 pr-2 pt-0"
            variant="link"
            aria-describedby="export-student-list-description"
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
          <form @submit.prevent="submitRename">
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
              @keyup.esc="cancelRename" />
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
          @click.prevent="submitRename">
          Rename
        </b-btn>
        <b-btn
          id="rename-cancel"
          class="cohort-manage-btn"
          variant="link"
          aria-label="Cancel rename cohort"
          size="sm"
          @click="cancelRename">
          Cancel
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley'
import CohortEditSession from '@/mixins/CohortEditSession'
import Context from '@/mixins/Context'
import DeleteCohortModal from '@/components/cohort/DeleteCohortModal'
import ExportListModal from '@/components/util/ExportListModal'
import router from '@/router'
import Util from '@/mixins/Util'
import Validator from '@/mixins/Validator'
import { deleteCohort } from '@/api/cohort'

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
      return this.editMode === 'rename'
    }
  },
  watch: {
    name() {
      this.renameError = undefined
    }
  },
  created() {
    this.isHistorySupported = this.cohortId && this.domain === 'default'
    this.name = this.cohortName
  },
  methods: {
    beginRename() {
      this.name = this.cohortName
      this.setEditMode('rename')
      this.alertScreenReader(`Renaming ${this.name} cohort`)
      this.putFocusNextTick('rename-cohort-input')
    },
    cancelDeleteModal() {
      this.showDeleteModal = false
      this.alertScreenReader(`Cancel deletion of ${this.name} cohort`)
    },
    cancelExportCohortModal() {
      this.showExportListModal = false
      this.alertScreenReader(`Cancel export of ${this.name} cohort`)
    },
    cancelRename() {
      this.name = this.cohortName
      this.setEditMode(null)
      this.alertScreenReader(`Cancel renaming of ${this.name} cohort`)
    },
    cohortDelete() {
      this.alertScreenReader(`Deleting ${this.name} cohort`)
      deleteCohort(this.cohortId).then(() => {
        this.showDeleteModal = false
        this.$ga.cohortEvent(this.cohortId, this.cohortName, 'delete')
        router.push({ path: '/' })
      })
    },
    exportCohort(csvColumnsSelected) {
      this.showExportListModal = false
      this.exportEnabled = false
      this.alertScreenReader(`Exporting ${this.name} cohort`)
      this.downloadCsvPerFilters(csvColumnsSelected).then(() => {
        this.exportEnabled = true
      })
    },
    getCsvExportColumns() {
      if (this.domain === 'default') {
        return this.getDefaultCsvExportColumns()
      }
      return this.getAdmitCsvExportColumns()
    },
    getCsvExportColumnsSelected() {
      return this.domain === 'default' ?
        ['first_name', 'last_name', 'sid', 'email', 'phone'] :
        this.$_.map(this.getCsvExportColumns(), 'value')
    },
    submitRename() {
      this.renameError = this.validateCohortName({
        id: this.cohortId,
        name: this.name
      })
      if (this.renameError) {
        this.putFocusNextTick('rename-cohort-input')
      } else {
        this.renameCohort(this.name).then(() => {
          this.alertScreenReader(`Saved new cohort name: ${this.name}`)
          this.setPageTitle(this.name)
          this.putFocusNextTick('cohort-name')
          this.$ga.cohortEvent(this.cohortId, this.name, 'rename')
        })
        this.setEditMode(null)
      }
    },
    toggleShowHideDetails() {
      this.toggleCompactView()
      this.alertScreenReader(this.isCompactView ? 'Filters are hidden' : 'Filters are visible')
    }
  }
}
</script>

<style scoped>
.rename-input {
  box-sizing: border-box;
  border: 2px solid #ccc;
  border-radius: 4px;
}
</style>
