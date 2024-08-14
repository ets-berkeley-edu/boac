<template>
  <div>
    <div class="d-flex flex-wrap justify-space-between">
      <div v-if="mode !== 'rename'">
        <h1 id="curated-group-name" class="page-section-header mb-0 mt-0">
          {{ curatedGroupName || domainLabel(true) }}
          <span v-if="!_isNil(totalStudentCount)" class="text-grey">
            ({{ pluralize(domain === 'admitted_students' ? 'admit' : 'student', totalStudentCount, {1: '1'}) }})
          </span>
        </h1>
      </div>
      <div v-if="mode === 'rename'" class="mr-3 w-100">
        <div class="align-center d-flex">
          <div class="w-75">
            <v-text-field
              id="rename-input"
              v-model="renameInput"
              :aria-invalid="!renameInput"
              :aria-label="`${domainLabel(true)} name, 255 characters or fewer`"
              :aria-required="true"
              class="mr-3"
              density="compact"
              :disabled="isSaving"
              hide-details
              maxlength="255"
              required
              variant="outlined"
              @keyup.enter="rename"
              @keyup.esc="exitRenameMode"
            />
          </div>
          <div>
            <v-btn
              id="rename-confirm"
              color="primary"
              :disabled="!_size(renameInput)"
              text="Rename"
              @click="rename"
            />
          </div>
          <div>
            <v-btn
              id="rename-cancel"
              :disabled="isSaving"
              text="Cancel"
              variant="plain"
              @click="exitRenameMode"
            />
          </div>
        </div>
        <div v-if="renameError" aria-live="polite" class="text-error ml-2 my-2">{{ renameError }}</div>
        <div class="text-grey">255 character limit <span v-if="_size(renameInput)">({{ 255 - _size(renameInput) }} left)</span></div>
        <span v-if="_size(renameInput) === 255" aria-live="polite" class="sr-only">Name cannot exceed 255 characters.</span>
      </div>
      <div v-if="!mode" class="d-flex align-center">
        <div v-if="isOwnedByCurrentUser">
          <v-btn
            id="bulk-add-sids-button"
            class="px-1"
            color="anchor"
            variant="text"
            @click="enterBulkAddMode"
          >
            Add {{ domain === 'admitted_students' ? 'Admits' : 'Students' }}
          </v-btn>
        </div>
        <div
          v-if="isOwnedByCurrentUser"
          class="text-grey"
          role="separator"
        >
          |
        </div>
        <div v-if="isOwnedByCurrentUser">
          <v-btn
            id="rename-button"
            class="font-size-15 px-1"
            color="anchor"
            text="Rename"
            variant="text"
            @click="enterRenameMode"
          />
        </div>
        <div v-if="isOwnedByCurrentUser" class="text-grey">|</div>
        <div v-if="isOwnedByCurrentUser">
          <v-btn
            id="delete-button"
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
            :function-cancel="() => isDeleteModalOpen = false"
            modal-header="Delete Curated Group"
          >
            Are you sure you want to delete "<strong>{{ curatedGroupName }}</strong>"?
          </AreYouSureModal>
          <AreYouSureModal
            v-model="isCohortWarningModalOpen"
            button-label-confirm="Close"
            :function-confirm="() => isCohortWarningModalOpen = false"
            modal-header="This group is in use as a cohort filter"
          >
            Sorry, you cannot delete this {{ domainLabel(false) }} until you have removed the filter from
            <span v-if="referencingCohorts.length === 1">cohort <span class="font-weight-700">{{ referencingCohorts[0].name }}</span>.</span>
            <span v-if="referencingCohorts.length > 1">cohorts:</span>
            <ul v-if="referencingCohorts.length > 1" class="mb-0 mt-2">
              <li v-for="cohort in referencingCohorts" :key="cohort.id">
                <span class="font-weight-700">{{ cohort.name }}</span>
              </li>
            </ul>
          </AreYouSureModal>
        </div>
        <div v-if="isOwnedByCurrentUser" class="text-grey">|</div>
        <div>
          <v-btn
            v-if="domain === 'default'"
            id="export-student-list-button"
            class="px-1 text-primary"
            :disabled="!exportEnabled || !totalStudentCount"
            text="Export List"
            variant="text"
            @click="() => showExportStudentsModal = true"
          />
          <v-btn
            v-if="domain === 'admitted_students'"
            id="export-student-list-button"
            class="px-1 text-primary"
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

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import Context from '@/mixins/Context'
import CuratedEditSession from '@/mixins/CuratedEditSession'
import ExportListModal from '@/components/util/ExportListModal'
import FerpaReminderModal from '@/components/util/FerpaReminderModal'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
import {deleteCuratedGroup, downloadCuratedGroupCsv, renameCuratedGroup} from '@/api/curated'
import {describeCuratedGroupDomain, getCsvExportColumns, getCsvExportColumnsSelected} from '@/berkeley'
import {useCuratedGroupStore} from '@/stores/curated-group'
import {validateCohortName} from '@/lib/cohort'

export default {
  name: 'CuratedGroupHeader',
  components: {AreYouSureModal, ExportListModal, FerpaReminderModal},
  mixins: [Context, CuratedEditSession, Util],
  setup() {
    const curatedGroupStore = useCuratedGroupStore()
    return {curatedGroupStore}
  },
  data: () => ({
    exportEnabled: true,
    isCohortWarningModalOpen: false,
    isDeleteModalOpen: false,
    isDeleting: false,
    isSaving: false,
    referencingCohorts: [],
    renameError: undefined,
    renameInput: undefined,
    showExportAdmitsModal: false,
    showExportStudentsModal: false
  }),
  computed: {
    isOwnedByCurrentUser() {
      return this.ownerId === this.currentUser.id
    }
  },
  watch: {
    renameInput() {
      this.renameError = undefined
    }
  },
  mounted() {
    if (this.referencingCohortIds?.length) {
      this._each(this.referencingCohortIds, cohortId => {
        const cohort = this._find(this.currentUser.myCohorts, ['id', cohortId])
        this.referencingCohorts.push(cohort)
      })
      this.referencingCohorts = this._sortBy(this.referencingCohorts, ['name'])
    }
    this.putFocusNextTick('curated-group-name')
  },
  methods: {
    cancelExportModal() {
      this.showExportAdmitsModal = this.showExportStudentsModal = false
      alertScreenReader(`Cancel export of ${this.name} ${this.domainLabel(false)}`)
    },
    enterBulkAddMode() {
      this.curatedGroupStore.setMode('bulkAdd')
    },
    enterRenameMode() {
      this.renameInput = this.curatedGroupName
      useCuratedGroupStore().setMode('rename')
      this.putFocusNextTick('rename-input')
    },
    exitRenameMode() {
      this.renameInput = undefined
      useCuratedGroupStore().resetMode()
      this.putFocusNextTick('curated-group-name')
    },
    exportGroup(csvColumnsSelected) {
      this.showExportAdmitsModal = this.showExportStudentsModal = this.exportEnabled = false
      alertScreenReader(`Exporting ${this.name} ${this.domainLabel(false)}`)
      return downloadCuratedGroupCsv(this.curatedGroupId, this.curatedGroupName, csvColumnsSelected).then(() => {
        this.exportEnabled = true
        alertScreenReader('Export is done.')
      })
    },
    deleteGroup() {
      this.isDeleting = true
      return deleteCuratedGroup(this.domain, this.curatedGroupId).then(() => {
        this.isDeleteModalOpen = false
        this.$router.push({path: '/'}, this._noop)
      }).catch(error => {
        this.error = error
      }).finally(() => {
        this.isDeleting = false
      })
    },
    domainLabel(capitalize) {
      return describeCuratedGroupDomain(this.domain, capitalize)
    },
    getCsvExportColumns,
    getCsvExportColumnsSelected,
    onClickDelete() {
      const hasReferencingCohorts = !!this.referencingCohorts.length
      this.isCohortWarningModalOpen = hasReferencingCohorts
      this.isDeleteModalOpen = !hasReferencingCohorts
    },
    rename() {
      const error = validateCohortName({name: this.renameInput})
      if (error !== true) {
        this.renameError = error
        this.putFocusNextTick('rename-input')
      } else {
        this.isSaving = true
        renameCuratedGroup(this.curatedGroupId, this.renameInput).then(curatedGroup => {
          useCuratedGroupStore().setCuratedGroupName(curatedGroup.name)
          this.setPageTitle(curatedGroup.name)
          this.exitRenameMode()
          this.isSaving = false
          this.putFocusNextTick('curated-group-name')
        })
      }
    }
  }
}
</script>

<style scoped>
.modal-footer {
  border-top: none;
}
.modal-header {
  border-bottom: none;
}
:deep(.v-dialog > .v-overlay__content > .v-card > .v-card-text, .v-dialog > .v-overlay__content > form > .v-card > .v-card-text) {
  padding: 0px !important;
}
</style>
