<template>
  <div class="pt-4">
    <ProgressButton
      v-if="cohort.showApplyButton"
      id="unsaved-filter-apply"
      :action="apply"
      :disabled="!!cohort.editMode"
      :in-progress="currentAction === 'search'"
    >
      Apply
    </ProgressButton>
    <v-btn
      v-if="cohort.showApplyButton"
      id="unsaved-filter-reset"
      :disabled="!!cohort.editMode"
      variant="text"
      @click="resetToLastApply"
    >
      Reset
    </v-btn>
    <div v-if="cohort.showSaveButton && currentAction !== 'search'">
      <ProgressButton
        id="save-button"
        :action="save"
        :color="currentAction === 'acknowledgeSave' ? 'success' : 'primary'"
        :disabled="!!cohort.editMode || showCreateModal || !!currentAction"
        :in-progress="currentAction === 'save'"
      >
        <span v-if="currentAction === 'acknowledgeSave'">Saved</span>
        <span v-if="currentAction === 'save'">Saving</span>
        <span v-if="!currentAction && cohort.cohortId">Save Cohort</span>
        <span v-if="!currentAction && !cohort.cohortId">Save</span>
      </ProgressButton>
      <v-btn
        v-if="!currentAction && cohort.cohortId"
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
import {get} from 'lodash'
import {putFocusNextTick, setPageTitle} from '@/lib/utils'
import {ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {useRouter} from 'vue-router'

const cohort = useCohortStore()
const context = useContextStore()
const currentAction = ref(undefined)
const showCreateModal = ref(false)

const apply = () => {
  context.broadcast('cohort-apply-filters')
  currentAction.value = 'search'
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
    currentAction.value = null
  })
}

const cancelCreateModal = () => {
  context.alertScreenReader('Canceled')
  showCreateModal.value = false
}

const create = name => {
  showCreateModal.value = false
  currentAction.value = 'save'
  context.alertScreenReader('Creating cohort')
  return createCohort(cohort.domain, name, cohort.filters).then(async data => {
    if (data) {
      cohort.updateSession(data, cohort.filters, cohort.students, cohort.totalStudentCount)
      cohort.stashOriginalFilters()
      cohort.setModifiedSinceLastSearch(null)
      savedCohortCallback(`Cohort "${cohort.cohortName}" created`)
      setPageTitle(cohort.cohortName)
      await useRouter().push(`/cohort/${cohort.cohortId}`)
      window.history.replaceState({...window.history.state, ...{}}, null)
      currentAction.value = null
    }
  })
}

const resetToLastApply = () => {
  context.alertScreenReader('Resetting filters')
  resetFiltersToLastApply()
}

const resetToSaved = () => {
  currentAction.value = 'search'
  cohort.setCurrentPage(0)
  cohort.setModifiedSinceLastSearch(null)
  cohort.setEditMode('apply')
  loadCohort(cohort.cohortId, cohort.orderBy, cohort.termId).then(() => {
    cohort.setEditMode(null)
    context.alertScreenReader('Filters reset')
    currentAction.value = null
  })
}

const save = () => {
  if (cohort.cohortId) {
    context.alertScreenReader(`Saving changes to cohort ${cohort.cohortName}`)
    currentAction.value = 'save'
    saveCohort(cohort.cohortId, cohort.cohortName, cohort.filters).then(() => {
      cohort.setModifiedSinceLastSearch(null)
      savedCohortCallback(`Cohort "${cohort.cohortName}" saved`)
    })
  } else {
    showCreateModal.value = true
    context.alertScreenReader('Create cohort form is open')
  }
}

const savedCohortCallback = updateStatus => {
  context.alertScreenReader(updateStatus)
  currentAction.value = 'acknowledgeSave'
  setTimeout(() => (currentAction.value = null), 2000)
}
</script>
