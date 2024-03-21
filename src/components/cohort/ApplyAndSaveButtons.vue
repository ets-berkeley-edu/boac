<template>
  <div class="pt-4">
    <v-btn
      v-if="useCohortStore().showApplyButton()"
      id="unsaved-filter-apply"
      :disabled="!!useCohortStore().editMode"
      class="mr-2"
      color="primary"
      @click="apply"
    >
      Apply
    </v-btn>
    <v-btn
      v-if="useCohortStore().showApplyButton()"
      id="unsaved-filter-reset"
      :disabled="!!useCohortStore().editMode"
      variant="text"
      @click="resetToLastApply"
    >
      Reset
    </v-btn>
    <div v-if="isPerforming !== 'search'">
      <v-btn
        id="save-button"
        class="mr-2"
        :color="saveButtonColor"
        :disabled="!!useCohortStore().editMode || showCreateModal || !!isPerforming"
        @click="save"
      >
        <span v-if="isPerforming === 'acknowledgeSave'">Saved</span>
        <span v-if="isPerforming === 'save'"><v-progress-circular size="small" /> Saving</span>
        <span v-if="!isPerforming && useCohortStore().cohortId">Save Cohort</span>
        <span v-if="!isPerforming && !useCohortStore().cohortId">Save</span>
      </v-btn>
      <v-btn
        v-if="!isPerforming && useCohortStore().cohortId"
        id="reset-to-saved-cohort"
        :disabled="!!useCohortStore().editMode"
        variant="text"
        @click="resetToSaved"
      >
        Reset
      </v-btn>
      <CreateCohortModal
        :cancel="cancelCreateModal"
        :create="create"
        :show-modal="showCreateModal"
      />
    </div>
  </div>
</template>

<script setup>
import {get} from 'lodash'
import {putFocusNextTick} from '@/lib/utils'
</script>

<script>
import CreateCohortModal from '@/components/cohort/CreateCohortModal'
import {applyFilters, loadCohort, resetFiltersToLastApply} from '@/stores/cohort-edit-session/utils'
import {createCohort, saveCohort} from '@/api/cohort'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {useContextStore} from '@/stores/context'
import {useRouter} from 'vue-router'

export default {
  name: 'ApplyAndSaveButtons',
  components: {CreateCohortModal},
  data: () => ({
    isPerforming: undefined,
    showCreateModal: false
  }),
  computed: {
    saveButtonColor() {
      return this.isPerforming === 'acknowledgeSave' ? 'success' : 'primary'
    }
  },
  methods: {
    apply() {
      const cohort = useCohortStore()
      const context = useContextStore()
      context.broadcast('cohort-apply-filters')
      this.isPerforming = 'search'
      context.alertScreenReader('Searching for students')
      cohort.setModifiedSinceLastSearch(false)
      const orderBy = get(
        context.currentUser.preferences,
        cohort.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
      )
      const termId = get(context.currentUser.preferences, 'termId')
      applyFilters(orderBy, termId).then(() => {
        putFocusNextTick('cohort-results-header')
        context.alertScreenReader(`Results include ${cohort.totalStudentCount} student${cohort.totalStudentCount === 1 ? '' : 's'}`)
        this.isPerforming = null
      })
    },
    cancelCreateModal() {
      useContextStore().alertScreenReader('Canceled')
      this.showCreateModal = false
    },
    create(name) {
      const cohortStore = useCohortStore()
      const context = useContextStore()
      this.showCreateModal = false
      this.isPerforming = 'save'
      context.alertScreenReader('Creating cohort')
      return createCohort(cohortStore.domain, name, cohortStore.filters).then(async cohort => {
        if (cohort) {
          cohortStore.updateSession(cohort, cohortStore.filters, cohortStore.students, cohort.totalStudentCount)
          cohortStore.stashOriginalFilters()
          cohortStore.setModifiedSinceLastSearch(null)
          this.savedCohortCallback(`Cohort "${cohortStore.cohortName}" created`)
          context.setPageTitle(cohortStore.cohortName)
          await useRouter().push(`/cohort/${cohortStore.cohortId}`)
          window.history.replaceState({...window.history.state, ...{}}, null)
          this.isPerforming = null
        }
      })
    },
    resetToLastApply() {
      useContextStore().alertScreenReader('Resetting filters')
      resetFiltersToLastApply()
    },
    resetToSaved() {
      const cohort = useCohortStore()
      this.isPerforming = 'search'
      cohort.setCurrentPage(0)
      cohort.setModifiedSinceLastSearch(null)
      cohort.setEditMode('apply')
      loadCohort(cohort.cohortId, cohort.orderBy, cohort.termId).then(() => {
        cohort.setEditMode(null)
        useContextStore().alertScreenReader('Filters reset')
        this.isPerforming = null
      })
    },
    save() {
      const cohort = useCohortStore()
      if (cohort.cohortId) {
        useContextStore().alertScreenReader(`Saving changes to cohort ${cohort.cohortName}`)
        this.isPerforming = 'save'
        saveCohort(cohort.cohortId, cohort.cohortName, cohort.filters).then(() => {
          cohort.setModifiedSinceLastSearch(null)
          this.savedCohortCallback(`Cohort "${cohort.cohortName}" saved`)
        })
      } else {
        this.showCreateModal = true
        useContextStore().alertScreenReader('Create cohort form is open')
      }
    },
    savedCohortCallback(updateStatus) {
      useContextStore().alertScreenReader(updateStatus)
      this.isPerforming = 'acknowledgeSave'
      setTimeout(() => (this.isPerforming = null), 2000)
    }
  }
}
</script>
