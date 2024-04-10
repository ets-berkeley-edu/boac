<template>
  <div>
    <div v-if="!cohort.cohortId && cohort.totalStudentCount === undefined" class="pb-3">
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
    <div v-if="!renameMode" class="d-flex flex-wrap justify-space-between pb-3">
      <h1
        v-if="cohort.cohortName"
        id="cohort-name"
        class="page-section-header align-self-center mb-0 mr-2"
      >
        {{ cohort.cohortName }}
        <span
          v-if="cohort.editMode !== 'apply' && cohort.totalStudentCount !== undefined"
          class="text-grey ml-2"
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
          class="font-size-15 text-no-wrap px-2"
          color="anchor"
          variant="text"
          @click="toggleShowHideDetails"
        >
          {{ cohort.isCompactView ? 'Show' : 'Hide' }} Filters
        </v-btn>
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
          class="font-size-15 px-2"
          color="anchor"
          variant="text"
          @click="beginRename"
        >
          Rename
        </v-btn>
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
          class="font-size-15 px-2"
          color="anchor"
          variant="text"
          @click="showDeleteModal = true"
        >
          Delete
        </v-btn>
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
          :disabled="!exportEnabled || !cohort.totalStudentCount || cohort.isModifiedSinceLastSearch"
          class="font-size-15 text-no-wrap px-2"
          color="anchor"
          variant="text"
          @click="showExportStudentsModal = true"
        >
          Export List
        </v-btn>
        <v-btn
          v-if="cohort.domain === 'admitted_students' && (cohort.cohortId || cohort.totalStudentCount !== undefined)"
          id="export-student-list-button"
          class="font-size-15 text-no-wrap px-2"
          color="anchor"
          :disabled="!exportEnabled || !cohort.totalStudentCount || cohort.isModifiedSinceLastSearch"
          variant="text"
          @click="showExportAdmitsModal = true"
        >
          Export List
        </v-btn>
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
          class="font-size-15 px-2"
          color="anchor"
          :disabled="cohort.isModifiedSinceLastSearch"
          variant="text"
          @click="toggleShowHistory(true)"
        >
          History
        </v-btn>
      </div>
      <div v-if="showHistory" class="d-flex align-self-baseline mr-4">
        <v-btn
          id="show-cohort-history-button"
          class="font-size-15 text-no-wrap px-2"
          color="anchor"
          variant="text"
          @click="toggleShowHistory(false)"
        >
          Back to Cohort
        </v-btn>
      </div>
    </div>
    <RenameCohort
      :cancel="cancelRename"
      :is-open="renameMode"
    ></RenameCohort>
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
import {get, size} from 'lodash'
import {getCsvExportColumns, getCsvExportColumnsSelected} from '@/berkeley'
import {pluralize} from '@/lib/utils'
import {putFocusNextTick} from '@/lib/utils'
import router from '@/router'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {useContextStore} from '@/stores/context'
</script>

<script>
import DeleteCohortModal from '@/components/cohort/DeleteCohortModal'
import ExportListModal from '@/components/util/ExportListModal'
import FerpaReminderModal from '@/components/util/FerpaReminderModal'
import RenameCohort from '@/components/cohort/RenameCohort'
import {deleteCohort, downloadCohortCsv, downloadCsv} from '@/api/cohort'

export default {
  name: 'CohortPageHeader',
  components: {
    DeleteCohortModal,
    ExportListModal,
    FerpaReminderModal,
    RenameCohort
  },
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
    exportEnabled: true,
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
      useContextStore().alertScreenReader(`Renaming cohort '${this.name}'`)
      putFocusNextTick('rename-cohort-input')
    },
    cancelDeleteModal() {
      this.showDeleteModal = false
      useContextStore().alertScreenReader(`Cancel deletion of cohort '${this.name}'`)
    },
    cancelExportModal() {
      this.showExportAdmitsModal = this.showExportStudentsModal = false
      useContextStore().alertScreenReader(`Cancel export of cohort '${this.name}'`)
    },
    cancelRename() {
      this.name = this.cohort.cohortName
      this.cohort.setEditMode(null)
      useContextStore().alertScreenReader(`Cancel renaming of cohort '${this.name}'`)
    },
    cohortDelete() {
      useContextStore().alertScreenReader(`Deleting cohort '${this.name}'`)
      return deleteCohort(this.cohort.cohortId).then(() => {
        this.showDeleteModal = false
        useContextStore().alertScreenReader(`Deleted cohort '${this.name}'`)
        router.push({path: '/'})
      }, error => {
        useContextStore().alertScreenReader(`Failed to delete cohort '${this.name}'`)
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
      useContextStore().alertScreenReader(`Exporting cohort '${this.name}'`)
      return this.downloadCsvPerFilters(csvColumnsSelected).then(() => {
        this.exportEnabled = true
        this.showExportAdmitsModal = this.showExportStudentsModal = this.exportEnabled = false
        useContextStore().alertScreenReader(`Downloading cohort '${this.name}'`)
      }, error => {
        useContextStore().alertScreenReader(`Failed to export cohort '${this.name}'`)
        this.handleError(error)
      })
    },
    handleError(error) {
      this.error = get(error, 'message', 'An unknown error occurred.')
    },
    toggleShowHideDetails() {
      this.cohort.toggleCompactView()
      useContextStore().alertScreenReader(this.cohort.isCompactView ? 'Filters are hidden' : 'Filters are visible')
    }
  }
}
</script>
