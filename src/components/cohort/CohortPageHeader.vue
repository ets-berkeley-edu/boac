<template>
  <div>
    <div v-if="!cohortStore.cohortId && isUndefined(cohortStore.totalStudentCount)">
      <h1 id="page-header">
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
        id="page-header"
        class="align-self-center mb-0 mr-2"
      >
        {{ cohortStore.cohortName }}
        <span
          v-if="cohortStore.editMode !== 'apply' && !isUndefined(cohortStore.totalStudentCount)"
          class="text-medium-emphasis ml-1"
        ><span class="sr-only">, </span>{{ pluralize(cohortStore.domain === 'admitted_students' ? 'admit' : 'student', cohortStore.totalStudentCount) }}</span>
      </h1>
      <h1
        v-if="!cohortStore.cohortName && !isUndefined(cohortStore.totalStudentCount)"
        id="page-header"
        class="align-self-center mb-0 mr-2"
      >
        {{ pluralize('Result', cohortStore.totalStudentCount) }}
      </h1>
      <div v-if="!isCohortHistoryPage" class="d-flex align-center align-self-center pr-3">
        <a
          v-if="cohortStore.totalStudentCount > cohortStore.pagination.itemsPerPage"
          id="skip-to-pagination-link"
          href="#pagination-container"
          class="sr-only"
        >
          Skip to pagination
        </a>
        <a
          id="skip-to-students-link"
          href="#cohort-students"
          class="sr-only"
        >
          Skip to students
        </a>
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
          class="text-medium-emphasis"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="cohortStore.cohortId && cohortStore.isOwnedByCurrentUser"
          id="rename-cohort-button"
          class="font-size-15 px-1"
          color="anchor"
          text="Rename"
          variant="text"
          @click="beginRename"
        />
        <div
          v-if="cohortStore.cohortId && cohortStore.isOwnedByCurrentUser"
          class="text-medium-emphasis"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="cohortStore.cohortId && cohortStore.isOwnedByCurrentUser"
          id="delete-cohort-button"
          class="font-size-15 px-1"
          color="anchor"
          text="Delete"
          variant="text"
          @click="showDeleteModal = true"
        />
        <div
          v-if="(cohortStore.cohortId && cohortStore.isOwnedByCurrentUser) || (cohortStore.cohortId && size(cohortStore.filters))"
          class="text-medium-emphasis"
          role="separator"
        >
          |
        </div>
        <v-btn
          v-if="cohortStore.domain === 'default' && (cohortStore.cohortId || !isUndefined(cohortStore.totalStudentCount))"
          id="export-student-list-button"
          :disabled="isDownloadingCSV || !cohortStore.totalStudentCount || cohortStore.isModifiedSinceLastSearch"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          text="Export List"
          variant="text"
          @click="showExportStudentsModal = true"
        />
        <v-btn
          v-if="cohortStore.domain === 'admitted_students' && (cohortStore.cohortId || !isUndefined(cohortStore.totalStudentCount))"
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
          class="text-medium-emphasis"
          role="separator"
        >
          |
        </div>
        <router-link
          v-if="isHistorySupported"
          id="cohort-history-link"
          class="v-btn v-btn--variant-text text-anchor text-capitalize font-size-15 px-1 text-no-wrap"
          :disabled="cohortStore.isModifiedSinceLastSearch"
          to="/cohort/history"
        >
          <span class="sr-only">Cohort </span>History
        </router-link>
      </div>
      <div v-if="isCohortHistoryPage" class="d-flex align-self-center mr-4">
        <router-link
          v-if="isHistorySupported"
          id="back-to-cohort-link"
          class="v-btn v-btn--variant-text text-anchor text-capitalize font-size-15 px-1 text-no-wrap"
          :to="`/cohort/${cohortStore.cohortId}`"
        >
          Back to Cohort
        </router-link>
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
import {get, isUndefined} from 'lodash'
import {getCsvExportColumns, getCsvExportColumnsSelected} from '@/berkeley'
import {pluralize} from '@/lib/utils'
import {ref, watch} from 'vue'
import {size} from 'lodash'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {useRouter} from 'vue-router'

defineProps({
  isCohortHistoryPage: {
    type: Boolean,
    required: true
  }
})

const cohortStore = useCohortStore()
const router = useRouter()

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
  name.value = cohortStore.cohortName
  cohortStore.setEditMode('rename')
  alertScreenReader(`Renaming cohort '${name.value}'`)
  putFocusNextTick('rename-cohort-input')
}

const cancelDeleteModal = () => {
  const cohortName = cohortStore.cohortName ? `'${cohortStore.cohortName}'` : ''
  showDeleteModal.value = false
  alertScreenReader(`Cancel deletion of cohort ${cohortName}`)
  putFocusNextTick('delete-cohort-button')
}

const cancelExportModal = () => {
  const cohortName = cohortStore.cohortName ? `'${cohortStore.cohortName}'` : ''
  showExportAdmitsModal.value = showExportStudentsModal.value = false
  alertScreenReader(`Cancel export of cohort ${cohortName}`)
  putFocusNextTick('export-student-list-button')
}

const cancelRename = () => {
  name.value = cohortStore.cohortName
  cohortStore.setEditMode(null)
  alertScreenReader(`Cancel renaming of cohort '${name.value}'`)
  putFocusNextTick('rename-cohort-button')
}

const cohortDelete = () => {
  alertScreenReader(`Deleting cohort '${name.value}'`)
  deleteCohort(cohortStore.cohortId).then(() => {
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
  const cohortName = name.value ? `'${name.value}'` : ''
  isDownloadingCSV.value = true
  alertScreenReader(`Exporting cohort ${cohortName}`)
  return downloadCsvPerFilters(csvColumnsSelected).then(() => {
    showExportAdmitsModal.value = showExportStudentsModal.value = isDownloadingCSV.value = false
    alertScreenReader(`Downloading cohort ${cohortName}`)
    putFocusNextTick('export-student-list-button')
  }, error => {
    alertScreenReader(`Failed to export cohort ${cohortName}`)
    handleError(error)
  })
}

const handleError = error => {
  error.value = get(error, 'message', 'An unknown error occurred.')
}

const toggleShowHideDetails = () => {
  cohortStore.toggleCompactView()
  alertScreenReader(cohortStore.isCompactView ? 'Filters are hidden' : 'Filters are visible')
  putFocusNextTick('show-hide-details-button')
}
</script>
