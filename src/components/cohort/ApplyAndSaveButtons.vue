<template>
  <div>
    <b-btn
      v-if="showApplyButton"
      id="unsaved-filter-apply"
      :disabled="!!editMode"
      class="btn-filter-draft btn-primary-color-override"
      variant="primary"
      @click="apply"
    >
      Apply
    </b-btn>
    <b-btn
      v-if="showApplyButton"
      id="unsaved-filter-reset"
      :disabled="!!editMode"
      class="btn-filter-draft"
      @click="resetToLastApply"
    >
      Reset
    </b-btn>
    <div v-if="showSaveButton && isPerforming !== 'search'">
      <b-btn
        id="save-button"
        :class="{'btn-primary-color-override': isPerforming !== 'acknowledgeSave'}"
        :variant="saveButtonVariant"
        :disabled="!!editMode || showCreateModal || !!isPerforming"
        class="btn-filter-draft save-button-width mt-3"
        @click="save"
      >
        <span v-if="isPerforming === 'acknowledgeSave'">Saved</span>
        <span v-if="isPerforming === 'save'"><font-awesome icon="spinner" spin /> Saving</span>
        <span v-if="!isPerforming && cohortId">Save Cohort</span>
        <span v-if="!isPerforming && !cohortId">Save</span>
      </b-btn>
      <b-btn
        v-if="!isPerforming && cohortId"
        id="reset-to-saved-cohort"
        :disabled="!!editMode"
        class="btn-filter-draft"
        @click="resetToSaved"
      >
        Reset
      </b-btn>
      <b-modal
        v-model="showCreateModal"
        body-class="pl-0 pr-0"
        hide-footer
        hide-header
        @shown="putFocusNextTick('modal-header')"
      >
        <CreateCohortModal :cancel="cancelCreateModal" :create="create" />
      </b-modal>
    </div>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession'
import Context from '@/mixins/Context'
import CreateCohortModal from '@/components/cohort/CreateCohortModal'
import store from '@/store'
import Util from '@/mixins/Util'
import {applyFilters, loadCohort, resetFiltersToLastApply} from '@/store/modules/cohort-edit-session/utils'
import {createCohort, saveCohort} from '@/api/cohort'

export default {
  name: 'ApplyAndSaveButtons',
  components: {CreateCohortModal},
  mixins: [CohortEditSession, Context, Util],
  data: () => ({
    isPerforming: undefined,
    showCreateModal: false
  }),
  computed: {
    saveButtonVariant() {
      return this.isPerforming === 'acknowledgeSave' ? 'success' : 'primary'
    }
  },
  methods: {
    apply() {
      this.broadcast('cohort-apply-filters')
      this.isPerforming = 'search'
      this.alertScreenReader('Searching for students')
      this.setModifiedSinceLastSearch(false)
      const orderBy = this._get(
        this.currentUser.preferences,
        this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
      )
      const termId = this._get(this.currentUser.preferences, 'termId')
      applyFilters(orderBy, termId).then(() => {
        this.putFocusNextTick('cohort-results-header')
        this.alertScreenReader(`Results include ${this.totalStudentCount} student${this.totalStudentCount === 1 ? '' : 's'}`)
        this.isPerforming = null
      })
    },
    cancelCreateModal() {
      this.alertScreenReader('Canceled')
      this.showCreateModal = false
    },
    create(name) {
      this.showCreateModal = false
      this.isPerforming = 'save'
      this.alertScreenReader('Creating cohort')
      createCohort(this.domain, name, this.filters).then(cohort => {
        store.commit('cohort/updateSession', {
          cohort,
          filters: this.filters,
          students: this.students,
          totalStudentCount: cohort.totalStudentCount
        })
        store.commit('cohort/stashOriginalFilters')
        store.commit('cohort/setModifiedSinceLastSearch', null)
        this.savedCohortCallback(`Cohort "${name}" created`)
        this.setPageTitle(this.cohortName)
        history.pushState({}, null, `/cohort/${this.cohortId}`)
        this.isPerforming = null
      })
    },
    resetToLastApply() {
      this.alertScreenReader('Resetting filters')
      resetFiltersToLastApply()
    },
    resetToSaved() {
      this.isPerforming = 'search'
      this.setCurrentPage(0)
      this.setModifiedSinceLastSearch(null)
      this.setEditMode('apply')
      loadCohort(this.cohortId, this.orderBy, this.termId).then(() => {
        this.setEditMode(null)
        this.alertScreenReader('Filters reset')
        this.isPerforming = null
      })
    },
    save() {
      if (this.cohortId) {
        this.alertScreenReader(`Saving changes to cohort ${this.cohortName}`)
        this.isPerforming = 'save'
        saveCohort(this.cohortId, this.cohortName, this.filters).then(() => {
          this.setModifiedSinceLastSearch(null)
          this.savedCohortCallback(`Cohort "${this.cohortName}" saved`)
        })
      } else {
        this.showCreateModal = true
        this.alertScreenReader('Create cohort form is open')
      }
    },
    savedCohortCallback(updateStatus) {
      this.alertScreenReader(updateStatus)
      this.isPerforming = 'acknowledgeSave'
      setTimeout(() => (this.isPerforming = null), 2000)
    }
  }
}
</script>

<style scoped>
.btn-filter-draft {
  height: 40px;
  margin: 15px 8px 0 0;
  width: 80px;
}
.save-button-width {
  min-width: 120px;
  width: 120px;
}
</style>
