<template>
  <div>
    <div class="d-flex justify-content-between mb-2">
      <div v-if="mode !== 'rename'">
        <h1
          id="curated-group-name"
          ref="pageHeader"
          class="page-section-header mt-0"
          tabindex="0">
          <span>{{ curatedGroupName || 'Curated Group' }}</span>
          <span v-if="!isNil(totalStudentCount)" class="faint-text"> (<span>{{ pluralize('student', totalStudentCount, {1: '1'}) }}</span>)</span>
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
              aria-label="Curated group name, 255 characters or fewer"
              aria-required="true"
              maxlength="255"
              required
              type="text"
              @keyup.esc="exitRenameMode" />
          </form>
        </div>
        <div v-if="renameError" class="has-error mb-2">{{ renameError }}</div>
        <div class="faint-text m-2">255 character limit <span v-if="size(renameInput)">({{ 255 - size(renameInput) }} left)</span></div>
        <div class="sr-only" aria-live="polite">{{ renameError }}</div>
        <div
          v-if="size(renameInput) === 255"
          class="sr-only"
          aria-live="polite">
          Name cannot exceed 255 characters.
        </div>
      </div>
      <div v-if="mode === 'rename'" class="d-flex align-self-baseline mr-4">
        <b-btn
          id="rename-confirm"
          :disabled="!size(renameInput)"
          class="btn-primary-color-override"
          variant="primary"
          size="sm"
          aria-label="Save changes to curated group name"
          @click.stop="rename">
          Rename
        </b-btn>
        <b-btn
          id="rename-cancel"
          class="cohort-manage-btn"
          variant="link"
          aria-label="Cancel rename curated group"
          size="sm"
          @click="exitRenameMode">
          Cancel
        </b-btn>
      </div>
      <div v-if="!mode" class="d-flex align-items-center mr-2">
        <div v-if="isOwnedByCurrentUser">
          <b-btn
            id="bulk-add-sids-button"
            variant="link"
            aria-label="Add students to this curated group by entering a list of student IDs"
            @click="enterBulkAddMode">
            Add Students
          </b-btn>
        </div>
        <div v-if="isOwnedByCurrentUser" class="faint-text">|</div>
        <div v-if="isOwnedByCurrentUser">
          <b-btn
            id="rename-button"
            variant="link"
            aria-label="Rename this curated group"
            @click="enterRenameMode">
            Rename
          </b-btn>
        </div>
        <div v-if="isOwnedByCurrentUser" class="faint-text">|</div>
        <div v-if="isOwnedByCurrentUser">
          <b-btn
            id="delete-button"
            v-b-modal="referencingCohorts.length ? 'cohort-warning-modal' : 'confirm-delete-modal'"
            variant="link"
            aria-label="Delete this curated group">
            Delete
          </b-btn>
          <b-modal
            id="confirm-delete-modal"
            v-model="isDeleteModalOpen">
            <div slot="modal-header">
              <h3>Delete Curated Group</h3>
            </div>
            <div id="confirm-delete-body" class="modal-body">
              Are you sure you want to delete "<strong>{{ curatedGroupName }}</strong>"?
            </div>
            <div slot="modal-footer">
              <b-btn
                id="delete-confirm"
                class="btn-primary-color-override"
                variant="primary"
                @click="deleteGroup">
                Delete
              </b-btn>
              <b-btn
                id="delete-cancel"
                variant="link"
                @click="isDeleteModalOpen = false">
                Cancel
              </b-btn>
            </div>
          </b-modal>
          <b-modal
            id="cohort-warning-modal"
            v-model="isCohortWarningModalOpen">
            <div slot="modal-header" class="ml-3 mt-3">
              <h3 class="font-size-24">This group is in use as a cohort filter</h3>
            </div>
            <div
              id="cohort-warning-body"
              class="modal-body"
              aria-live="polite"
              role="alert">
              Sorry, you cannot delete this curated group until you have removed the filter
              from
              <span v-if="referencingCohorts.length === 1">cohort <span class="font-weight-bolder">{{ referencingCohorts[0].name }}</span>.</span>
              <span v-if="referencingCohorts.length > 1">cohorts:</span>
              <ul v-if="referencingCohorts.length > 1" class="mb-0 mt-2">
                <li v-for="cohort in referencingCohorts" :key="cohort.id">
                  <span class="font-weight-bolder">{{ cohort.name }}</span>
                </li>
              </ul>
            </div>
            <div slot="modal-footer">
              <b-btn
                id="cohort-warning-modal-close"
                class="mb-1 mr-3"
                variant="link"
                @click="isCohortWarningModalOpen = false">
                Close
              </b-btn>
            </div>
          </b-modal>
        </div>
        <div v-if="isOwnedByCurrentUser" class="faint-text">|</div>
        <div>
          <b-btn
            id="export-student-list-button"
            v-b-modal="'export-list-modal'"
            :disabled="!exportEnabled || !totalStudentCount"
            variant="link"
            aria-label="Download CSV file containing all students">
            Export List
          </b-btn>
          <b-modal
            id="export-list-modal"
            v-model="showExportListModal"
            body-class="pl-0 pr-0"
            hide-footer
            hide-header
            @shown="focusModalById('export-list-confirm')">
            <ExportListModal
              :cancel-export-list-modal="cancelExportGroupModal"
              :csv-columns="getDefaultCsvExportColumns()"
              :csv-columns-selected="['first_name', 'last_name', 'sid', 'email', 'phone']"
              :export-list="exportGroup" />
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
        :to="`/cohort/${referencingCohorts[0].id}`">
        {{ referencingCohorts[0].name }}.
      </router-link>
      <span v-if="referencingCohorts.length > 1">
        <span v-for="(cohort, index) in referencingCohorts" :key="cohort.id">
          <span v-if="index === referencingCohorts.length - 1">and </span>
          <router-link
            :id="`referencing-cohort-${index}`"
            aria-label="Link to cohort"
            :to="`/cohort/${cohort.id}`">{{ cohort.name }}</router-link>{{ index === referencingCohorts.length - 1 ? '.' : (referencingCohorts.length > 2 ? ',' : '') }}
        </span>
      </span>
    </div>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import CuratedEditSession from '@/mixins/CuratedEditSession'
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import ExportListModal from '@/components/util/ExportListModal'
import router from '@/router'
import Util from '@/mixins/Util'
import Validator from '@/mixins/Validator.vue'
import { deleteCuratedGroup, downloadCuratedGroupCsv } from '@/api/curated'

export default {
  name: 'CuratedGroupHeader',
  components: { ExportListModal },
  mixins: [Berkeley, Context, CuratedEditSession, CurrentUserExtras, Util, Validator],
  data: () => ({
    exportEnabled: true,
    isCohortWarningModalOpen: false,
    isDeleteModalOpen: false,
    referencingCohorts: [],
    renameError: undefined,
    renameInput: undefined,
    showExportListModal: false
  }),
  computed: {
    isOwnedByCurrentUser() {
      return this.ownerId === this.$currentUser.id
    }
  },
  watch: {
    renameInput() {
      this.renameError = undefined
    }
  },
  mounted() {
    if (this.referencingCohortIds.length) {
      this.each(this.referencingCohortIds, cohortId => {
        const cohort = this.find(this.myCohorts, ['id', cohortId])
        this.referencingCohorts.push(cohort)
      })
      this.referencingCohorts = this.$_.sortBy(this.referencingCohorts, ['name'])
    }
    this.putFocusNextTick('curated-group-name')
  },
  methods: {
    cancelExportGroupModal() {
      this.showExportListModal = false
      this.alertScreenReader(`Cancel export of ${this.name} curated group`)
    },
    enterBulkAddMode() {
      this.setMode('bulkAdd')
    },
    enterRenameMode() {
      this.renameInput = this.curatedGroupName
      this.setMode('rename')
      this.putFocusNextTick('rename-input')
    },
    exitRenameMode() {
      this.renameInput = undefined
      this.setMode(undefined)
      this.putFocusNextTick('curated-group-name')
    },
    deleteGroup() {
      deleteCuratedGroup(this.curatedGroupId)
        .then(() => {
          this.isDeleteModalOpen = false
          router.push({ path: '/home' })
        })
        .catch(error => {
          this.error = error
        })
    },
    exportGroup(csvColumnsSelected) {
      this.showExportListModal = false
      this.exportEnabled = false
      this.alertScreenReader(`Exporting ${this.name} curated group`)
      downloadCuratedGroupCsv(this.curatedGroupId, this.curatedGroupName, csvColumnsSelected).then(() => {
        this.exportEnabled = true
      })
    },
    rename() {
      this.renameError = this.validateCohortName({
        name: this.renameInput
      })
      if (this.renameError) {
        this.putFocusNextTick('rename-input')
      } else {
        this.renameCuratedGroup(this.renameInput).then(() => {
          this.setPageTitle(this.renameInput)
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
</style>
