<template>
  <div class="pt-4">
    <ProgressButton
      v-if="useCohortStore().showApplyButton()"
      id="unsaved-filter-apply"
      :action="apply"
      class="mr-2"
      :disabled="!!useCohortStore().editMode"
      :in-progress="isPerforming === 'search'"
    >
      Apply
    </ProgressButton>
    <v-btn
      v-if="useCohortStore().showApplyButton()"
      id="unsaved-filter-reset"
      :disabled="!!useCohortStore().editMode"
      variant="text"
      @click="resetToLastApply"
    >
      Reset
    </v-btn>
    <div v-if="isPerforming !== 'search' && !useCohortStore().showApplyButton()">
      <ProgressButton
        id="save-button"
        :action="save"
        class="mr-2"
        :color="saveButtonColor"
        :disabled="!!useCohortStore().editMode || showCreateModal || !!isPerforming"
        :in-progress="isPerforming === 'save'"
      >
        <span v-if="isPerforming === 'acknowledgeSave'">Saved</span>
        <span v-if="isPerforming === 'save'">Saving</span>
        <span v-if="!isPerforming && useCohortStore().cohortId">Save Cohort</span>
        <span v-if="!isPerforming && !useCohortStore().cohortId">Save</span>
      </ProgressButton>
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
import {get, map} from 'lodash'
</script>

<script>
import CreateCohortModal from '@/components/cohort/CreateCohortModal'
import ProgressButton from '@/components/util/ProgressButton'
import {applyFilters, loadCohort, resetFiltersToLastApply} from '@/stores/cohort-edit-session/utils'
import {createCohort, saveCohort} from '@/api/cohort'
import {putFocusNextTick, setPageTitle} from '@/lib/utils'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {useContextStore} from '@/stores/context'
import {useRouter} from 'vue-router'

export default {
  name: 'ApplyAndSaveButtons',
  components: {CreateCohortModal, ProgressButton},
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
      const orderBy = get(
        context.currentUser.preferences,
        cohort.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
      )
      const termId = get(context.currentUser.preferences, 'termId')
      applyFilters(orderBy, termId).then(() => {
        putFocusNextTick('cohort-results-header')
        context.alertScreenReader(`Results include ${cohort.totalStudentCount} student${cohort.totalStudentCount === 1 ? '' : 's'}`)
        cohort.setModifiedSinceLastSearch(false)
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
      return createCohort(cohortStore.domain, name, map(cohortStore.filters, 'value')).then(async cohort => {
        if (cohort) {
          cohortStore.updateSession(cohort, cohortStore.filters, cohortStore.students, cohort.totalStudentCount)
          cohortStore.stashOriginalFilters()
          cohortStore.setModifiedSinceLastSearch(null)
          this.savedCohortCallback(`Cohort "${cohortStore.cohortName}" created`)
          setPageTitle(cohortStore.cohortName)
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
        saveCohort(cohort.cohortId, cohort.cohortName, map(cohort.filters, 'value')).then(() => {
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
