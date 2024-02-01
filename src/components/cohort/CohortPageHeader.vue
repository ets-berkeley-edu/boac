<template>
  <div>
    <div v-if="!cohortId && totalStudentCount === undefined" class="pb-3">
      <h1 id="create-cohort-h1" class="page-section-header">
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
        <h1 v-if="cohortName" id="cohort-name" class="page-section-header pb-0">
          {{ cohortName }}
          <span
            v-if="editMode !== 'apply' && totalStudentCount !== undefined"
            class="faint-text"
          >{{ pluralize(domain === 'admitted_students' ? 'admit' : 'student', totalStudentCount) }}</span>
        </h1>
        <h1 v-if="!cohortName && totalStudentCount !== undefined" id="cohort-results-header">
          {{ pluralize('Result', totalStudentCount) }}
        </h1>
      </div>
      <div v-if="!showHistory" class="d-flex align-self-baseline mr-3">
        <div v-if="cohortId && _size(filters)">
          <b-btn
            id="show-hide-details-button"
            class="no-wrap pr-1 p-0"
            variant="link"
            @click="toggleShowHideDetails"
          >
            {{ isCompactView ? 'Show' : 'Hide' }} Filters
          </b-btn>
        </div>
        <div v-if="cohortId && isOwnedByCurrentUser && _size(filters)" class="faint-text">|</div>
        <div v-if="cohortId && isOwnedByCurrentUser">
          <b-btn
            id="rename-button"
            class="pt-0 px-1"
            variant="link"
            @click="beginRename"
          >
            Rename
          </b-btn>
        </div>
        <div v-if="cohortId && isOwnedByCurrentUser" class="faint-text">|</div>
        <div v-if="cohortId && isOwnedByCurrentUser">
          <b-btn
            id="delete-button"
            v-b-modal="'confirm-delete-modal'"
            class="pt-0 px-1"
            variant="link"
          >
            Delete
          </b-btn>
          <b-modal
            id="confirm-delete-modal"
            v-model="showDeleteModal"
            body-class="pl-0 pr-0"
            hide-footer
            hide-header
            @shown="putFocusNextTick('modal-header')"
          >
            <DeleteCohortModal
              :cohort-name="cohortName"
              :cancel-delete-modal="cancelDeleteModal"
              :delete-cohort="cohortDelete"
            />
          </b-modal>
        </div>
        <div v-if="(cohortId && isOwnedByCurrentUser) || (cohortId && _size(filters))" class="faint-text">|</div>
        <div v-if="cohortId || totalStudentCount !== undefined">
          <b-btn
            v-if="domain === 'default'"
            id="export-student-list-button"
            v-b-modal="'export-students-modal'"
            :disabled="!exportEnabled || !totalStudentCount || isModifiedSinceLastSearch"
            class="no-wrap pt-0 px-1"
            variant="link"
          >
            Export List
          </b-btn>
          <b-btn
            v-if="domain === 'admitted_students'"
            id="export-student-list-button"
            v-b-modal="'export-admits-modal'"
            :disabled="!exportEnabled || !totalStudentCount || isModifiedSinceLastSearch"
            class="no-wrap pt-0 px-1"
            variant="link"
          >
            Export List
          </b-btn>
          <b-modal
            id="export-admits-modal"
            v-model="showExportAdmitsModal"
            body-class="pl-0 pr-0"
            hide-footer
            hide-header
            @shown="putFocusNextTick('modal-header')"
          >
            <FerpaReminderModal
              :cancel="cancelExportModal"
              :confirm="() => exportStudents(getCsvExportColumnsSelected(domain))"
            />
          </b-modal>
          <b-modal
            id="export-students-modal"
            v-model="showExportStudentsModal"
            body-class="pl-0 pr-0"
            hide-footer
            hide-header
            @shown="putFocusNextTick('modal-header')"
          >
            <ExportListModal
              :cancel="cancelExportModal"
              :csv-columns-selected="getCsvExportColumnsSelected(domain)"
              :csv-columns="getCsvExportColumns(domain)"
              :export="exportStudents"
            />
          </b-modal>
        </div>
        <div v-if="isHistorySupported" class="faint-text">|</div>
        <div v-if="isHistorySupported">
          <b-btn
            id="show-cohort-history-button"
            :disabled="isModifiedSinceLastSearch"
            class="no-wrap pl-1 pr-0 pt-0"
            variant="link"
            @click="toggleShowHistory(true)"
          >
            History
          </b-btn>
        </div>
      </div>
      <div v-if="showHistory" class="d-flex align-self-baseline mr-4">
        <b-btn
          id="show-cohort-history-button"
          class="no-wrap pl-2 pr-0 pt-0"
          variant="link"
          @click="toggleShowHistory(false)"
        >
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
              @keyup.esc="cancelRename"
            />
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
          aria-live="polite"
        >
          Cohort name cannot exceed 255 characters.
        </div>
      </div>
      <div class="d-flex align-self-baseline mr-2">
        <b-btn
          id="rename-confirm"
          :disabled="!name"
          class="btn-primary-color-override rename-btn"
          variant="primary"
          size="sm"
          @click.prevent="submitRename"
        >
          Rename
        </b-btn>
        <b-btn
          id="rename-cancel"
          class="rename-btn"
          variant="link"
          size="sm"
          @click="cancelRename"
        >
          Cancel
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession'
import Context from '@/mixins/Context'
import DeleteCohortModal from '@/components/cohort/DeleteCohortModal'
import ExportListModal from '@/components/util/ExportListModal'
import FerpaReminderModal from '@/components/util/FerpaReminderModal'
import router from '@/router'
import Util from '@/mixins/Util'
import Validator from '@/mixins/Validator'
import {deleteCohort, downloadCohortCsv, downloadCsv, saveCohort} from '@/api/cohort'
import {getCsvExportColumns, getCsvExportColumnsSelected} from '@/berkeley'

export default {
  name: 'CohortPageHeader',
  components: {DeleteCohortModal, ExportListModal, FerpaReminderModal},
  mixins: [CohortEditSession, Context, Util, Validator],
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
    showExportAdmitsModal: false,
    showExportStudentsModal: false
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
      this.$announcer.polite(`Renaming cohort '${this.name}'`)
      this.putFocusNextTick('rename-cohort-input')
    },
    cancelDeleteModal() {
      this.showDeleteModal = false
      this.$announcer.polite(`Cancel deletion of cohort '${this.name}'`)
    },
    cancelExportModal() {
      this.showExportAdmitsModal = this.showExportStudentsModal = false
      this.$announcer.polite(`Cancel export of cohort '${this.name}'`)
    },
    cancelRename() {
      this.name = this.cohortName
      this.setEditMode(null)
      this.$announcer.polite(`Cancel renaming of cohort '${this.name}'`)
    },
    cohortDelete() {
      this.$announcer.polite(`Deleting cohort '${this.name}'`)
      deleteCohort(this.cohortId).then(() => {
        this.showDeleteModal = false
        router.push({path: '/'})
      })
    },
    downloadCsvPerFilters(csvColumnsSelected) {
      return new Promise(resolve => {
        const isReadOnly = this.cohortId && !this.isOwnedByCurrentUser
        if (isReadOnly) {
          downloadCohortCsv(this.cohortId, this.cohortName, csvColumnsSelected).then(resolve)
        } else {
          downloadCsv(this.domain, this.cohortName, this.filters, csvColumnsSelected).then(resolve)
        }
      })
    },
    exportStudents(csvColumnsSelected) {
      this.showExportAdmitsModal = this.showExportStudentsModal = this.exportEnabled = false
      this.$announcer.polite(`Exporting cohort '${this.name}'`)
      this.downloadCsvPerFilters(csvColumnsSelected).then(() => {
        this.exportEnabled = true
        this.$announcer.polite('Export is done.')
      })
    },
    getCsvExportColumns,
    getCsvExportColumnsSelected,
    submitRename() {
      this.renameError = this.validateCohortName({
        id: this.cohortId,
        name: this.name
      })
      if (this.renameError) {
        this.putFocusNextTick('rename-cohort-input')
      } else {
        this.renameCohort(name)
        saveCohort(this.cohortId, this.cohortName, this.filters).then(() => {
          this.$announcer.polite(`Cohort renamed to '${this.name}'`)
          this.setPageTitle(this.name)
          this.putFocusNextTick('cohort-name')
        })
        this.setEditMode(null)
      }
    },
    toggleShowHideDetails() {
      this.toggleCompactView()
      this.$announcer.polite(this.isCompactView ? 'Filters are hidden' : 'Filters are visible')
    }
  }
}
</script>

<style scoped>
.rename-btn {
  height: 38px;
}
.rename-input {
  box-sizing: border-box;
  border: 2px solid #ccc;
  border-radius: 4px;
}
</style>
