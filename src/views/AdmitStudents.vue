<template>
  <div v-if="!contextStore.loading" class="default-margins">
    <div class="d-flex flex-wrap justify-space-between">
      <h1 id="cohort-name">
        CE3 Admissions
        <span
          v-if="totalAdmitCount !== undefined"
          class="text-medium-emphasis"
        >{{ pluralize('admitted student', totalAdmitCount) }}</span>
      </h1>
      <a
        v-if="totalAdmitCount > pagination.itemsPerPage"
        id="skip-to-pagination-widget"
        class="sr-only"
        href="#pagination-container"
      >
        Skip to pagination
      </a>
      <div class="d-flex align-center align-self-center mr-6">
        <v-btn
          id="admitted-students-cohort-show-filters"
          class="font-size-15 px-1 text-no-wrap"
          aria-label="Create a CE3 Admissions cohort"
          color="anchor"
          variant="text"
          @click="createNewAdmittedStudentsCohort"
        >
          Create Cohort
        </v-btn>
        <div class="text-medium-emphasis" role="separator">|</div>
        <v-btn
          id="export-student-list-button"
          :disabled="!exportEnabled || !totalAdmitCount"
          class="font-size-15 px-1 text-no-wrap"
          color="anchor"
          text="Export List"
          variant="text"
          @click="openFerpaReminderDialog"
        />
        <FerpaReminderModal
          :cancel="cancelExportModal"
          :confirm="exportCohort"
          :is-downloading="isDownloadingCSV"
          :show-modal="showExportListDialog"
        />
      </div>
    </div>
    <div v-if="admits" class="pb-2">
      <AdmitDataWarning :updated-at="get(admits, '[0].updatedAt')" />
    </div>
    <SectionSpinner :loading="sorting" />
    <div v-if="!sorting">
      <div class="align-center d-flex justify-content-end mr-6">
        <div class="mr-auto">
          <CuratedGroupSelector
            context-description="Admit Students"
            domain="admitted_students"
            :students="admits"
          />
        </div>
        <div class="mr-4">
          <SortBy domain="admitted_students" />
        </div>
      </div>
      <div v-if="totalAdmitCount > pagination.itemsPerPage" class="mt-3">
        <Pagination
          :click-handler="goToPage"
          :init-page-number="pagination.currentPage"
          :limit="10"
          :per-page="pagination.itemsPerPage"
          :total-rows="totalAdmitCount"
        />
      </div>
      <div class="mt-3">
        <AdmitStudentsTable
          :include-curated-checkbox="true"
          :students="admits"
        />
        <hr />
      </div>
      <div v-if="totalAdmitCount > pagination.itemsPerPage" class="mt-3">
        <Pagination
          :click-handler="goToPage"
          id-prefix="auxiliary-pagination"
          :init-page-number="pagination.currentPage"
          :is-widget-at-bottom-of-page="true"
          :limit="10"
          :per-page="pagination.itemsPerPage"
          :total-rows="totalAdmitCount"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdmitStudentsTable from '@/components/admit/AdmitStudentsTable'
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector'
import FerpaReminderModal from '@/components/util/FerpaReminderModal'
import Pagination from '@/components/util/Pagination'
import SectionSpinner from '@/components/util/SectionSpinner'
import SortBy from '@/components/student/SortBy'
import {alertScreenReader, pluralize, putFocusNextTick, toInt} from '@/lib/utils'
import {downloadCsv} from '@/api/cohort'
import {get, map} from 'lodash'
import {getAdmitCsvExportColumns} from '@/berkeley'
import {getAllAdmits} from '@/api/admit'
import {onBeforeUnmount, onMounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {useRoute, useRouter} from 'vue-router'

const admits = ref(undefined)
const contextStore = useContextStore()
const counter = ref(null)
const exportEnabled = ref(true)
const isDownloadingCSV = ref(false)
const pagination = {currentPage: 1, itemsPerPage: 50}
const route = useRoute()
const router = useRouter()
const showExportListDialog = ref(false)
const sorting = ref(false)
const totalAdmitCount = ref(undefined)

contextStore.loadingStart()

onMounted(() => {
  contextStore.setEventHandler('admitSortBy-user-preference-change', onAdmitSortByUserPreferenceChange)
  counter.value = toInt(route.query._, 0)
  initPagination()
  loadAdmits()
})

onBeforeUnmount(() => {
  contextStore.removeEventHandler('admitSortBy-user-preference-change', onAdmitSortByUserPreferenceChange)
})

const cancelExportModal = () => {
  showExportListDialog.value = false
  alertScreenReader('Export canceled')
}

const createNewAdmittedStudentsCohort = () => {
  router.push({
    path: '/cohort/new',
    query: {domain: 'admitted_students'}
  })
}

const exportCohort = () => {
  const name = 'CE3 Admissions'
  isDownloadingCSV.value = true
  exportEnabled.value = false
  alertScreenReader(`Exporting cohort ${name}`)
  downloadCsv(
    'admitted_students',
    name,
    [],
    map(getAdmitCsvExportColumns(), 'value')
  ).then(() => {
    showExportListDialog.value = false
    exportEnabled.value = true
    isDownloadingCSV.value = false
  })
}

const goToPage = page => {
  if (page !== pagination.currentPage) {
    if (pagination.currentPage) {
      alertScreenReader(`Loading page ${page} of this cohort's students`)
    }
    pagination.currentPage = page
    router.push({
      query: {...route.query, p: pagination.currentPage}
    })
  }
}

const initPagination = () => {
  if (route.query.p && !isNaN(route.query.p)) {
    pagination.currentPage = parseInt(route.query.p, 10)
  }
}

const loadAdmits = () => {
  const limit = pagination.itemsPerPage
  const offset =
    pagination.currentPage === 0
      ? 0
      : (pagination.currentPage - 1) * limit
  getAllAdmits(contextStore.currentUser.preferences.admitSortBy, limit, offset).then(response => {
    if (response) {
      admits.value = get(response, 'students')
      totalAdmitCount.value = get(response, 'totalStudentCount')
      contextStore.loadingComplete(`${totalAdmitCount.value} CE3 admits loaded`, 'cohort-name')
    } else {
      router.push({path: '/404'})
    }
    sorting.value = false
  })
}

const onAdmitSortByUserPreferenceChange = sortBy => {
  sorting.value = true
  loadAdmits()
  if (!contextStore.loading) {
    goToPage(1)
    alertScreenReader(`Sort admitted students by ${sortBy}`)
  }
}

const openFerpaReminderDialog = () => {
  showExportListDialog.value = true
  putFocusNextTick('modal-header')
}
</script>
