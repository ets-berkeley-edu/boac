<template>
  <div>
    <div v-if="!cohortStore.cohortId && cohortStore.totalStudentCount === undefined">
      <h1 id="create-cohort-h1" class="page-section-header">
        Create {{ cohortStore.domain === 'default' ? 'a Cohort' : 'an admissions cohort' }}
      </h1>
      <div v-if="cohortStore.domain === 'default'">
        Find a set of students, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
      <div v-if="cohortStore.domain === 'admitted_students'">
        Find a set of admitted students using the filters below.
      </div>
    </div>
    <div v-if="cohortStore.editMode !== 'rename'" class="d-flex flex-wrap justify-space-between">
      <h1
        v-if="cohortStore.cohortName"
        id="cohort-name"
        class="page-section-header align-self-center mb-0 mr-2"
      >
        {{ cohortStore.cohortName }}
        <span
          v-if="cohortStore.editMode !== 'apply' && cohortStore.totalStudentCount !== undefined"
          class="text-grey ml-1"
        >{{ pluralize(cohortStore.domain === 'admitted_students' ? 'admit' : 'student', cohortStore.totalStudentCount) }}</span>
      </h1>
      <h1
        v-if="!cohortStore.cohortName && cohortStore.totalStudentCount !== undefined"
        id="cohort-results-header"
        class="page-section-header align-self-center mb-0 mr-2"
      >
        {{ pluralize('Result', cohortStore.totalStudentCount) }}
      </h1>
      <div v-if="!showHistory" class="d-flex align-center align-self-center pr-3">
        <v-btn
          v-if="cohortStore.cohortId && size(cohortStore.filters)"
          id="show-hide-details-button"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          :text="`${cohortStore.isCompactView ? 'Show' : 'Hide'} Filters`"
          variant="text"
          @click="toggleShowHideDetails"
        />
        <div
          v-if="cohortStore.cohortId && cohortStore.isOwnedByCurrentUser && size(cohortStore.filters)"
          class="text-grey"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="cohortStore.cohortId && cohortStore.isOwnedByCurrentUser"
          id="rename-button"
          class="font-size-15 px-1"
          color="anchor"
          text="Rename"
          variant="text"
          @click="beginRename"
        />
        <div
          v-if="cohortStore.cohortId && cohortStore.isOwnedByCurrentUser"
          class="text-grey"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="cohortStore.cohortId && cohortStore.isOwnedByCurrentUser"
          id="delete-button"
          class="font-size-15 px-1"
          color="anchor"
          text="Delete"
          variant="text"
          @click="showDeleteModal = true"
        />
        <div
          v-if="(cohortStore.cohortId && cohortStore.isOwnedByCurrentUser) || (cohortStore.cohortId && size(cohortStore.filters))"
          class="text-grey"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="cohortStore.domain === 'default' && (cohortStore.cohortId || cohortStore.totalStudentCount !== undefined)"
          id="export-student-list-button"
          :disabled="isDownloadingCSV || !cohortStore.totalStudentCount || cohortStore.isModifiedSinceLastSearch"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          text="Export List"
          variant="text"
          @click="showExportStudentsModal = true"
        />
        <v-btn
          v-if="cohortStore.domain === 'admitted_students' && (cohortStore.cohortId || cohortStore.totalStudentCount !== undefined)"
          id="export-student-list-button"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          :disabled="isDownloadingCSV || !cohortStore.totalStudentCount || cohortStore.isModifiedSinceLastSearch"
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
          :disabled="cohortStore.isModifiedSinceLastSearch"
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
      :is-open="cohortStore.editMode === 'rename'"
    />
    <AreYouSureModal
      id="confirm-delete-modal"
      v-model="showDeleteModal"
      button-label-confirm="Delete"
      :function-cancel="cancelDeleteModal"
      :function-confirm="cohortDelete"
      modal-header="Delete Saved Cohort"
    >
      Are you sure you want to delete "<strong>{{ cohortStore.cohortName }}</strong>"?
    </AreYouSureModal>
    <ExportListModal
      id="export-students-modal"
      :cancel="cancelExportModal"
      :csv-columns-selected="getCsvExportColumnsSelected(cohortStore.domain)"
      :csv-columns="getCsvExportColumns(cohortStore.domain)"
      :error="error"
      :export="exportStudents"
      :show-modal="showExportStudentsModal"
    />
    <FerpaReminderModal
      id="export-admits-modal"
      :cancel="cancelExportModal"
      :confirm="() => exportStudents(getCsvExportColumnsSelected(cohortStore.domain))"
      :is-downloading="isDownloadingCSV"
      :show-modal="showExportAdmitsModal"
    />
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import ExportListModal from '@/components/util/ExportListModal'
import FerpaReminderModal from '@/components/util/FerpaReminderModal'
import RenameCohort from '@/components/cohort/RenameCohort'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {deleteCohort, downloadCohortCsv, downloadCsv} from '@/api/cohort'
import {get} from 'lodash'
import {getCsvExportColumns, getCsvExportColumnsSelected} from '@/berkeley'
import {pluralize} from '@/lib/utils'
import {ref, watch} from 'vue'
import router from '@/router'
import {size} from 'lodash'
import {useCohortStore} from '@/stores/cohort-edit-session'

defineProps({
  showHistory: {
    type: Boolean,
    required: true
  },
  toggleShowHistory: {
    type: Function,
    required: true
  }
})

const cohortStore = useCohortStore()

const error = ref(undefined)
const isDownloadingCSV = ref(false)
const isHistorySupported = ref(cohortStore.cohortId && cohortStore.domain === 'default')
const name = ref(cohortStore.cohortName)
const renameError = ref(undefined)
const showDeleteModal = ref(false)
const showExportAdmitsModal = ref(false)
const showExportStudentsModal = ref(false)

watch(name, () => {
  renameError.value = undefined
})
watch(showDeleteModal, () => {
  error.value = undefined
})
watch(showExportAdmitsModal, () => {
  error.value = undefined
})
watch(showExportStudentsModal, () => {
  error.value = undefined
})

const beginRename = () => {
  name.value = cohortStore.cohortName
  cohortStore.setEditMode('rename')
  alertScreenReader(`Renaming cohort '${name.value}'`)
  putFocusNextTick('rename-cohort-input')
}

const cancelDeleteModal = () => {
  showDeleteModal.value = false
  alertScreenReader(`Cancel deletion of cohort '${name.value}'`)
}

const cancelExportModal = () => {
  showExportAdmitsModal.value = showExportStudentsModal.value = false
  alertScreenReader(`Cancel export of cohort '${name.value}'`)
}

const cancelRename = () => {
  name.value = cohortStore.cohortName
  cohortStore.setEditMode(null)
  alertScreenReader(`Cancel renaming of cohort '${name.value}'`)
}

const cohortDelete = () => {
  alertScreenReader(`Deleting cohort '${name.value}'`)
  return deleteCohort(cohortStore.cohortId).then(() => {
    showDeleteModal.value = false
    alertScreenReader(`Deleted cohort '${name.value}'`)
    router.push({path: '/'})
  }, error => {
    alertScreenReader(`Failed to delete cohort '${name.value}'`)
    handleError(error)
  })
}

const downloadCsvPerFilters = csvColumnsSelected => {
  return new Promise((resolve, reject) => {
    const isReadOnly = cohortStore.cohortId && !cohortStore.isOwnedByCurrentUser
    if (isReadOnly) {
      downloadCohortCsv(cohortStore.cohortId, cohortStore.cohortName, csvColumnsSelected).then(resolve, reject)
    } else {
      downloadCsv(cohortStore.domain, cohortStore.cohortName, cohortStore.filters, csvColumnsSelected).then(resolve, reject)
    }
  })
}

const exportStudents = csvColumnsSelected => {
  isDownloadingCSV.value = true
  alertScreenReader(`Exporting cohort '${name.value}'`)
  return downloadCsvPerFilters(csvColumnsSelected).then(() => {
    showExportAdmitsModal.value = showExportStudentsModal.value = isDownloadingCSV.value = false
    alertScreenReader(`Downloading cohort '${name.value}'`)
  }, error => {
    alertScreenReader(`Failed to export cohort '${name.value}'`)
    handleError(error)
  })
}

const handleError = error => {
  error.value = get(error, 'message', 'An unknown error occurred.')
}

const toggleShowHideDetails = () => {
  cohortStore.toggleCompactView()
  alertScreenReader(cohortStore.isCompactView ? 'Filters are hidden' : 'Filters are visible')
}
</script>
