<template>
  <div>
    <div v-if="!cohortId && isUndefined(totalStudentCount)">
      <h1 id="page-header" class="mb-2">
        Create {{ domain === 'default' ? 'a Cohort' : 'an admissions cohort' }}
      </h1>
      <div v-if="domain === 'default'">
        Find a set of students, then save your search as a filtered cohort. Revisit your filtered cohorts at any time.
      </div>
      <div v-if="domain === 'admitted_students'">
        Find a set of admitted students using the filters below.
      </div>
    </div>
    <div v-if="editMode !== 'rename'" class="d-flex flex-wrap justify-space-between">
      <h1
        v-if="cohortName"
        id="page-header"
        class="align-self-center mb-0 mr-2"
      >
        {{ cohortName }}
        <span
          v-if="editMode !== 'apply' && !isUndefined(totalStudentCount)"
          class="text-medium-emphasis ml-1"
        ><span class="sr-only">, </span>({{ pluralize(domain === 'admitted_students' ? 'admit' : 'student', totalStudentCount) }})</span>
      </h1>
      <h1
        v-if="!cohortName && !isUndefined(totalStudentCount)"
        id="page-header"
        class="align-self-center mb-0 mr-2"
      >
        {{ pluralize('Result', totalStudentCount) }}
      </h1>
      <div v-if="!isCohortHistoryPage" class="d-flex align-center align-self-center pr-3">
        <a
          v-if="totalStudentCount > pagination.itemsPerPage"
          id="skip-to-pagination-link"
          href="#pagination-container"
          class="sr-only"
        >
          Skip to pagination
        </a>
        <a
          v-if="totalStudentCount"
          id="skip-to-students-link"
          href="#cohort-students"
          class="sr-only"
        >
          Skip to students
        </a>
        <v-btn
          v-if="cohortId && size(filters)"
          id="show-hide-details-button"
          aria-controls="cohort-filters"
          :aria-expanded="!isCompactView"
          :aria-label="`${isCompactView ? 'Show' : 'Hide'} Cohort Filters`"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          :text="`${isCompactView ? 'Show' : 'Hide'} Filters`"
          variant="text"
          @click="toggleShowHideDetails"
        />
        <div
          v-if="cohortId && isOwnedByCurrentUser && size(filters)"
          class="text-medium-emphasis"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="cohortId && isOwnedByCurrentUser"
          id="rename-cohort-button"
          aria-label="Rename Cohort"
          class="font-size-15 px-1"
          color="anchor"
          text="Rename"
          variant="text"
          @click="beginRename"
        />
        <div
          v-if="cohortId && isOwnedByCurrentUser"
          class="text-medium-emphasis"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="cohortId && isOwnedByCurrentUser"
          id="delete-cohort-button"
          aria-label="Delete Cohort"
          class="font-size-15 px-1"
          color="anchor"
          text="Delete"
          variant="text"
          @click="showDeleteModal = true"
        />
        <div
          v-if="(cohortId && isOwnedByCurrentUser) || (cohortId && size(filters))"
          class="text-medium-emphasis"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="domain === 'default' && (cohortId || !isUndefined(totalStudentCount))"
          id="export-student-list-button"
          :disabled="isDownloadingCSV || !totalStudentCount || isModifiedSinceLastSearch"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          text="Export List"
          variant="text"
          @click="showExportStudentsModal = true"
        />
        <v-btn
          v-if="domain === 'admitted_students' && (cohortId || !isUndefined(totalStudentCount))"
          id="export-student-list-button"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          :disabled="isDownloadingCSV || !totalStudentCount || isModifiedSinceLastSearch"
          text="Export List"
          variant="text"
          @click="showExportAdmitsModal = true"
        />
        <div
          v-if="isHistorySupported"
          class="text-medium-emphasis"
          role="separator"
        >
          |
        </div>
        <router-link
          v-if="isHistorySupported"
          id="cohort-history-link"
          class="v-btn v-btn--variant-text text-anchor text-capitalize font-size-15 px-1 text-no-wrap"
          :disabled="isModifiedSinceLastSearch"
          to="/cohort/history"
        >
          <span class="sr-only">Cohort</span>&nbsp;History
        </router-link>
      </div>
      <div v-if="isCohortHistoryPage" class="d-flex align-self-center mr-4">
        <router-link
          v-if="isHistorySupported"
          id="back-to-cohort-link"
          class="v-btn v-btn--variant-text text-anchor text-capitalize font-size-15 px-1 text-no-wrap"
          :to="`/cohort/${cohortId}`"
        >
          Back to Cohort
        </router-link>
      </div>
    </div>
    <div v-if="editMode === 'rename'" class="mt-1">
      <RenameCohort />
    </div>
    <AreYouSureModal
      id="confirm-delete-modal"
      v-model="showDeleteModal"
      button-label-confirm="Delete"
      :function-cancel="cancelDeleteModal"
      :function-confirm="cohortDelete"
      modal-header="Delete Saved Cohort"
    >
      Are you sure you want to delete "<strong>{{ cohortName }}</strong>"?
    </AreYouSureModal>
    <ExportListModal
      id="export-students-modal"
      :cancel="cancelExportModal"
      :csv-columns-selected="getCsvExportColumnsSelected(domain)"
      :csv-columns="getCsvExportColumns(domain)"
      :error="error"
      :export="exportStudents"
      :show-modal="showExportStudentsModal"
    />
    <FerpaReminderModal
      id="export-admits-modal"
      :cancel="cancelExportModal"
      :confirm="() => exportStudents(getCsvExportColumnsSelected(domain))"
      :is-downloading="isDownloadingCSV"
      :show-modal="showExportAdmitsModal"
    />
  </div>
</template>

<script setup>
import {get, isUndefined, size} from 'lodash'
import {ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {storeToRefs} from 'pinia'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import ExportListModal from '@/components/util/ExportListModal'
import FerpaReminderModal from '@/components/util/FerpaReminderModal'
import RenameCohort from '@/components/cohort/RenameCohort'
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'
import {deleteCohort, downloadCohortCsv, downloadCsv} from '@/api/cohort'
import {getCsvExportColumns, getCsvExportColumnsSelected} from '@/lib/berkeley-utils'
import {useCohortStore} from '@/stores/cohort-edit-session'

defineProps({
  isCohortHistoryPage: {
    type: Boolean,
    required: true
  }
})

const cohortStore = useCohortStore()
const {
  cohortId,
  cohortName,
  domain,
  editMode,
  filters,
  isCompactView,
  isOwnedByCurrentUser,
  isModifiedSinceLastSearch,
  pagination,
  totalStudentCount
} = storeToRefs(cohortStore)
const router = useRouter()
const error = ref(undefined)
const isDownloadingCSV = ref(false)
const isHistorySupported = ref(cohortId.value && domain.value === 'default')
const showDeleteModal = ref(false)
const showExportAdmitsModal = ref(false)
const showExportStudentsModal = ref(false)

watch(showDeleteModal, () => {
  putFocusNextTick('are-you-sure-cancel')
  error.value = undefined
})
watch(showExportAdmitsModal, () => {
  putFocusNextTick('csv-column-options-0')
  error.value = undefined
})
watch(showExportStudentsModal, () => {
  putFocusNextTick('csv-column-options-0')
  error.value = undefined
})

const beginRename = () => {
  cohortStore.setEditMode('rename')
  putFocusNextTick('rename-cohort-input')
}

const cancelDeleteModal = () => {
  showDeleteModal.value = false
  alertScreenReader('Canceled delete cohort')
  putFocusNextTick('delete-cohort-button')
}

const cancelExportModal = () => {
  showExportAdmitsModal.value = showExportStudentsModal.value = false
  alertScreenReader('Canceled export cohort')
  putFocusNextTick('export-student-list-button')
}

const cohortDelete = () => {
  alertScreenReader(`Deleting cohort "${cohortName.value}"`)
  deleteCohort(cohortId.value).then(
    () => {
      showDeleteModal.value = false
      alertScreenReader(`Deleted cohort "${cohortName.value}"`)
      router.push({path: '/'})
    },
    error => {
      alertScreenReader(`Failed to delete cohort "${cohortName.value}"`)
      handleError(error)
    }
  )
}

const downloadCsvPerFilters = csvColumnsSelected => {
  return new Promise((resolve, reject) => {
    const isReadOnly = cohortId.value && !isOwnedByCurrentUser.value
    if (isReadOnly) {
      downloadCohortCsv(cohortId.value, cohortName.value, csvColumnsSelected).then(resolve, reject)
    } else {
      downloadCsv(domain.value, cohortName.value, filters.value, csvColumnsSelected).then(resolve, reject)
    }
  })
}

const exportStudents = csvColumnsSelected => {
  isDownloadingCSV.value = true
  alertScreenReader(`Exporting cohort "${cohortName.value}"`)
  return downloadCsvPerFilters(csvColumnsSelected).then(
    () => {
      showExportAdmitsModal.value = showExportStudentsModal.value = isDownloadingCSV.value = false
      alertScreenReader(`Downloading cohort "${cohortName.value}"`)
      putFocusNextTick('export-student-list-button')
    },
    error => {
      alertScreenReader(`Failed to export cohort "${cohortName.value}"`)
      putFocusNextTick('export-student-list-button')
      handleError(error)
    }
  )
}

const handleError = error => {
  error.value = get(error, 'message', 'An unknown error occurred.')
}

const toggleShowHideDetails = () => {
  cohortStore.toggleCompactView()
  putFocusNextTick('show-hide-details-button', {scroll: false})
}
</script>
