<template>
  <div>
    <div v-if="!useCohortStore().cohortId && useCohortStore().totalStudentCount === undefined" class="pb-3">
      <h1 id="create-cohort-h1" class="page-section-header">
        Create {{ useCohortStore().domain === 'default' ? 'a Cohort' : 'an admissions cohort' }}
      </h1>
      <div v-if="useCohortStore().domain === 'default'">
        Find a set of students, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
      <div v-if="useCohortStore().domain === 'admitted_students'">
        Find a set of admitted students using the filters below.
      </div>
    </div>
    <div v-if="!renameMode" class="d-flex flex-wrap justify-content-between">
      <div>
        <h1 v-if="useCohortStore().cohortName" id="cohort-name" class="page-section-header pb-0">
          {{ useCohortStore().cohortName }}
          <span
            v-if="useCohortStore().editMode !== 'apply' && useCohortStore().totalStudentCount !== undefined"
            class="faint-text"
          >{{ pluralize(useCohortStore().domain === 'admitted_students' ? 'admit' : 'student', useCohortStore().totalStudentCount) }}</span>
        </h1>
        <h1 v-if="!useCohortStore().cohortName && useCohortStore().totalStudentCount !== undefined" id="cohort-results-header">
          {{ pluralize('Result', useCohortStore().totalStudentCount) }}
        </h1>
      </div>
      <div v-if="!showHistory" class="d-flex align-self-baseline mr-3">
        <div v-if="useCohortStore().cohortId && size(useCohortStore().filters)">
          <v-btn
            id="show-hide-details-button"
            class="text-no-wrap pr-1 p-0"
            variant="text"
            @click="toggleShowHideDetails"
          >
            {{ useCohortStore().isCompactView ? 'Show' : 'Hide' }} Filters
          </v-btn>
        </div>
        <div v-if="useCohortStore().cohortId && useCohortStore().isOwnedByCurrentUser && size(useCohortStore().filters)" class="faint-text">|</div>
        <div v-if="useCohortStore().cohortId && useCohortStore().isOwnedByCurrentUser">
          <v-btn
            id="rename-button"
            class="pt-0 px-1"
            variant="text"
            @click="beginRename"
          >
            Rename
          </v-btn>
        </div>
        <div v-if="useCohortStore().cohortId && useCohortStore().isOwnedByCurrentUser" class="faint-text">|</div>
        <div v-if="useCohortStore().cohortId && useCohortStore().isOwnedByCurrentUser">
          <v-btn
            id="delete-button"
            class="pt-0 px-1"
            variant="text"
            @click="showDeleteModal = true"
          >
            Delete
          </v-btn>
          <DeleteCohortModal
            id="confirm-delete-modal"
            :cohort-name="useCohortStore().cohortName"
            :cancel-delete-modal="cancelDeleteModal"
            :delete-cohort="cohortDelete"
            :error="error"
            :show-modal="showDeleteModal"
          />
        </div>
        <div v-if="(useCohortStore().cohortId && useCohortStore().isOwnedByCurrentUser) || (useCohortStore().cohortId && size(useCohortStore().filters))" class="faint-text">|</div>
        <div v-if="useCohortStore().cohortId || useCohortStore().totalStudentCount !== undefined">
          <v-btn
            v-if="useCohortStore().domain === 'default'"
            id="export-student-list-button"
            :disabled="!exportEnabled || !useCohortStore().totalStudentCount || useCohortStore().isModifiedSinceLastSearch"
            class="text-no-wrap pt-0 px-1"
            variant="text"
            @click="showExportStudentsModal = true"
          >
            Export List
          </v-btn>
          <ExportListModal
            id="export-students-modal"
            :cancel="cancelExportModal"
            :csv-columns-selected="getCsvExportColumnsSelected(useCohortStore().domain)"
            :csv-columns="getCsvExportColumns(useCohortStore().domain)"
            :error="error"
            :export="exportStudents"
            :show-modal="showExportStudentsModal"
          />
          <v-btn
            v-if="useCohortStore().domain === 'admitted_students'"
            id="export-student-list-button"
            class="text-no-wrap pt-0 px-1"
            :disabled="!exportEnabled || !useCohortStore().totalStudentCount || useCohortStore().isModifiedSinceLastSearch"
            variant="text"
            @click="showExportAdmitsModal = true"
          >
            Export List
          </v-btn>
          <FerpaReminderModal
            id="export-admits-modal"
            :cancel="cancelExportModal"
            :confirm="() => exportStudents(getCsvExportColumnsSelected(useCohortStore().domain))"
            :show-modal="showExportAdmitsModal"
          />
        </div>
        <div v-if="isHistorySupported" class="faint-text">|</div>
        <div v-if="isHistorySupported">
          <v-btn
            id="show-cohort-history-button"
            :disabled="useCohortStore().isModifiedSinceLastSearch"
            class="pl-1 pr-0 pt-0"
            variant="text"
            @click="toggleShowHistory(true)"
          >
            History
          </v-btn>
        </div>
      </div>
      <div v-if="showHistory" class="d-flex align-self-baseline mr-4">
        <v-btn
          id="show-cohort-history-button"
          class="text-no-wrap pl-2 pr-0 pt-0"
          variant="text"
          @click="toggleShowHistory(false)"
        >
          Back to Cohort
        </v-btn>
      </div>
    </div>
    <RenameCohort
      :cancel="cancelRename"
      :error="renameError"
      :submit="submitRename"
    ></RenameCohort>
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
import {deleteCohort, downloadCohortCsv, downloadCsv, saveCohort} from '@/api/cohort'
import {validateCohortName} from '@/lib/cohort'

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
    this.isHistorySupported = useCohortStore().cohortId && useCohortStore().domain === 'default'
    this.name = useCohortStore().cohortName
  },
  methods: {
    beginRename() {
      this.name = useCohortStore().cohortName
      useCohortStore().setEditMode('rename')
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
      this.name = useCohortStore().cohortName
      useCohortStore().setEditMode(null)
      useContextStore().alertScreenReader(`Cancel renaming of cohort '${this.name}'`)
    },
    cohortDelete() {
      useContextStore().alertScreenReader(`Deleting cohort '${this.name}'`)
      return deleteCohort(useCohortStore().cohortId).then(() => {
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
        const isReadOnly = useCohortStore().cohortId && !useCohortStore().isOwnedByCurrentUser
        if (isReadOnly) {
          downloadCohortCsv(useCohortStore().cohortId, useCohortStore().cohortName, csvColumnsSelected).then(resolve, reject)
        } else {
          downloadCsv(useCohortStore().domain, useCohortStore().cohortName, useCohortStore().filters, csvColumnsSelected).then(resolve, reject)
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
    submitRename() {
      this.renameError = validateCohortName({
        id: useCohortStore().cohortId,
        name: this.name
      })
      if (this.renameError) {
        putFocusNextTick('rename-cohort-input')
      } else {
        this.renameCohort(this.name)
        saveCohort(useCohortStore().cohortId, useCohortStore().cohortName, useCohortStore().filters).then(() => {
          useContextStore().alertScreenReader(`Cohort renamed to '${this.name}'`)
          this.setPageTitle(this.name)
          putFocusNextTick('cohort-name')
        })
        useCohortStore().setEditMode(null)
      }
    },
    toggleShowHideDetails() {
      useCohortStore().toggleCompactView()
      useContextStore().alertScreenReader(useCohortStore().isCompactView ? 'Filters are hidden' : 'Filters are visible')
    }
  }
}
</script>
