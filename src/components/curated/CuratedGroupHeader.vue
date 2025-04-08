<template>
  <div>
    <div class="d-flex flex-wrap justify-space-between">
      <div v-if="mode !== 'rename'">
        <h1 id="curated-group-name" class="mb-0 mt-0">
          {{ curatedGroupName || domainLabel(true) }}
          <span v-if="!isNil(totalStudentCount)" class="text-medium-emphasis">
            ({{ pluralize(domain === 'admitted_students' ? 'admit' : 'student', totalStudentCount, {1: '1'}) }})
          </span>
        </h1>
        <div
          v-if="owner.id !== currentUser.id && (owner.name || owner.uid)"
          :id="`curated-group-owner-${owner.uid}`"
          class="text-medium-emphasis"
        >
          Owned by {{ owner.name || `UID ${owner.uid}` }}
          <span v-if="size(owner.deptCodes)">
            (<span id="cohort-owner-dept-codes">{{ owner.deptCodes.join(', ') }}</span>)
          </span>
        </div>
      </div>
      <a
        v-if="totalStudentCount > itemsPerPage"
        id="skip-to-pagination-link"
        href="#pagination-container"
        class="sr-only"
      >
        Skip to pagination
      </a>
      <a
        v-if="totalStudentCount"
        id="skip-to-students-link"
        href="#curated-cohort-students"
        class="sr-only"
      >
        Skip to students
      </a>
      <div v-if="mode === 'rename'" class="w-100">
        <RenameCuratedGroup />
      </div>
      <div v-if="!mode" class="d-flex align-center">
        <div v-if="owner.id === currentUser.id">
          <v-btn
            id="bulk-add-sids-button"
            class="font-size-15 px-1"
            color="anchor"
            variant="text"
            @click="enterBulkAddMode"
          >
            Add {{ domain === 'admitted_students' ? 'Admits' : 'Students' }}<span class="sr-only">to {{ domainLabel(false) }}</span>
          </v-btn>
        </div>
        <div
          v-if="owner.id === currentUser.id"
          class="text-medium-emphasis"
          role="separator"
        >
          |
        </div>
        <div v-if="owner.id === currentUser.id">
          <v-btn
            id="rename-curated-group-button"
            :aria-label="`Rename ${domainLabel(false)}`"
            class="font-size-15 px-1"
            color="anchor"
            text="Rename"
            variant="text"
            @click="enterRenameMode"
          />
        </div>
        <div v-if="owner.id === currentUser.id" class="text-medium-emphasis">|</div>
        <div v-if="owner.id === currentUser.id">
          <v-btn
            id="delete-curated-group-button"
            :aria-label="`Delete ${domainLabel(false)}`"
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
            :modal-header="`Delete ${domainLabel(false)}`"
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
        <div v-if="owner.id === currentUser.id" class="text-medium-emphasis">|</div>
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
    <div v-if="referencingCohorts.length">
      <div v-if="owner.id === currentUser.id">
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
      <div v-if="owner.id !== currentUser.id">
        Used as a filter in {{ referencingCohorts.length === 1 ? 'a cohort' : 'cohorts' }} owned by the owner of this {{ domainLabel(true) }}.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {each, find, isNil, map, size, sortBy} from 'lodash'
import {onMounted, ref, watch} from 'vue'
import {storeToRefs} from 'pinia'
import {useRouter} from 'vue-router'
import type {Cohort} from '@/lib/types'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import ExportListModal from '@/components/util/ExportListModal.vue'
import FerpaReminderModal from '@/components/util/FerpaReminderModal.vue'
import RenameCuratedGroup from '@/components/curated/RenameCuratedGroup.vue'
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'
import {deleteCuratedGroup, downloadCuratedGroupCsv} from '@/api/curated'
import {describeCuratedGroupDomain, getCsvExportColumns, getCsvExportColumnsSelected} from '@/lib/berkeley-utils'
import {useContextStore} from '@/stores/context'
import {useCuratedGroupStore} from '@/stores/curated-group'

const contextStore = useContextStore()
const curatedStore = useCuratedGroupStore()
const router = useRouter()

const {curatedGroupId, curatedGroupName, domain, itemsPerPage, mode, owner, referencingCohortIds, totalStudentCount} = storeToRefs(curatedStore)
const currentUser = contextStore.currentUser
const exportEnabled = ref(true)
const isCohortWarningModalOpen = ref(false)
const isDeleteModalOpen = ref(false)
const isDeleting = ref(false)
const referencingCohorts = ref<Cohort[]>([])
const showExportAdmitsModal = ref(false)
const showExportStudentsModal = ref(false)

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
  if (owner.value.id === currentUser.id) {
    each(referencingCohortIds.value || [], cohortId => {
      const cohort: Cohort | undefined = find(currentUser.myCohorts, ['id', cohortId])
      if (cohort) {
        referencingCohorts.value.push(cohort)
      }
    })
    referencingCohorts.value = sortBy(referencingCohorts.value, ['name'])
  } else {
    referencingCohorts.value = map<number, Cohort>(referencingCohortIds.value, (id: number): Cohort => ({id, domain: domain.value, name: '', totalStudentCount: NaN}))
  }
})

const cancelDeleteModal = () => {
  isDeleteModalOpen.value = false
  alertScreenReader(`Canceled delete ${domainLabel(false)}`)
  putFocusNextTick('delete-curated-group-button')
}

const cancelExportModal = () => {
  showExportAdmitsModal.value = showExportStudentsModal.value = false
  alertScreenReader(`Canceled export ${domainLabel(false)}`)
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
  curatedStore.setMode('rename')
  putFocusNextTick('rename-curated-group-input')
}

const exportGroup = csvColumnsSelected => {
  showExportAdmitsModal.value = showExportStudentsModal.value = exportEnabled.value = false
  alertScreenReader(`Exporting ${domainLabel(false)} ${curatedGroupName.value}`)
  return downloadCuratedGroupCsv(curatedGroupId.value, curatedGroupName.value, csvColumnsSelected).then(() => {
    exportEnabled.value = true
    alertScreenReader(`Downloading ${domainLabel(false)} ${curatedGroupName.value}`)
  })
}

const deleteGroup = () => {
  alertScreenReader(`Deleting ${domainLabel(false)} "${curatedGroupName.value}"`)
  isDeleting.value = true
  deleteCuratedGroup(domain.value, curatedGroupId.value).then(() => {
    isDeleteModalOpen.value = false
    alertScreenReader(`Deleted ${domainLabel(false)} "${curatedGroupName.value}"`)
    router.push({path: '/'}).then(() => {
      isDeleting.value = false
    })
  }).catch(error => {
    alertScreenReader(`Failed to delete ${domainLabel(false)} "${curatedGroupName.value}"`)
    error.value = error
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
</script>
