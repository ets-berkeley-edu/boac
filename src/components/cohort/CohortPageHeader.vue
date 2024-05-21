<template>
  <div>
    <div v-if="!cohort.cohortId && cohort.totalStudentCount === undefined">
      <h1 id="create-cohort-h1" class="page-section-header">
        Create {{ cohort.domain === 'default' ? 'a Cohort' : 'an admissions cohort' }}
      </h1>
      <div v-if="cohort.domain === 'default'">
        Find a set of students, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
      <div v-if="cohort.domain === 'admitted_students'">
        Find a set of admitted students using the filters below.
      </div>
    </div>
    <div v-if="!renameMode" class="d-flex flex-wrap justify-space-between">
      <h1
        v-if="cohort.cohortName"
        id="cohort-name"
        class="page-section-header align-self-center mb-0 mr-2"
      >
        {{ cohort.cohortName }}
        <span
          v-if="cohort.editMode !== 'apply' && cohort.totalStudentCount !== undefined"
          class="text-grey ml-1"
        >{{ pluralize(cohort.domain === 'admitted_students' ? 'admit' : 'student', cohort.totalStudentCount) }}</span>
      </h1>
      <h1
        v-if="!cohort.cohortName && cohort.totalStudentCount !== undefined"
        id="cohort-results-header"
        class="page-section-header align-self-center mb-0 mr-2"
      >
        {{ pluralize('Result', cohort.totalStudentCount) }}
      </h1>
      <div v-if="!showHistory" class="d-flex align-center align-self-center pr-3">
        <v-btn
          v-if="cohort.cohortId && size(cohort.filters)"
          id="show-hide-details-button"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          :text="`${cohort.isCompactView ? 'Show' : 'Hide'} Filters`"
          variant="text"
          @click="toggleShowHideDetails"
        />
        <div
          v-if="cohort.cohortId && cohort.isOwnedByCurrentUser && size(cohort.filters)"
          class="text-grey"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="cohort.cohortId && cohort.isOwnedByCurrentUser"
          id="rename-button"
          class="font-size-15 px-1"
          color="anchor"
          text="Rename"
          variant="text"
          @click="beginRename"
        />
        <div
          v-if="cohort.cohortId && cohort.isOwnedByCurrentUser"
          class="text-grey"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="cohort.cohortId && cohort.isOwnedByCurrentUser"
          id="delete-button"
          class="font-size-15 px-1"
          color="anchor"
          text="Delete"
          variant="text"
          @click="showDeleteModal = true"
        />
        <div
          v-if="(cohort.cohortId && cohort.isOwnedByCurrentUser) || (cohort.cohortId && size(cohort.filters))"
          class="text-grey"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="cohort.domain === 'default' && (cohort.cohortId || cohort.totalStudentCount !== undefined)"
          id="export-student-list-button"
          :disabled="isDownloadingCSV || !cohort.totalStudentCount || cohort.isModifiedSinceLastSearch"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          text="Export List"
          variant="text"
          @click="showExportStudentsModal = true"
        />
        <v-btn
          v-if="cohort.domain === 'admitted_students' && (cohort.cohortId || cohort.totalStudentCount !== undefined)"
          id="export-student-list-button"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          :disabled="isDownloadingCSV || !cohort.totalStudentCount || cohort.isModifiedSinceLastSearch"
          text="Export List"
          variant="text"
          @click="showExportAdmitsModal = true"
        />
        <div
          v-if="isHistorySupported"
          class="text-grey"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="isHistorySupported"
          id="show-cohort-history-button"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          :disabled="cohort.isModifiedSinceLastSearch"
          text="History"
          variant="text"
          @click="toggleShowHistory(true)"
        />
      </div>
      <div v-if="showHistory" class="d-flex align-self-baseline mr-4">
        <v-btn
          id="show-cohort-history-button"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          text="Back to Cohort"
          variant="text"
          @click="toggleShowHistory(false)"
        />
      </div>
    </div>
    <RenameCohort
      :cancel="cancelRename"
      class="mb-1 pt-1"
      :is-open="renameMode"
    />
    <DeleteCohortModal
      id="confirm-delete-modal"
      :cancel-delete-modal="cancelDeleteModal"
      :delete-cohort="cohortDelete"
      :error="error"
      :show-modal="showDeleteModal"
    />
    <ExportListModal
      id="export-students-modal"
      :cancel="cancelExportModal"
      :csv-columns-selected="getCsvExportColumnsSelected(cohort.domain)"
      :csv-columns="getCsvExportColumns(cohort.domain)"
      :error="error"
      :export="exportStudents"
      :show-modal="showExportStudentsModal"
    />
    <FerpaReminderModal
      id="export-admits-modal"
      :cancel="cancelExportModal"
      :confirm="() => exportStudents(getCsvExportColumnsSelected(cohort.domain))"
      :show-modal="showExportAdmitsModal"
    />
  </div>
</template>

<script setup>
import DeleteCohortModal from '@/components/cohort/DeleteCohortModal'
import ExportListModal from '@/components/util/ExportListModal'
import FerpaReminderModal from '@/components/util/FerpaReminderModal'
import RenameCohort from '@/components/cohort/RenameCohort'
import {size} from 'lodash'
import {getCsvExportColumns, getCsvExportColumnsSelected} from '@/berkeley'
import {pluralize} from '@/lib/utils'
</script>

<script>
import router from '@/router'
import {deleteCohort, downloadCohortCsv, downloadCsv} from '@/api/cohort'
import {get} from 'lodash'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'

export default {
  name: 'CohortPageHeader',
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
    error: undefined,
    isDownloadingCSV: false,
    isHistorySupported: true,
    name: undefined,
    renameError: undefined,
    showDeleteModal: false,
    showExportAdmitsModal: false,
    showExportStudentsModal: false
  }),
  computed: {
    cohort() {
      return useCohortStore()
    },
    renameMode() {
      return useCohortStore().editMode === 'rename'
    }
  },
  watch: {
    name() {
      this.renameError = undefined
    },
    showDeleteModal() {
      this.error = undefined
    },
    showExportAdmitsModal() {
      this.error = undefined
    },
    showExportStudentsModal() {
      this.error = undefined
    }
  },
  created() {
    this.isHistorySupported = this.cohort.cohortId && this.cohort.domain === 'default'
    this.name = this.cohort.cohortName
  },
  methods: {
    beginRename() {
      this.name = this.cohort.cohortName
      this.cohort.setEditMode('rename')
      alertScreenReader(`Renaming cohort '${this.name}'`)
      putFocusNextTick('rename-cohort-input')
    },
    cancelDeleteModal() {
      this.showDeleteModal = false
      alertScreenReader(`Cancel deletion of cohort '${this.name}'`)
    },
    cancelExportModal() {
      this.showExportAdmitsModal = this.showExportStudentsModal = false
      alertScreenReader(`Cancel export of cohort '${this.name}'`)
    },
    cancelRename() {
      this.name = this.cohort.cohortName
      this.cohort.setEditMode(null)
      alertScreenReader(`Cancel renaming of cohort '${this.name}'`)
    },
    cohortDelete() {
      alertScreenReader(`Deleting cohort '${this.name}'`)
      return deleteCohort(this.cohort.cohortId).then(() => {
        this.showDeleteModal = false
        alertScreenReader(`Deleted cohort '${this.name}'`)
        router.push({path: '/'})
      }, error => {
        alertScreenReader(`Failed to delete cohort '${this.name}'`)
        this.handleError(error)
      })
    },
    downloadCsvPerFilters(csvColumnsSelected) {
      return new Promise((resolve, reject) => {
        const isReadOnly = this.cohort.cohortId && !this.cohort.isOwnedByCurrentUser
        if (isReadOnly) {
          downloadCohortCsv(this.cohort.cohortId, this.cohort.cohortName, csvColumnsSelected).then(resolve, reject)
        } else {
          downloadCsv(this.cohort.domain, this.cohort.cohortName, this.cohort.filters, csvColumnsSelected).then(resolve, reject)
        }
      })
    },
    exportStudents(csvColumnsSelected) {
      this.isDownloadingCSV = true
      alertScreenReader(`Exporting cohort '${this.name}'`)
      return this.downloadCsvPerFilters(csvColumnsSelected).then(() => {
        this.showExportAdmitsModal = this.showExportStudentsModal = this.isDownloadingCSV = false
        alertScreenReader(`Downloading cohort '${this.name}'`)
      }, error => {
        alertScreenReader(`Failed to export cohort '${this.name}'`)
        this.handleError(error)
      })
    },
    handleError(error) {
      this.error = get(error, 'message', 'An unknown error occurred.')
    },
    toggleShowHideDetails() {
      this.cohort.toggleCompactView()
      alertScreenReader(this.cohort.isCompactView ? 'Filters are hidden' : 'Filters are visible')
    }
  }
}
</script>
