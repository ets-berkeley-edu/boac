<template>
  <div>
    <div class="d-flex flex-wrap justify-space-between">
      <div v-if="mode !== 'rename'">
        <h1 id="curated-group-name" class="page-section-header mb-0 mt-0">
          {{ curatedGroupName || domainLabel(true) }}
          <span v-if="!isNil(totalStudentCount)" class="text-medium-emphasis">
            ({{ pluralize(domain === 'admitted_students' ? 'admit' : 'student', totalStudentCount, {1: '1'}) }})
          </span>
        </h1>
      </div>
      <div v-if="mode === 'rename'" class="mr-3 w-100">
        <div class="align-center d-flex">
          <div class="w-75">
            <v-text-field
              id="rename-curated-group-input"
              v-model="renameInput"
              :aria-invalid="!renameInput"
              :aria-label="`${domainLabel(true)} name, 255 characters or fewer`"
              :aria-required="true"
              class="mr-3"
              :disabled="isSaving"
              hide-details
              maxlength="255"
              required
              @keyup.enter="rename"
              @keyup.esc="exitRenameMode"
            />
          </div>
          <div>
            <v-btn
              id="rename-curated-group-confirm"
              color="primary"
              :disabled="!size(renameInput) || isSaving"
              text="Rename"
              @click="rename"
            />
          </div>
          <div>
            <v-btn
              id="rename-curated-group-cancel"
              class="ml-1"
              :disabled="isSaving"
              text="Cancel"
              variant="text"
              @click="exitRenameMode"
            />
          </div>
        </div>
        <div v-if="renameError" aria-live="polite" class="text-error ml-2 my-2">{{ renameError }}</div>
        <div class="text-medium-emphasis">255 character limit <span v-if="size(renameInput)">({{ 255 - size(renameInput) }} left)</span></div>
        <span
          v-if="size(renameInput) === 255"
          aria-live="polite"
          class="sr-only"
          role="alert"
        >
          Name cannot exceed 255 characters.
        </span>
      </div>
      <div v-if="!mode" class="d-flex align-center">
        <div v-if="ownerId === currentUser.id">
          <v-btn
            id="bulk-add-sids-button"
            class="font-size-15 px-1"
            color="anchor"
            variant="text"
            @click="enterBulkAddMode"
          >
            Add {{ domain === 'admitted_students' ? 'Admits' : 'Students' }}
          </v-btn>
        </div>
        <div
          v-if="ownerId === currentUser.id"
          class="text-medium-emphasis"
          role="separator"
        >
          |
        </div>
        <div v-if="ownerId === currentUser.id">
          <v-btn
            id="rename-curated-group-button"
            class="font-size-15 px-1"
            color="anchor"
            text="Rename"
            variant="text"
            @click="enterRenameMode"
          />
        </div>
        <div v-if="ownerId === currentUser.id" class="text-medium-emphasis">|</div>
        <div v-if="ownerId === currentUser.id">
          <v-btn
            id="delete-curated-group-button"
            class="font-size-15 px-1"
            color="anchor"
            text="Delete"
            variant="text"
            @click="onClickDelete"
          />
          <AreYouSureModal
            v-model="isDeleteModalOpen"
            :button-label-confirm="isDeleting ? 'Deleting' : 'Delete'"
            :function-confirm="deleteGroup"
            :function-cancel="cancelDeleteModal"
            modal-header="Delete Curated Group"
          >
            Are you sure you want to delete "<strong>{{ curatedGroupName }}</strong>"?
          </AreYouSureModal>
          <AreYouSureModal
            v-model="isCohortWarningModalOpen"
            button-label-confirm="Close"
            :function-confirm="confirmDeleteWarning"
            modal-header="This group is in use as a cohort filter"
          >
            Sorry, you cannot delete this {{ domainLabel(false) }} until you have removed the filter from
            <span v-if="referencingCohorts.length === 1">cohort <span class="font-weight-bold">{{ referencingCohorts[0].name }}</span>.</span>
            <span v-if="referencingCohorts.length > 1">cohorts:</span>
            <ul v-if="referencingCohorts.length > 1" class="mb-0 mt-2">
              <li v-for="cohort in referencingCohorts" :key="cohort.id">
                <span class="font-weight-bold">{{ cohort.name }}</span>
              </li>
            </ul>
          </AreYouSureModal>
        </div>
        <div v-if="ownerId === currentUser.id" class="text-medium-emphasis">|</div>
        <div>
          <v-btn
            v-if="domain === 'default'"
            id="export-student-list-button"
            class="font-size-15 px-1 text-primary"
            :disabled="!exportEnabled || !totalStudentCount"
            text="Export List"
            variant="text"
            @click="() => showExportStudentsModal = true"
          />
          <v-btn
            v-if="domain === 'admitted_students'"
            id="export-student-list-button"
            class="font-size-15 px-1 text-primary"
            :disabled="!exportEnabled || !totalStudentCount"
            text="Export List"
            variant="text"
            @click="() => showExportAdmitsModal = true"
          />
          <ExportListModal
            id="export-students-modal"
            :cancel="cancelExportModal"
            :csv-columns="getCsvExportColumns(domain)"
            :csv-columns-selected="getCsvExportColumnsSelected(domain)"
            :export="exportGroup"
            :show-modal="showExportStudentsModal"
          />
          <FerpaReminderModal
            id="export-admits-modal"
            :show-modal="showExportAdmitsModal"
            :cancel="cancelExportModal"
            :confirm="() => exportGroup(getCsvExportColumnsSelected(domain))"
          />
        </div>
      </div>
    </div>
    <div v-if="referencingCohorts.length" class="pb-2">
      Used as a filter in {{ referencingCohorts.length === 1 ? 'cohort' : 'cohorts' }}
      <router-link
        v-if="referencingCohorts.length === 1"
        id="referencing-cohort-0"
        aria-label="Link to cohort"
        :to="`/cohort/${referencingCohorts[0].id}`"
      >
        {{ referencingCohorts[0].name }}.
      </router-link>
      <span v-if="referencingCohorts.length > 1">
        <span v-for="(cohort, index) in referencingCohorts" :key="cohort.id">
          <span v-if="index === referencingCohorts.length - 1">and </span>
          <router-link
            :id="`referencing-cohort-${index}`"
            aria-label="Link to cohort"
            :to="`/cohort/${cohort.id}`"
          >{{ cohort.name }}</router-link>{{ index === referencingCohorts.length - 1 ? '.' : (referencingCohorts.length > 2 ? ',' : '') }}
        </span>
      </span>
    </div>
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import ExportListModal from '@/components/util/ExportListModal'
import FerpaReminderModal from '@/components/util/FerpaReminderModal'
import router from '@/router'
import {alertScreenReader, pluralize, setPageTitle} from '@/lib/utils'
import {deleteCuratedGroup, downloadCuratedGroupCsv, renameCuratedGroup} from '@/api/curated'
import {describeCuratedGroupDomain, getCsvExportColumns, getCsvExportColumnsSelected} from '@/berkeley'
import {each, find, isNil, noop, size, sortBy} from 'lodash'
import {onMounted, ref, watch} from 'vue'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useCuratedGroupStore} from '@/stores/curated-group'
import {validateCohortName} from '@/lib/cohort'
import {storeToRefs} from 'pinia'

const contextStore = useContextStore()
const curatedStore = useCuratedGroupStore()

const {curatedGroupId, curatedGroupName, domain, mode, ownerId, referencingCohortIds, totalStudentCount} = storeToRefs(curatedStore)
const currentUser = contextStore.currentUser
const exportEnabled = ref(true)
const isCohortWarningModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const isDeleting = ref(false)
const isSaving = ref(false)
const referencingCohorts = ref([])
const renameError = ref(undefined)
const renameInput = ref(undefined)
const showExportAdmitsModal = ref(false)
const showExportStudentsModal = ref(false)

watch(renameInput, () => {
  renameError.value = undefined
})
watch(showExportAdmitsModal, isOpen => {
  if (isOpen) {
    putFocusNextTick('csv-column-options-0')
  }
})
watch(showExportStudentsModal, isOpen => {
  if (isOpen) {
    putFocusNextTick('csv-column-options-0')
  }
})

onMounted(() => {
  each(referencingCohortIds.value || [], cohortId => {
    const cohort = find(currentUser.myCohorts, ['id', cohortId])
    referencingCohorts.value.push(cohort)
  })
  referencingCohorts.value = sortBy(referencingCohorts.value, ['name'])
  putFocusNextTick('curated-group-name')
})

const cancelDeleteModal = () => {
  isDeleteModalOpen.value = false
  alertScreenReader('Canceled delete')
  putFocusNextTick('delete-curated-group-button')
}

const cancelExportModal = () => {
  showExportAdmitsModal.value = showExportStudentsModal.value = false
  alertScreenReader(`Canceled export of ${curatedGroupName.value} ${domainLabel(false)}`)
  putFocusNextTick('export-student-list-button')
}

const confirmDeleteWarning = () => {
  isCohortWarningModalOpen.value = false
  alertScreenReader('Closed')
  putFocusNextTick('delete-curated-group-button')
}

const enterBulkAddMode = () => {
  curatedStore.setMode('bulkAdd')
}

const enterRenameMode = () => {
  renameInput.value = curatedGroupName.value
  curatedStore.setMode('rename')
  putFocusNextTick('rename-curated-group-input')
}

const exitRenameMode = () => {
  renameInput.value = undefined
  curatedStore.resetMode()
  alertScreenReader('Canceled rename')
  putFocusNextTick('rename-curated-group-button')
}

const exportGroup = csvColumnsSelected => {
  showExportAdmitsModal.value = showExportStudentsModal.value = exportEnabled.value = false
  alertScreenReader(`Exporting ${curatedGroupName.value} ${domainLabel(false)}`)
  return downloadCuratedGroupCsv(curatedGroupId.value, curatedGroupName.value, csvColumnsSelected).then(() => {
    exportEnabled.value = true
    alertScreenReader('Export is done.')
  })
}

const deleteGroup = () => {
  isDeleting.value = true
  return deleteCuratedGroup(domain.value, curatedGroupId.value).then(() => {
    isDeleteModalOpen.value = false
    alertScreenReader(`Deleted ${domainLabel(false)}`)
    router.push({path: '/'}, noop)
  }).catch(error => {
    error.value = error
  }).finally(() => {
    isDeleting.value = false
  })
}

const domainLabel = capitalize => {
  return describeCuratedGroupDomain(domain.value, capitalize)
}

const onClickDelete = () => {
  const hasReferencingCohorts = !!referencingCohorts.value.length
  isCohortWarningModalOpen.value = hasReferencingCohorts
  isDeleteModalOpen.value = !hasReferencingCohorts
}

const rename = () => {
  const error = validateCohortName({name: renameInput.value})
  if (error !== true) {
    renameError.value = error
    putFocusNextTick('rename-curated-group-input')
  } else {
    isSaving.value = true
    renameCuratedGroup(curatedGroupId.value, renameInput.value).then(curatedGroup => {
      curatedStore.setCuratedGroupName(curatedGroup.name)
      setPageTitle(curatedGroup.name)
      exitRenameMode()
      isSaving.value = false
      alertScreenReader(`Renamed ${domainLabel(false)}`)
      putFocusNextTick('rename-curated-group-button"')
    })
  }
}
</script>
