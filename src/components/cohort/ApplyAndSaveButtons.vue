<template>
  <div class="my-2">
    <ProgressButton
      v-if="cohort.showApplyButton"
      id="unsaved-filter-apply"
      :action="apply"
      class="mr-2 text-uppercase"
      :disabled="!!cohort.editMode"
      :in-progress="currentAction === 'search'"
      text="Apply"
    />
    <v-btn
      v-if="cohort.showApplyButton"
      id="unsaved-filter-reset"
      class="text-uppercase"
      color="grey-darken-2"
      :disabled="!!cohort.editMode"
      text="Reset"
      variant="outlined"
      @click="resetToLastApply"
    />
    <div v-if="cohort.showSaveButton && currentAction !== 'search'">
      <ProgressButton
        id="save-cohort-button"
        :action="save"
        :color="currentAction === 'acknowledgeSave' ? 'success' : 'primary'"
        density="comfortable"
        :disabled="!!cohort.editMode || showCreateModal || !!currentAction"
        :in-progress="currentAction === 'save'"
        size="large"
      >
        <span v-if="currentAction === 'acknowledgeSave'">Saved</span>
        <span v-if="currentAction === 'save'">Saving</span>
        <span v-if="!currentAction && cohort.cohortId">Save Cohort</span>
        <span v-if="!currentAction && !cohort.cohortId">Save</span>
      </ProgressButton>
      <v-btn
        v-if="!currentAction && cohort.cohortId"
        id="reset-to-saved-cohort"
        class="ml-2"
        :disabled="!!cohort.editMode"
        text="Reset"
        variant="text"
        @click="resetToSaved"
      />
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
import router from '@/router'
import {alertScreenReader, putFocusNextTick, setPageTitle} from '@/lib/utils'
import {applyFilters, loadCohort, resetFiltersToLastApply} from '@/stores/cohort-edit-session/utils'
import {createCohort, saveCohort} from '@/api/cohort'
import {get} from 'lodash'
import {ref} from 'vue'
import {useCohortStore} from '@/stores/cohort-edit-session'
import {useContextStore} from '@/stores/context'

const cohort = useCohortStore()
const context = useContextStore()
const currentAction = ref(undefined)
const showCreateModal = ref(false)

const apply = () => {
  context.broadcast('cohort-apply-filters')
  currentAction.value = 'search'
  alertScreenReader('Searching for students')
  const orderBy = get(
    context.currentUser.preferences,
    cohort.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
  )
  const termId = get(context.currentUser.preferences, 'termId')
  applyFilters(orderBy, termId).then(() => {
    cohort.setModifiedSinceLastSearch(false)
    currentAction.value = null
    alertScreenReader(`Results include ${cohort.totalStudentCount} student${cohort.totalStudentCount === 1 ? '' : 's'}`)
    putFocusNextTick('save-cohort-button')
  })
}

const cancelCreateModal = () => {
  showCreateModal.value = false
}

const create = name => {
  showCreateModal.value = false
  currentAction.value = 'save'
  alertScreenReader('Creating cohort')
  return createCohort(cohort.domain, name, cohort.filters).then(async data => {
    if (data) {
      cohort.updateSession(data, cohort.filters, cohort.students, cohort.totalStudentCount)
      cohort.stashOriginalFilters()
      cohort.setModifiedSinceLastSearch(null)
      savedCohortCallback(`Cohort "${cohort.cohortName}" created`)
      setPageTitle(cohort.cohortName)
      await router.push(`/cohort/${cohort.cohortId}`)
      window.history.replaceState({...window.history.state, ...{}}, null)
      currentAction.value = null
    }
  })
}

const resetToLastApply = () => {
  alertScreenReader('Resetting filters')
  resetFiltersToLastApply().then(() => {
    alertScreenReader('Filters reset')
    putFocusNextTick('filter-select-primary-new')
  })
}

const resetToSaved = () => {
  currentAction.value = 'search'
  cohort.setCurrentPage(0)
  cohort.setModifiedSinceLastSearch(null)
  cohort.setEditMode('apply')
  loadCohort(cohort.cohortId, cohort.orderBy, cohort.termId).then(() => {
    cohort.setEditMode(null)
    currentAction.value = null
    alertScreenReader('Filters reset')
    putFocusNextTick('filter-select-primary-new')
  })
}

const save = () => {
  if (cohort.cohortId) {
    alertScreenReader(`Saving changes to cohort ${cohort.cohortName}`)
    currentAction.value = 'save'
    saveCohort(cohort.cohortId, cohort.cohortName, cohort.filters).then(() => {
      cohort.setModifiedSinceLastSearch(null)
      savedCohortCallback(`Cohort "${cohort.cohortName}" saved`)
    })
  } else {
    showCreateModal.value = true
  }
}

const savedCohortCallback = updateStatus => {
  currentAction.value = 'acknowledgeSave'
  alertScreenReader(updateStatus)
  putFocusNextTick('filter-select-primary-new')
  setTimeout(() => (currentAction.value = null), 2000)
}
</script>
