<template>
  <div>
    <div class="d-flex flex-wrap justify-content-between">
      <div v-if="mode !== 'rename'">
        <h1 id="curated-group-name" class="page-section-header mb-0 mt-0">
          {{ curatedGroupName || domainLabel(true) }}
          <span v-if="!_isNil(totalStudentCount)" class="faint-text">
            ({{ pluralize(domain === 'admitted_students' ? 'admit' : 'student', totalStudentCount, {1: '1'}) }})
          </span>
        </h1>
      </div>
      <div v-if="mode === 'rename'" class="w-100 mr-3">
        <div>
          <form @submit.prevent="rename">
            <input
              id="rename-input"
              v-model="renameInput"
              :aria-invalid="!renameInput"
              class="form-control"
              :aria-label="`${domainLabel(true)} name, 255 characters or fewer`"
              aria-required="true"
              maxlength="255"
              required
              type="text"
              @keyup.esc="exitRenameMode"
            />
          </form>
        </div>
        <div v-if="renameError" class="has-error mb-2">{{ renameError }}</div>
        <div class="faint-text m-2">255 character limit <span v-if="_size(renameInput)">({{ 255 - _size(renameInput) }} left)</span></div>
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
        <b-btn
          id="rename-confirm"
          :disabled="!_size(renameInput)"
          class="btn-primary-color-override rename-btn"
          size="sm"
          variant="primary"
          @click.stop="rename"
        >
          Rename
        </b-btn>
        <b-btn
          id="rename-cancel"
          class="rename-btn"
          size="sm"
          variant="link"
          @click="exitRenameMode"
        >
          Cancel
        </b-btn>
      </div>
      <div v-if="!mode" class="d-flex align-items-center">
        <div v-if="isOwnedByCurrentUser">
          <b-btn
            id="bulk-add-sids-button"
            class="px-1"
            variant="link"
            @click="enterBulkAddMode"
          >
            Add {{ domain === 'admitted_students' ? 'Admits' : 'Students' }}
          </b-btn>
        </div>
        <div v-if="isOwnedByCurrentUser" class="faint-text">|</div>
        <div v-if="isOwnedByCurrentUser">
          <b-btn
            id="rename-button"
            class="px-1"
            variant="link"
            @click="enterRenameMode"
          >
            Rename
          </b-btn>
        </div>
        <div v-if="isOwnedByCurrentUser" class="faint-text">|</div>
        <div v-if="isOwnedByCurrentUser">
          <b-btn
            id="delete-button"
            v-b-modal="referencingCohorts.length ? 'cohort-warning-modal' : 'confirm-delete-modal'"
            class="px-1"
            variant="link"
          >
            Delete
          </b-btn>
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
              <b-btn
                id="delete-confirm"
                class="btn-primary-color-override"
                variant="primary"
                @click="deleteGroup"
              >
                Delete
              </b-btn>
              <b-btn
                id="delete-cancel"
                variant="link"
                @click="isDeleteModalOpen = false"
              >
                Cancel
              </b-btn>
            </template>
          </b-modal>
          <b-modal
            id="cohort-warning-modal"
            v-model="isCohortWarningModalOpen"
            hide-header
            @shown="putFocusNextTick('modal-header')"
          >
            <ModalHeader text="This group is in use as a cohort filter" />
            <div
              id="cohort-warning-body"
              class="modal-body pt-0"
              aria-live="polite"
              role="alert"
            >
              Sorry, you cannot delete this {{ domainLabel(false) }} until you have removed the filter
              from
              <span v-if="referencingCohorts.length === 1">cohort <span class="font-weight-bolder">{{ referencingCohorts[0].name }}</span>.</span>
              <span v-if="referencingCohorts.length > 1">cohorts:</span>
              <ul v-if="referencingCohorts.length > 1" class="mb-0 mt-2">
                <li v-for="cohort in referencingCohorts" :key="cohort.id">
                  <span class="font-weight-bolder">{{ cohort.name }}</span>
                </li>
              </ul>
            </div>
            <template #modal-footer>
              <b-btn
                id="cohort-warning-modal-close"
                class="mb-1 mr-3"
                variant="link"
                @click="isCohortWarningModalOpen = false"
              >
                Close
              </b-btn>
            </template>
          </b-modal>
        </div>
        <div v-if="isOwnedByCurrentUser" class="faint-text">|</div>
        <div>
          <b-btn
            v-if="domain === 'default'"
            id="export-student-list-button"
            v-b-modal="'export-students-modal'"
            class="px-1"
            :disabled="!exportEnabled || !totalStudentCount"
            variant="link"
          >
            Export List
          </b-btn>
          <b-btn
            v-if="domain === 'admitted_students'"
            id="export-student-list-button"
            v-b-modal="'export-admits-modal'"
            class="px-1"
            :disabled="!exportEnabled || !totalStudentCount"
            variant="link"
          >
            Export List
          </b-btn>
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
import Context from '@/mixins/Context'
import CuratedEditSession from '@/mixins/CuratedEditSession'
import ExportListModal from '@/components/util/ExportListModal'
import FerpaReminderModal from '@/components/util/FerpaReminderModal'
import ModalHeader from '@/components/util/ModalHeader'
import store from '@/store'
import Util from '@/mixins/Util'
import Validator from '@/mixins/Validator.vue'
import {deleteCuratedGroup, downloadCuratedGroupCsv, renameCuratedGroup} from '@/api/curated'
import {describeCuratedGroupDomain, getCsvExportColumns, getCsvExportColumnsSelected} from '@/berkeley'

export default {
  name: 'CuratedGroupHeader',
  components: {ExportListModal, FerpaReminderModal, ModalHeader},
  mixins: [Context, CuratedEditSession, Util, Validator],
  data: () => ({
    exportEnabled: true,
    isCohortWarningModalOpen: false,
    isDeleteModalOpen: false,
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
      this.$announcer.polite(`Cancel export of ${this.name} ${this.domainLabel(false)}`)
    },
    enterBulkAddMode() {
      store.commit('curatedGroup/setMode', 'bulkAdd')
    },
    enterRenameMode() {
      this.renameInput = this.curatedGroupName
      store.commit('curatedGroup/setMode', 'rename')
      this.putFocusNextTick('rename-input')
    },
    exitRenameMode() {
      this.renameInput = undefined
      store.commit('curatedGroup/resetMode')
      this.putFocusNextTick('curated-group-name')
    },
    exportGroup(csvColumnsSelected) {
      this.showExportAdmitsModal = this.showExportStudentsModal = this.exportEnabled = false
      this.$announcer.polite(`Exporting ${this.name} ${this.domainLabel(false)}`)
      downloadCuratedGroupCsv(this.curatedGroupId, this.curatedGroupName, csvColumnsSelected).then(() => {
        this.exportEnabled = true
        this.$announcer.polite('Export is done.')
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
      this.renameError = this.validateCohortName({
        name: this.renameInput
      })
      if (this.renameError) {
        this.putFocusNextTick('rename-input')
      } else {
        renameCuratedGroup(this.curatedGroupId, this.renameInput).then(curatedGroup => {
          store.commit('curatedGroup/setCuratedGroupName', curatedGroup.name)
          this.setPageTitle(curatedGroup.name)
          this.exitRenameMode()
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
.rename-btn {
  height: 38px;
}
</style>
