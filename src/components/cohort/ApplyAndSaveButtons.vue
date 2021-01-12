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
        id="create-cohort"
        v-model="showCreateModal"
        body-class="pl-0 pr-0"
        hide-footer
        hide-header-close
        title="Name Your Cohort"
        @shown="focusModalById('create-input')"
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
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import Util from '@/mixins/Util'

export default {
  name: 'ApplyAndSaveButtons',
  components: { CreateCohortModal },
  mixins: [CohortEditSession, Context, CurrentUserExtras, Util],
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
      this.$eventHub.emit('cohort-apply-filters')
      this.isPerforming = 'search'
      this.alertScreenReader('Searching for students')
      this.applyFilters(this.$_.get(this.preferences, this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy')).then(() => {
        this.putFocusNextTick('cohort-results-header')
        this.alertScreenReader(`Results include ${this.totalStudentCount} student${this.totalStudentCount === 1 ? '' : 's'}`)
        this.$ga.cohortEvent(this.cohortId, this.cohortName || '', 'search')
        this.isPerforming = null
      })
    },
    cancelCreateModal() {
      this.alertScreenReader('Cancelled')
      this.showCreateModal = false
    },
    create(name) {
      this.showCreateModal = false
      this.isPerforming = 'save'
      this.alertScreenReader('Creating cohort')
      this.createCohort(name).then(() => {
        this.savedCohortCallback(`Cohort "${name}" created`)
        this.setPageTitle(this.cohortName)
        this.$ga.cohortEvent(this.cohortId, name, 'create')
        history.pushState({}, null, `/cohort/${this.cohortId}`)
        this.isPerforming = null
      })
    },
    resetToLastApply() {
      this.alertScreenReader('Resetting filters')
      this.resetFiltersToLastApply()
    },
    resetToSaved() {
      this.isPerforming = 'search'
      this.resetFiltersToSaved(this.cohortId).then(() => {
        this.alertScreenReader('Filters reset')
        this.isPerforming = null
      })
    },
    save() {
      if (this.cohortId) {
        this.alertScreenReader(`Saving changes to cohort ${this.cohortName}`)
        this.isPerforming = 'save'
        this.saveExistingCohort().then(() => {
          this.$ga.cohortEvent(this.cohortId, this.cohortName, 'save')
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
