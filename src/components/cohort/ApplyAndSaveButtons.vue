<template>
  <div class="pt-4">
    <ProgressButton
      v-if="cohort.showApplyButton()"
      id="unsaved-filter-apply"
      :action="apply"
      :disabled="!!cohort.editMode"
      :in-progress="isPerforming === 'search'"
    >
      Apply
    </ProgressButton>
    <v-btn
      v-if="cohort.showApplyButton()"
      id="unsaved-filter-reset"
      class="ml-1"
      :disabled="!!cohort.editMode"
      variant="text"
      @click="resetToLastApply"
    >
      Reset
    </v-btn>
    <div v-if="isPerforming !== 'search' && !cohort.showApplyButton">
      <ProgressButton
        id="save-button"
        :action="save"
        :color="isPerforming === 'acknowledgeSave' ? 'success' : 'primary'"
        :disabled="!!cohort.editMode || showCreateModal || !!isPerforming"
        :in-progress="isPerforming === 'save'"
      >
        <span v-if="isPerforming === 'acknowledgeSave'">Saved</span>
        <span v-if="isPerforming === 'save'">Saving</span>
        <span v-if="!isPerforming && cohort.cohortId">Save Cohort</span>
        <span v-if="!isPerforming && !cohort.cohortId">Save</span>
      </ProgressButton>
      <v-btn
        v-if="!isPerforming && cohort.cohortId"
        id="reset-to-saved-cohort"
        class="ml-1"
        :disabled="!!cohort.editMode"
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
import CreateCohortModal from '@/components/cohort/CreateCohortModal'
import ProgressButton from '@/components/util/ProgressButton'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {applyFilters, loadCohort, resetFiltersToLastApply} from '@/stores/cohort-edit-session/utils'
import {createCohort, saveCohort} from '@/api/cohort'
import {get, map} from 'lodash'
import {putFocusNextTick, setPageTitle} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useRouter} from 'vue-router'

const cohort = useCohortStore()
const context = useContextStore()
let isPerforming = false
let showCreateModal = false

const apply = () => {
  context.broadcast('cohort-apply-filters')
  isPerforming = 'search'
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
    isPerforming = null
  })
}

const cancelCreateModal = () => {
  context.alertScreenReader('Canceled')
  showCreateModal = false
}

const create = name => {
  showCreateModal = false
  isPerforming = 'save'
  context.alertScreenReader('Creating cohort')
  return createCohort(cohort.domain, name, map(cohort.filters, 'value')).then(async data => {
    if (data) {
      cohort.updateSession(data, cohort.filters, cohort.students, cohort.totalStudentCount)
      cohort.stashOriginalFilters()
      cohort.setModifiedSinceLastSearch(null)
      savedCohortCallback(`Cohort "${cohort.cohortName}" created`)
      setPageTitle(cohort.cohortName)
      await useRouter().push(`/cohort/${cohort.cohortId}`)
      window.history.replaceState({...window.history.state, ...{}}, null)
      isPerforming = null
    }
  })
}

const resetToLastApply = () => {
  context.alertScreenReader('Resetting filters')
  resetFiltersToLastApply()
}

const resetToSaved = () => {
  isPerforming = 'search'
  cohort.setCurrentPage(0)
  cohort.setModifiedSinceLastSearch(null)
  cohort.setEditMode('apply')
  loadCohort(cohort.cohortId, cohort.orderBy, cohort.termId).then(() => {
    cohort.setEditMode(null)
    context.alertScreenReader('Filters reset')
    isPerforming = null
  })
}

const save = () => {
  if (cohort.cohortId) {
    context.alertScreenReader(`Saving changes to cohort ${cohort.cohortName}`)
    isPerforming = 'save'
    saveCohort(cohort.cohortId, cohort.cohortName, map(cohort.filters, 'value')).then(() => {
      cohort.setModifiedSinceLastSearch(null)
      savedCohortCallback(`Cohort "${cohort.cohortName}" saved`)
    })
  } else {
    showCreateModal = true
    context.alertScreenReader('Create cohort form is open')
  }
}

const savedCohortCallback = updateStatus => {
  context.alertScreenReader(updateStatus)
  isPerforming = 'acknowledgeSave'
  setTimeout(() => (isPerforming = null), 2000)
}
</script>
