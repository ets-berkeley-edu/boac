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
      <div v-if="mode === 'rename'" class="w-100 mr-3">
        <v-text-field
          id="rename-input"
          v-model="renameInput"
          :aria-invalid="!renameInput"
          :aria-label="`${domainLabel(true)} name, 255 characters or fewer`"
          :aria-required="true"
          class="v-input-details-override mr-3"
          counter="255"
          density="comfortable"
          :disabled="isSaving"
          maxlength="255"
          persistent-counter
          required
          type="text"
          @keyup.enter="rename"
          @keyup.esc="exitRenameMode"
        />
        <div v-if="renameError" class="text-error mb-2">{{ renameError }}</div>
        <div class="text-grey ma-2">255 character limit <span v-if="_size(renameInput)">({{ 255 - _size(renameInput) }} left)</span></div>
        <div class="sr-only" aria-live="polite">{{ renameError }}</div>
        <div
          v-if="_size(renameInput) === 255"
          class="sr-only"
          aria-live="polite"
        >
          Name cannot exceed 255 characters.
        </div>
      </div>
      <div v-if="mode === 'rename'" class="d-flex align-self-baseline mr-2">
        <v-btn
          id="rename-confirm"
          class="font-size-15 px-1 text-no-wrap"
          color="primary"
          :disabled="!_size(renameInput)"
          size="large"
          text="Rename"
          @click="rename"
        />
        <v-btn
          id="rename-cancel"
          :disabled="isSaving"
          size="large"
          text="Cancel"
          variant="plain"
          @click="exitRenameMode"
        />
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
            @click="() => {
              const hasReferencingCohorts = !!referencingCohorts.length
              isCohortWarningModalOpen = hasReferencingCohorts
              isDeleteModalOpen = !hasReferencingCohorts
            }"
          />
          <AreYouSureModal
            :show-modal="isDeleteModalOpen"
            :function-confirm="deleteGroup"
            function-cancel="() => isDeleteModalOpen = false"
          />
          <!--
          <b-modal
            id="confirm-delete-modal"
            v-model="isDeleteModalOpen"
            hide-header
            @shown="putFocusNextTick('modal-header')"
          >
            <ModalHeader :text="`Delete ${domainLabel(true)}`" />
            <div class="modal-body">
              Are you sure you want to delete "<strong>{{ curatedGroupName }}</strong>"?
            </div>
            <template #modal-footer>
              <v-btn
                id="delete-confirm"
                class="btn-primary-color-override"
                variant="primary"
                @click="deleteGroup"
              >
                Delete
              </v-btn>
              <v-btn
                id="delete-cancel"
                variant="link"
                @click="isDeleteModalOpen = false"
              >
                Cancel
              </v-btn>
            </template>
          </b-modal>
          -->
          <v-overlay
            v-model="isCohortWarningModalOpen"
            persistent
            width="100%"
          >
            <v-card
              class="modal-content"
              min-width="400"
              max-width="600"
            >
              <ModalHeader text="This group is in use as a cohort filter" />
              <div
                id="cohort-warning-body"
                aria-live="polite"
                role="alert"
              >
                Sorry, you cannot delete this {{ domainLabel(false) }} until you have removed the filter from
                <span v-if="referencingCohorts.length === 1">cohort <span class="font-weight-700">{{ referencingCohorts[0].name }}</span>.</span>
                <span v-if="referencingCohorts.length > 1">cohorts:</span>
                <ul v-if="referencingCohorts.length > 1" class="mb-0 mt-2">
                  <li v-for="cohort in referencingCohorts" :key="cohort.id">
                    <span class="font-weight-700">{{ cohort.name }}</span>
                  </li>
                </ul>
              </div>
              <hr />
              <div class="d-flex justify-end py-3 px-4">
                <v-btn
                  id="cohort-warning-modal-close"
                  @click="isCohortWarningModalOpen = false"
                >
                  Close
                </v-btn>
              </div>
            </v-card>
          </v-overlay>
        </div>
        <div v-if="isOwnedByCurrentUser" class="text-grey">|</div>
        <div>
          <v-btn
            v-if="domain === 'default'"
            id="export-student-list-button"
            class="px-1"
            :disabled="!exportEnabled || !totalStudentCount"
            text="Export List"
            variant="text"
            @click="() => showExportStudentsModal = true"
          />
          <v-btn
            v-if="domain === 'admitted_students'"
            id="export-student-list-button"
            v-b-modal="'export-admits-modal'"
            class="px-1"
            :disabled="!exportEnabled || !totalStudentCount"
            text="Export List"
            variant="text"
            @click="() => showExportAdmitsModal = true"
          />
          <b-modal
            id="export-admits-modal"
            v-model="showExportAdmitsModal"
            body-class="pl-0 pr-0"
            hide-footer
            hide-header
            @shown="putFocusNextTick('modal-header')"
          >
            <FerpaReminderModal
              :cancel="cancelExportModal"
              :confirm="() => exportGroup(getCsvExportColumnsSelected(domain))"
            />
          </b-modal>
          <b-modal
            id="export-students-modal"
            v-model="showExportStudentsModal"
            body-class="pl-0 pr-0"
            hide-footer
            hide-header
            @shown="putFocusNextTick('modal-header')"
          >
            <ExportListModal
              :cancel="cancelExportModal"
              :csv-columns="getCsvExportColumns(domain)"
              :csv-columns-selected="getCsvExportColumnsSelected(domain)"
              :export="exportGroup"
            />
          </b-modal>
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
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Context from '@/mixins/Context'
import CuratedEditSession from '@/mixins/CuratedEditSession'
import ExportListModal from '@/components/util/ExportListModal'
import FerpaReminderModal from '@/components/util/FerpaReminderModal'
import ModalHeader from '@/components/util/ModalHeader'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
import {deleteCuratedGroup, downloadCuratedGroupCsv, renameCuratedGroup} from '@/api/curated'
import {describeCuratedGroupDomain, getCsvExportColumns, getCsvExportColumnsSelected} from '@/berkeley'
import {useCuratedGroupStore} from '@/stores/curated-group'
import {validateCohortName} from '@/lib/cohort'

export default {
  name: 'CuratedGroupHeader',
  components: {AreYouSureModal, ExportListModal, FerpaReminderModal, ModalHeader},
  mixins: [Context, CuratedEditSession, Util],
  data: () => ({
    exportEnabled: true,
    isCohortWarningModalOpen: false,
    isDeleteModalOpen: false,
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
    if (this.referencingCohortIds.length) {
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
      useCuratedGroupStore().setMode('bulkAdd')
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
      downloadCuratedGroupCsv(this.curatedGroupId, this.curatedGroupName, csvColumnsSelected).then(() => {
        this.exportEnabled = true
        alertScreenReader('Export is done.')
      })
    },
    deleteGroup() {
      deleteCuratedGroup(this.domain, this.curatedGroupId).then(
        () => {
          this.isDeleteModalOpen = false
          this.$router.push({path: '/'}, this._noop)
        })
        .catch(error => {
          this.error = error
        })
    },
    domainLabel(capitalize) {
      return describeCuratedGroupDomain(this.domain, capitalize)
    },
    getCsvExportColumns,
    getCsvExportColumnsSelected,
    rename() {
      this.renameError = validateCohortName({
        name: this.renameInput
      })
      if (this.renameError) {
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
</style>
